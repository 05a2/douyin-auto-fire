from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models import Message
from app.douyin import PageOperationError
from app.sender import LATEST_OUTGOING_MESSAGE, _confirm_sticker_sent, _sticker_resource_key, send_message


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


@pytest.mark.asyncio
async def test_sticker_confirmation_waits_for_new_matching_outgoing_message() -> None:
    page = MagicMock()
    page.wait_for_function = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    latest_group = MagicMock()
    latest = MagicMock()
    latest_group.first = latest
    marker_group = MagicMock()
    marker = MagicMock()
    marker_group.first = marker
    marker.count = AsyncMock(return_value=0)
    latest.locator.return_value = marker_group
    anchors = MagicMock()
    anchors.evaluate_all = AsyncMock()
    page.locator.side_effect = lambda selector: latest_group if selector == LATEST_OUTGOING_MESSAGE else anchors

    await _confirm_sticker_sent(page, ("anchor", "old-content"), "比心", "resource-key")

    assert page.wait_for_function.await_args.kwargs["arg"] == [
        LATEST_OUTGOING_MESSAGE,
        "anchor",
        "old-content",
        "resource-key",
    ]
    page.wait_for_timeout.assert_awaited_once_with(3_000)


@pytest.mark.asyncio
async def test_sticker_confirmation_reports_page_send_failure() -> None:
    page = MagicMock()
    page.wait_for_function = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    latest_group = MagicMock()
    latest = MagicMock()
    latest_group.first = latest
    marker_group = MagicMock()
    marker = MagicMock()
    marker_group.first = marker
    marker.count = AsyncMock(return_value=1)
    marker.is_visible = AsyncMock(return_value=True)
    latest.locator.return_value = marker_group
    anchors = MagicMock()
    anchors.evaluate_all = AsyncMock()
    page.locator.side_effect = lambda selector: latest_group if selector == LATEST_OUTGOING_MESSAGE else anchors

    with pytest.raises(PageOperationError, match="发送失败"):
        await _confirm_sticker_sent(page, ("anchor", "old-content"), "比心")


@pytest.mark.asyncio
async def test_sticker_confirmation_reports_missing_new_message() -> None:
    page = MagicMock()
    page.wait_for_function = AsyncMock(side_effect=TimeoutError)
    anchors = MagicMock()
    anchors.evaluate_all = AsyncMock()
    page.locator.return_value = anchors

    with pytest.raises(PageOperationError, match="没有检测到新的已发送消息"):
        await _confirm_sticker_sent(page, ("anchor", "old-content"), "比心")


@pytest.mark.asyncio
async def test_sticker_resource_key_ignores_signed_query_string() -> None:
    item = MagicMock()
    item.get_attribute = AsyncMock(
        return_value="https://p26-sign.douyinpic.com/obj/im-resource/sticker-key?x-signature=temporary"
    )

    assert await _sticker_resource_key(item) == "sticker-key"
