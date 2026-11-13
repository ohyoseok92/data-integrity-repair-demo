# Data integrity repair: one webhook-to-contact path

## 한국어 안내

실제 고객 사례가 아닌 가상 데이터 예제입니다. 웹훅 재시도로 중복 기록이 생기거나, 빈 이메일이 검증된 값을 덮어쓰거나, 다른 계정의 연락처가 바뀌는 오류를 재현합니다. `repair.py`의 수정과 테스트 5개로 결과를 확인할 수 있습니다.

실제 시스템의 오류 한 건은 비식별 입력과 기대 결과를 받아 작업 범위를 먼저 확인합니다. 국내 의뢰는 [크몽(129,000원)](https://kmong.com/gig/832484), 해외 의뢰는 [Payhip(USD 99)](https://payhip.com/b/yUF4Q)에서 문의할 수 있습니다. 시스템을 확인하기 전에는 같은 수정이나 6시간 내 해결을 약속하지 않습니다.

## English overview

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

If you have one reproducible Python/API data error, [describe it before paying](https://payhip.com/b/yUF4Q).
