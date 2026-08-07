from __future__ import annotations

import re
import tomllib
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "course.toml"
LESSONS = ROOT / "lessons"
REVIEWS = ROOT / "reviews"
ALLOWED_KINDS = {"guided", "workshop", "test-workshop", "experiment", "capstone"}
COURSE_MARKER = re.compile(r"<!--\s*course-chapter:\s*(\d+)\s*-->")
REVIEW_MARKER = re.compile(r"<!--\s*review-chapter:\s*(\d+)\s*-->")


def load_course() -> dict[str, object]:
    return tomllib.loads(MANIFEST.read_text(encoding="utf-8"))


def chapters() -> list[dict[str, object]]:
    course = load_course()
    return list(course["chapters"])  # type: ignore[arg-type]


def test_manifest_covers_every_chapter_once_and_in_order() -> None:
    numbers = [chapter["number"] for chapter in chapters()]

    assert numbers == list(range(1, 27))


def test_progress_points_to_the_first_unfinished_chapter() -> None:
    course = load_course()
    progress = course["progress"]
    assert isinstance(progress, dict)

    completed_through = progress["completed_through"]
    next_chapter = progress["next_chapter"]

    assert isinstance(completed_through, int)
    assert next_chapter == completed_through + 1
    assert next_chapter in {chapter["number"] for chapter in chapters()}
    assert ROOT / str(progress["reviews"]) == REVIEWS

    review_index = (REVIEWS / "README.md").read_text(encoding="utf-8")
    assert f"下一课是第 {next_chapter} 章" in review_index


def test_every_chapter_uses_one_self_contained_lesson_directory() -> None:
    expected_directories: set[str] = set()

    for chapter in chapters():
        number = int(str(chapter["number"]))
        courseware = ROOT / str(chapter["courseware"])
        lesson_directory = courseware.parent
        expected_directories.add(lesson_directory.name)

        assert courseware.name == "lesson.md"
        assert lesson_directory.parent == LESSONS
        assert lesson_directory.name.startswith(f"{number:02d}_")

        for field in ("courseware", "example", "exercise", "test"):
            path = ROOT / str(chapter[field])
            assert path.exists(), f"第 {number} 章缺少 {field}: {path}"

        example = (ROOT / str(chapter["example"])).resolve()
        assert example.is_relative_to(LESSONS.resolve()), (
            f"第 {number} 章的示例代码必须位于 lessons/: {example}"
        )

        for field in ("exercise", "test"):
            path = (ROOT / str(chapter[field])).resolve()
            assert path.is_relative_to(lesson_directory.resolve()), (
                f"第 {number} 章的 {field} 必须位于 {lesson_directory.relative_to(ROOT)}"
            )

        solution = chapter.get("solution")
        if solution is not None:
            path = (ROOT / str(solution)).resolve()
            assert path.exists(), f"第 {number} 章缺少 solution: {path}"
            assert path.is_relative_to(LESSONS.resolve()), (
                f"第 {number} 章的参考实现必须位于 lessons/: {path}"
            )

    actual_directories = {
        path.name for path in LESSONS.iterdir() if path.is_dir() and not path.name.startswith("_")
    }
    assert actual_directories == expected_directories


def test_every_chapter_has_one_substantive_courseware_file() -> None:
    """每章必须有独立课件，不能重新退化为共享提纲或练习文件。"""

    marker_locations: dict[int, list[Path]] = {}
    for markdown in LESSONS.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for number in COURSE_MARKER.findall(text):
            marker_locations.setdefault(int(number), []).append(markdown)

    for chapter in chapters():
        number = int(str(chapter["number"]))
        courseware = ROOT / str(chapter["courseware"])
        locations = marker_locations.get(number, [])

        assert locations == [courseware], (
            f"第 {number} 章必须只在自己的 lesson.md 中出现课程标记；实际="
            f"{[path.relative_to(ROOT) for path in locations]}"
        )

        text = courseware.read_text(encoding="utf-8")
        compact_text = re.sub(r"\s+", "", text)
        assert len(compact_text) >= 600, (
            f"第 {number} 章课件正文过短，不能只提供目录或提纲：{courseware.relative_to(ROOT)}"
        )
        assert re.search(rf"^# 第 {number} 章[：:]", text, re.MULTILINE)
        assert "```" in text, f"第 {number} 章课件缺少代码或文本示例"


