import pytest

from app.browser import _normalize_cookies
from app.config import ConfigError


def test_normalizes_cookie_editor_export() -> None:
    cookies = [
        {
            "domain": ".douyin.com",
            "expirationDate": 1800175766.5,
            "hostOnly": False,
            "httpOnly": True,
            "name": "UIFID",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "token",
        }
    ]

    assert _normalize_cookies(cookies) == [
        {
            "name": "UIFID",
            "value": "token",
            "domain": ".douyin.com",
            "path": "/",
            "expires": 1800175766.5,
            "httpOnly": True,
            "secure": True,
            "sameSite": "None",
        }
    ]


def test_session_cookie_ignores_expiration_date() -> None:
    cookies = [
        {
            "domain": ".douyin.com",
            "expirationDate": 1800175766.5,
            "name": "sessionid",
            "session": True,
            "value": "token",
        }
    ]

    assert _normalize_cookies(cookies)[0]["expires"] == -1


def test_ignores_cookie_editor_empty_name_artifact() -> None:
    cookies = [
        {"domain": "www.douyin.com", "name": "", "value": "douyin.com"},
        {"domain": ".douyin.com", "name": "sessionid", "value": "token"},
    ]

    assert [cookie["name"] for cookie in _normalize_cookies(cookies)] == ["sessionid"]


def test_rejects_cookie_without_domain() -> None:
    with pytest.raises(ConfigError, match="缺少有效的 domain"):
        _normalize_cookies([{"name": "UIFID", "value": "token"}])
