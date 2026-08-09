from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models import Message
from app.sender import send_message


@pytest.mark.asyncio
async def test_random_message_delegates_to_selected_choice(monkeypatch) -> None:
    editor = AsyncMock()
    page = MagicMock()
    message_items = MagicMock()
    message_items.count = AsyncMock(return_value=0)
    page.locator.return_value = message_items
    page.keyboard.insert_text = AsyncMock()
    page.keyboard.press = AsyncMock()
    page.wait_for_function = AsyncMock()
    editor.page = page
    chat = AsyncMock()
    chat.message_input.return_value = editor
    text = Message(type="text", content="你好")
    message = Message(type="random", choices=(text,))
    monkeypatch.setattr("app.sender.random.choice", lambda choices: choices[0])

    await send_message(page, chat, message, {})

    page.keyboard.insert_text.assert_awaited_once_with("你好")
    page.keyboard.press.assert_awaited_once_with("Enter")


@pytest.mark.asyncio
async def test_missing_sticker_mapping_fails() -> None:
    with pytest.raises(Exception, match="没有原生表情映射"):
        await send_message(AsyncMock(), AsyncMock(), Message(type="douyin_sticker", sticker="比心"), {})


@pytest.mark.asyncio
async def test_image_message_requires_path() -> None:
    with pytest.raises(Exception, match="缺少文件路径"):
        await send_message(AsyncMock(), AsyncMock(), Message(type="image", path=None), {})
