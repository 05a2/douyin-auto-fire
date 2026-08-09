from __future__ import annotations

import random

from playwright.async_api import Page

from app.douyin import DouyinChat, PageOperationError, first_visible
from app.models import Message, Sticker
from app.selectors import IMAGE_INPUTS, STICKER_BUTTONS, STICKER_PANELS


async def send_message(page: Page, chat: DouyinChat, message: Message, stickers: dict[str, Sticker]) -> None:
    if message.type == "random":
        await send_message(page, chat, random.choice(message.choices), stickers)
        return
    if message.type == "text":
        await send_text(chat, message.content or "")
        return
    if message.type == "image":
        if message.path is None:
            raise PageOperationError("图片消息缺少文件路径")
        await send_image(page, message.path.as_posix())
        return
    if message.type == "douyin_sticker":
        sticker = stickers.get(message.sticker or "")
        if sticker is None:
            raise PageOperationError(f"没有原生表情映射: {message.sticker}")
        await send_douyin_sticker(page, sticker)
        return
    raise PageOperationError(f"不支持的消息类型: {message.type}")


async def send_text(chat: DouyinChat, content: str) -> None:
    editor = await chat.message_input()
    page = editor.page
    messages = page.locator('[data-e2e="msg-item-content"]')
    before = await messages.count()
    await editor.click()
    await page.keyboard.insert_text(content)
    await page.keyboard.press("Enter")
    try:
        await page.wait_for_function(
            """([selector, count, text]) => {
                const items = [...document.querySelectorAll(selector)];
                return items.length > count && items.some(item => item.textContent.includes(text));
            }""",
            arg=['[data-e2e="msg-item-content"]', before, content],
            timeout=10_000,
        )
    except Exception as exc:
        raise PageOperationError("文字消息已触发发送，但无法确认是否发送成功；为避免重复不会自动重试") from exc


async def send_image(page: Page, image_path: str) -> None:
    file_input = None
    for selector in IMAGE_INPUTS:
        candidate = page.locator(selector).first
        if await candidate.count():
            file_input = candidate
            break
    if file_input is None:
        raise PageOperationError("找不到图片上传控件")
    await file_input.set_input_files(image_path)
    await page.wait_for_timeout(1_500)

    send_button = page.get_by_role("button", name="发送", exact=True)
    if await send_button.count() and await send_button.first.is_visible():
        await send_button.first.click()
    else:
        await page.keyboard.press("Enter")
    await page.wait_for_timeout(1_000)


async def send_douyin_sticker(page: Page, sticker: Sticker) -> None:
    message_boxes = page.locator('.messageMessageBoxmessageBox')
    before = await message_boxes.count()
    button = await first_visible(page, STICKER_BUTTONS)
    await button.click(force=True)
    panel = await first_visible(page, STICKER_PANELS)

    if sticker.category:
        category = panel.get_by_text(sticker.category, exact=True)
        if await category.count() and await category.first.is_visible():
            await category.first.click()

    name = sticker.accessible_name or sticker.name
    item = panel.locator('.emojiEmojiItememojiItem').filter(has_text=name)
    for index in range(await item.count()):
        candidate = item.nth(index)
        description = candidate.locator('.emojiEmojiItememojiItemDesc')
        if await description.count() and (await description.first.inner_text()).strip() == name:
            await candidate.click(force=True)
            await _confirm_sticker_sent(page, message_boxes, before, name)
            return

    candidates = (
        panel.get_by_role("img", name=name, exact=True),
        panel.get_by_role("button", name=name, exact=True),
        panel.locator(f'[aria-label="{_css_escape(name)}"]'),
        panel.locator(f'[title="{_css_escape(name)}"]'),
        panel.locator(f'[alt="{_css_escape(name)}"]'),
    )
    for candidate in candidates:
        if await candidate.count() and await candidate.first.is_visible():
            await candidate.first.click()
            await _confirm_sticker_sent(page, message_boxes, before, name)
            return

    if sticker.fallback_index is not None:
        items = panel.locator('[role="button"], img, [aria-label], [title]')
        if await items.count() > sticker.fallback_index:
            await items.nth(sticker.fallback_index).click()
            await _confirm_sticker_sent(page, message_boxes, before, name)
            return
    raise PageOperationError(f"在抖音表情面板中找不到原生表情: {sticker.name}")


def _css_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


async def _confirm_sticker_sent(page: Page, message_boxes, before: int, name: str) -> None:
    try:
        await page.wait_for_function(
            """([selector, count]) => document.querySelectorAll(selector).length > count""",
            arg=['.messageMessageBoxmessageBox', before],
            timeout=10_000,
        )
    except Exception as exc:
        raise PageOperationError(f"原生表情“{name}”已点击，但无法确认是否发送成功") from exc