def test_reviews_exist_only_for_completed_chapters() -> None:
    course = load_course()
    progress = course["progress"]
    assert isinstance(progress, dict)
    completed_through = int(str(progress["completed_through"]))

    expected_reviews: set[Path] = set()
    for chapter in chapters():
        number = int(str(chapter["number"]))
        review_value = chapter.get("review")
        if number <= completed_through:
            assert review_value is not None, f"已完成的第 {number} 章缺少 review"
            review = ROOT / str(review_value)
            expected_reviews.add(review)
            assert review.parent == REVIEWS
            assert review.exists()

            text = review.read_text(encoding="utf-8")
            assert REVIEW_MARKER.findall(text) == [str(number)]
            assert len(re.sub(r"\s+", "", text)) >= 300
            assert "快速自测" in text
        else:
            assert review_value is None, f"未完成的第 {number} 章不应提前生成 review"

    actual_reviews = set(REVIEWS.glob("[0-9][0-9]_*.md"))
    assert actual_reviews == expected_reviews


def test_every_chapter_declares_an_explicit_completion_contract() -> None:
    for chapter in chapters():
        kind = chapter["kind"]
        assert kind in ALLOWED_KINDS

        command = str(chapter["command"])
        assert str(chapter["test"]) in command

        if kind == "capstone":
            assert "solution" not in chapter
            assert "不提供" in str(chapter["solution_policy"])
        else:
            assert "solution" in chapter


def test_completed_python_exercises_do_not_contain_placeholders() -> None:
    course = load_course()
    progress = course["progress"]
    assert isinstance(progress, dict)
    completed_through = int(str(progress["completed_through"]))

    unresolved: list[str] = []
    for chapter in chapters():
        number = int(str(chapter["number"]))
        exercise = ROOT / str(chapter["exercise"])
        if number > completed_through or exercise.suffix != ".py":
            continue
        text = exercise.read_text(encoding="utf-8")
        if "TODO" in text or "NotImplementedError" in text:
            unresolved.append(str(exercise.relative_to(ROOT)))

    assert not unresolved, "已完成章节仍含占位实现：\n" + "\n".join(unresolved)


def test_public_indexes_and_agent_rules_describe_the_new_layout() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    lessons_index = (LESSONS / "README.md").read_text(encoding="utf-8")
    agent_rules = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "course.toml" in readme
    assert "lessons/" in readme
    assert "reviews/" in readme
    assert all(f"| {number} |" in lessons_index for number in range(1, 27))
    assert "[progress].next_chapter" in agent_rules
    assert "lesson.md" in agent_rules


def test_course_code_is_not_scattered_across_legacy_directories() -> None:
    for directory in ("docs", "examples", "exercises", "learning_tests", "solutions", "src"):
        assert not (ROOT / directory).exists(), f"课程内容不应散落到根目录：{directory}/"


def test_source_distribution_includes_the_complete_course() -> None:
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "include AGENTS.md" in manifest
    assert "include course.toml" in manifest
    for directory in ("lessons", "reviews"):
        assert f"recursive-include {directory} " in manifest
    for removed in ("docs", "examples", "exercises", "learning_tests", "solutions", "src"):
        assert f"recursive-include {removed} " not in manifest


def test_internal_markdown_links_point_to_existing_files() -> None:
    markdown_files = [ROOT / "README.md", ROOT / "AGENTS.md"]
    for directory in ("lessons", "reviews"):
        markdown_files.extend((ROOT / directory).rglob("*.md"))

    missing: list[str] = []
    for markdown in markdown_files:
        text = markdown.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]*]\(([^)]+)\)", text):
            if target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            path_text = unquote(target.split("#", maxsplit=1)[0])
            if path_text and not (markdown.parent / path_text).exists():
                missing.append(f"{markdown.relative_to(ROOT)} -> {target}")

    assert not missing, "无效的本地 Markdown 链接：\n" + "\n".join(missing)
