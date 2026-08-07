from importlib.metadata import version

from lessons._loader import load_exercise

exercise = load_exercise("16_packaging")
module_facts = exercise["module_facts"]
import_is_cached = exercise["import_is_cached"]
read_resource_text = exercise["read_resource_text"]
distribution_version = exercise["distribution_version"]


def test_module_facts_come_from_the_imported_module_and_spec() -> None:
    facts = module_facts("python_learning_lab.advanced.imports_lab")

    assert facts["__name__"] == "python_learning_lab.advanced.imports_lab"
    assert facts["__package__"] == "python_learning_lab.advanced.imports_lab"
    assert facts["__file__"].endswith("__init__.py")
    assert facts["spec_name"] == "python_learning_lab.advanced.imports_lab"
    assert facts["origin"] == facts["__file__"]


def test_repeated_import_reuses_the_cached_module_object() -> None:
    assert import_is_cached("json")


def test_package_resource_is_read_without_using_the_working_directory() -> None:
    text = read_resource_text(
        "python_learning_lab.advanced.imports_lab",
        "resources/welcome.txt",
    )

    assert "安装包内部" in text


def test_distribution_metadata_uses_the_distribution_name() -> None:
    assert distribution_version("python-learning-lab") == version("python-learning-lab")
