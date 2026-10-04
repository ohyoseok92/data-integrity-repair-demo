"""Deliberately broken baseline for the synthetic before/after demo."""

import sqlite3

from repair import Event


def setup(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE contacts (
            contact_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            email TEXT NOT NULL,
            email_verified INTEGER NOT NULL
        );
        CREATE TABLE events (account_id TEXT, event_id TEXT, contact_id TEXT);
        """
    )


def ingest(connection: sqlite3.Connection, event: Event) -> None:
    # Missing account condition, verified-value rule, and idempotency key.
    connection.execute(
        "UPDATE contacts SET email = ? WHERE contact_id = ?",
        (event.extracted_email or "", event.contact_id),
    )
    connection.execute(
        "INSERT INTO events VALUES (?, ?, ?)",
        (event.account_id, event.event_id, event.contact_id),
    )
    connection.commit()
