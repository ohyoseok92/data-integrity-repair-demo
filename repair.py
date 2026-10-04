"""A bounded, transactional repair for one synthetic contact-ingest path."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    account_id: str
    event_id: str
    contact_id: str
    extracted_email: str | None


def setup(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE contacts (
            contact_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            email TEXT NOT NULL,
            email_verified INTEGER NOT NULL CHECK (email_verified IN (0, 1))
        );
        CREATE TABLE events (
            account_id TEXT NOT NULL,
            event_id TEXT NOT NULL,
            contact_id TEXT NOT NULL,
            PRIMARY KEY (account_id, event_id)
        );
        """
    )


def ingest(connection: sqlite3.Connection, event: Event) -> str:
    """Return 'applied' or 'duplicate'; raise ValueError for a bad boundary."""
    if not event.account_id or not event.event_id or not event.contact_id:
        raise ValueError("account_id, event_id and contact_id are required")

    # BEGIN IMMEDIATE serializes concurrent writers before the lookup. The
    # unique event key still protects against retries from another process.
    connection.execute("BEGIN IMMEDIATE")
    try:
        if connection.execute(
            "SELECT 1 FROM events WHERE account_id = ? AND event_id = ?",
            (event.account_id, event.event_id),
        ).fetchone():
            connection.rollback()
            return "duplicate"

        contact = connection.execute(
            "SELECT email_verified FROM contacts WHERE account_id = ? AND contact_id = ?",
            (event.account_id, event.contact_id),
        ).fetchone()
        if contact is None:
            raise ValueError("contact does not belong to account")

        email = (event.extracted_email or "").strip()
        if email and not contact[0]:
            connection.execute(
                "UPDATE contacts SET email = ? WHERE account_id = ? AND contact_id = ?",
                (email, event.account_id, event.contact_id),
            )

        connection.execute(
            "INSERT INTO events (account_id, event_id, contact_id) VALUES (?, ?, ?)",
            (event.account_id, event.event_id, event.contact_id),
        )
        connection.commit()
        return "applied"
    except Exception:
        connection.rollback()
        raise
