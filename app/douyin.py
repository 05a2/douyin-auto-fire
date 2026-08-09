from __future__ import annotations

from playwright.async_api import Locator, Page

from app.selectors import MESSAGE_INPUTS, SEARCH_INPUTS


class PageOperationError(RuntimeError):
    pass


class DouyinChat:
    def __init__(self, page: Page, timeout_ms: int = 15_000) -> None:
        self.page = page
        self.timeout_ms = timeout_ms

    async def open_target(self, name: str) -> None:
        search = await first_visible(self.page, SEARCH_INPUTS, self.timeout_ms)
        await search.click()
        await search.fill("")
        await search.fill(name)

        result = self.page.get_by_text(name, exact=True)
        try:
            await result.first.wait_for(state="visible", timeout=self.timeout_ms)
        except Exception as exc:
            raise PageOperationError(f"搜索不到好友: {name}") from exc

        matches = await result.count()
        if matches > 1:
            raise PageOperationError(f"好友名称存在多个精确匹配，请配置唯一名称: {name}")
        await result.first.click()
        await self.message_input()

        # Confirm the target remains visible after navigation instead of trusting search order.
        try:
            await self.page.get_by_text(name, exact=True).first.wait_for(state="visible", timeout=5_000)
        except Exception as exc:
            raise PageOperationError(f"无法确认当前聊天对象: {name}") from exc

    async def message_input(self) -> Locator:
        return await first_visible(self.page, MESSAGE_INPUTS, self.timeout_ms)


async def first_visible(page: Page, selectors: tuple[str, ...], timeout_ms: int = 15_000) -> Locator:
    per_selector = max(500, timeout_ms // max(1, len(selectors)))
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            await locator.wait_for(state="visible", timeout=per_selector)
            return locator
        except Exception:
            continue
    raise PageOperationError(f"找不到页面元素，已尝试: {', '.join(selectors)}")
