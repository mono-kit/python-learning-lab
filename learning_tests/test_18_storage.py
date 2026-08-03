import sqlite3

import pytest

from learning_tests.loader import load_exercise


exercise = load_exercise("18_storage.py")
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


def test_transaction_rolls_back_on_error(repository) -> None:
    with pytest.raises(RuntimeError), repository.transaction() as connection:
        connection.execute("INSERT INTO notes (id, text) VALUES (?, ?)", ("temp", "x"))
        raise RuntimeError("rollback")
    assert repository.get("temp") is None
