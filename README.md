# Data integrity repair: one webhook-to-contact path

This is a synthetic portfolio example, not a client system or a paid engagement.
It demonstrates three failures that can survive a successful HTTP response:

| Failure | Unsafe result | Repaired invariant |
| --- | --- | --- |
| The sender retries the same event | Two event records | One `(account_id, event_id)` record |
| Extraction returns a blank email | A verified email becomes blank | A verified email stays unchanged |
| A contact ID belongs to another account | The other account's contact changes | Reject the event without a write |

`unsafe.py` is a deliberately broken baseline. `repair.py` makes the account
lookup and event insert one SQLite transaction, treats an event key as an
idempotency key, and preserves verified values. The example uses only Python's
standard library and invented names and addresses.

Run it:

```sh
python -m unittest discover -s tests -v
python demo.py
```

The tests cover retries, blank overwrites, cross-account writes, and a valid
update. `demo.py` prints the unsafe and repaired outcomes side by side.

In a real job, I would first agree on the failing input, the expected record,
and the account boundary. This sample does not claim that the same patch applies
to an unseen production database or that a broader migration fits six hours.
