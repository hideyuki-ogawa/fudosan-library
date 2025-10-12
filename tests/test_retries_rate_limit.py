from __future__ import annotations

import httpx
import pytest
import respx


@respx.mock
def test_retries_on_rate_limit(monkeypatch: pytest.MonkeyPatch, client) -> None:
    sleeps: list[float] = []

    def _record_sleep(duration: float) -> None:
        sleeps.append(duration)

    monkeypatch.setattr("fudosan_library.client.time.sleep", _record_sleep)

    respx.get("https://api.test/XIT001").mock(
        side_effect=[
            httpx.Response(status_code=429, json={"code": "XIT001", "message": "too many"}),
            httpx.Response(
                status_code=200,
                json={
                    "code": "XIT001",
                    "status": "OK",
                    "data": [
                        {
                            "TradePrice": 1000000,
                            "MunicipalityCode": "13101",
                            "Prefecture_ja": "東京都",
                            "Area": 42.0,
                            "PriceClassification": "01",
                        }
                    ],
                },
            ),
        ]
    )

    records = client.get_trade_prices(
        year=2023,
        price_classification="01",
        area="13",
        city="13101",
    )

    assert len(records) == 1
    assert sleeps, "expected backoff sleep to be recorded"
    assert sleeps[0] > 0.0
