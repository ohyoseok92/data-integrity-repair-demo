"""Print the before/after behavior on invented records."""

import sqlite3

import repair
import unsafe


def run(module: object) -> tuple[str, int, str]:
    connection = sqlite3.connect(":memory:")
    module.setup(connection)
    connection.execute(
        "INSERT INTO contacts VALUES ('c-1', 'shop-a', 'owner@example.test', 1)"
    )
    connection.commit()
    event = repair.Event("shop-a", "delivery-42", "c-1", "")
    module.ingest(connection, event)
    module.ingest(connection, event)
    email = connection.execute(
        "SELECT email FROM contacts WHERE contact_id = 'c-1'"
    ).fetchone()[0]
    count = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    cross_account = "accepted"
    try:
        module.ingest(connection, repair.Event("shop-b", "delivery-43", "c-1", "wrong@example.test"))
    except ValueError:
        cross_account = "rejected"
    return email, count, cross_account


if __name__ == "__main__":
    print("baseline (email, event count, cross-account event):", run(unsafe))
    print("repaired (email, event count, cross-account event):", run(repair))
