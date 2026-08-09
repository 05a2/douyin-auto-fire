from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from app.models import Message, Sticker
from app.sender import send_message


@pytest.mark.asyncio
async def test_random_message_delegates_to_selected_choice(monkeypatch) -> None:
    editor = AsyncMock()
    editor.page.wait_for_timeout = AsyncMock()
    chat = AsyncMock()
    chat.message_input.return_value = editor
    page = AsyncMock()
    text = Message(type="text", content="你好")
    message = Message(type="random", choices=(text,))
    monkeypatch.setattr("app.sender.random.choice", lambda choices: choices[0])

    await send_message(page, chat, message, {})

    editor.fill.assert_awaited_once_with("你好")
    editor.press.assert_awaited_once_with("Enter")


@pytest.mark.asyncio
async def test_missing_sticker_mapping_fails() -> None:
    with pytest.raises(Exception, match="没有原生表情映射"):
        await send_message(AsyncMock(), AsyncMock(), Message(type="douyin_sticker", sticker="比心"), {})


@pytest.mark.asyncio
async def test_image_message_requires_path() -> None:
    with pytest.raises(Exception, match="缺少文件路径"):
        await send_message(AsyncMock(), AsyncMock(), Message(type="image", path=None), {})
