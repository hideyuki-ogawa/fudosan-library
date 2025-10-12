from __future__ import annotations

import pytest

from fudosan_library.client import FudosanClient


@pytest.fixture()
def client() -> FudosanClient:
    return FudosanClient(api_key="dummy-key", base_url="https://api.test")
