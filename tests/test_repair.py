import sqlite3
import unittest

import repair


class IngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        repair.setup(self.connection)
        self.connection.executemany(
            "INSERT INTO contacts VALUES (?, ?, ?, ?)",
            [
                ("c-1", "shop-a", "owner@example.test", 1),
                ("c-2", "shop-a", "old@example.test", 0),
                ("c-3", "shop-b", "other@example.test", 0),
            ],
        )
        self.connection.commit()

    def tearDown(self) -> None:
        self.connection.close()

    def email(self, contact_id: str) -> str:
        return self.connection.execute(
            "SELECT email FROM contacts WHERE contact_id = ?", (contact_id,)
        ).fetchone()[0]

    def count(self) -> int:
        return self.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    def test_retry_creates_one_event(self) -> None:
        event = repair.Event("shop-a", "e-1", "c-2", "new@example.test")
        self.assertEqual(repair.ingest(self.connection, event), "applied")
        self.assertEqual(repair.ingest(self.connection, event), "duplicate")
        self.assertEqual(self.count(), 1)
        self.assertEqual(self.email("c-2"), "new@example.test")

    def test_blank_does_not_overwrite_verified_email(self) -> None:
        repair.ingest(self.connection, repair.Event("shop-a", "e-2", "c-1", "  "))
        self.assertEqual(self.email("c-1"), "owner@example.test")

    def test_nonblank_does_not_overwrite_verified_email(self) -> None:
        repair.ingest(self.connection, repair.Event("shop-a", "e-3", "c-1", "other@example.test"))
        self.assertEqual(self.email("c-1"), "owner@example.test")

    def test_cross_account_contact_is_rejected_atomically(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not belong"):
            repair.ingest(self.connection, repair.Event("shop-a", "e-4", "c-3", "wrong@example.test"))
        self.assertEqual(self.count(), 0)
        self.assertEqual(self.email("c-3"), "other@example.test")

    def test_missing_identifier_does_not_write(self) -> None:
        with self.assertRaisesRegex(ValueError, "required"):
            repair.ingest(self.connection, repair.Event("", "e-5", "c-2", "new@example.test"))
        self.assertEqual(self.count(), 0)
        self.assertEqual(self.email("c-2"), "old@example.test")


if __name__ == "__main__":
    unittest.main()
