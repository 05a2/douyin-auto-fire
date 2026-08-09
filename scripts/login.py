from __future__ import annotations

import asyncio

from playwright.async_api import async_playwright

from app.browser import verify_login


async def login() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(locale="zh-CN")
        page = await context.new_page()
        await page.goto("https://www.douyin.com/im", wait_until="domcontentloaded")
        print("请在浏览器中完成登录并进入私信页面，然后回到终端按 Enter。")
        await asyncio.to_thread(input)
        await verify_login(page)
        await context.storage_state(path="storage-state.json.tmp")
        await browser.close()
        from pathlib import Path

        Path("storage-state.json.tmp").replace("storage-state.json")
        print("登录状态已保存到 storage-state.json")


if __name__ == "__main__":
    asyncio.run(login())
