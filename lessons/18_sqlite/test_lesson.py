import sqlite3
from pathlib import Path

import pytest

from lessons._loader import load_exercise

exercise = load_exercise("18_sqlite")
Note = exercise["Note"]
SQLiteNoteRepository = exercise["SQLiteNoteRepository"]


@pytest.fixture
def repository():
    connection = sqlite3.connect(":memory:")
    value = SQLiteNoteRepository(connection)
    value.initialize()
    try:
        yield value
    finally:
        connection.close()


def test_repository_round_trip_and_update(repository) -> None:
    repository.save(Note("note-1", "first"))
    assert repository.get("note-1") == Note("note-1", "first")

    repository.save(Note("note-1", "updated"))
    assert repository.get("note-1") == Note("note-1", "updated")
    assert repository.get("missing") is None


def test_parameter_binding_handles_sql_characters_as_plain_data(repository) -> None:
    text = "Robert'); DROP TABLE notes;--"
    repository.save(Note("note-2", text))
    assert repository.get("note-2") == Note("note-2", text)


def test_transaction_rolls_back_repository_writes_on_error(repository) -> None:
    with pytest.raises(RuntimeError), repository.transaction():
        repository.save(Note("temp-1", "first"))
        repository.save(Note("temp-2", "second"))
        raise RuntimeError("rollback")

    assert repository.get("temp-1") is None
    assert repository.get("temp-2") is None


def test_file_database_persists_after_close_and_reopen(tmp_path: Path) -> None:
    path = tmp_path / "notes.sqlite3"
    first_connection = sqlite3.connect(path)
    first = SQLiteNoteRepository(first_connection)
    first.initialize()
    first.save(Note("note-1", "persistent"))
    first_connection.close()

    second_connection = sqlite3.connect(path)
    second = SQLiteNoteRepository(second_connection)
    try:
        assert second.get("note-1") == Note("note-1", "persistent")
    finally:
        second_connection.close()
