from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from app.config import ConfigError, parse_auth_json
from app.models import Settings
from app.selectors import CHAT_URL, LOGIN_MARKERS, LOGIN_REQUIRED_MARKERS, RISK_MARKERS


class AuthenticationError(RuntimeError):
    pass


class RiskControlError(RuntimeError):
    pass


@dataclass
class BrowserSession:
    page: Page
    context: BrowserContext


@asynccontextmanager
async def open_douyin(settings: Settings) -> AsyncIterator[BrowserSession]:
    playwright: Playwright | None = None
    browser: Browser | None = None
    context: BrowserContext | None = None
    try:
        playwright = await async_playwright().start()
        launch_args = {"headless": settings.headless}
        if settings.browser_path:
            launch_args["executable_path"] = settings.browser_path
        browser = await playwright.chromium.launch(**launch_args)

        context_args = {"viewport": {"width": 1440, "height": 1000}, "locale": "zh-CN"}
        if settings.storage_state:
            state = parse_auth_json(settings.storage_state, "DOUYIN_STORAGE_STATE")
            if not isinstance(state, dict):
                raise ConfigError("DOUYIN_STORAGE_STATE 必须是 JSON 对象")
            context_args["storage_state"] = state
        context = await browser.new_context(**context_args)
        if not settings.storage_state and settings.cookie:
            cookies = parse_auth_json(settings.cookie, "DOUYIN_COOKIE")
            if not isinstance(cookies, list):
                raise ConfigError("DOUYIN_COOKIE 必须是 Cookie 数组")
            await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto(CHAT_URL, wait_until="domcontentloaded", timeout=45_000)
        if settings.trace:
            await context.tracing.start(screenshots=True, snapshots=True, sources=False)
        yield BrowserSession(page=page, context=context)
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()


async def verify_login(page: Page, timeout_ms: int = 15_000) -> None:
    if await _any_visible(page, RISK_MARKERS, timeout_ms=2_000):
        raise RiskControlError("抖音要求进行安全验证，任务已停止")
    if await _any_visible(page, LOGIN_REQUIRED_MARKERS, timeout_ms=2_000):
        raise AuthenticationError("抖音登录状态已失效")
    if not await _any_visible(page, LOGIN_MARKERS, timeout_ms=timeout_ms):
        raise AuthenticationError("未检测到抖音私信页面，登录状态可能失效或页面结构已变化")


async def save_trace(session: BrowserSession, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    await session.context.tracing.stop(path=path)


async def _any_visible(page: Page, selectors: tuple[str, ...], timeout_ms: int) -> bool:
    per_selector = max(250, timeout_ms // max(1, len(selectors)))
    for selector in selectors:
        try:
            await page.locator(selector).first.wait_for(state="visible", timeout=per_selector)
            return True
        except Exception:
            continue
    return False
