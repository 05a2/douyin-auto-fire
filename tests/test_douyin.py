from unittest.mock import AsyncMock, MagicMock

import pytest

from app.douyin import DouyinChat


@pytest.mark.asyncio
async def test_search_result_accepts_visible_partial_text() -> None:
    page = MagicMock()
    rows = MagicMock()
    page.locator.return_value.filter.return_value = rows
    rows.count = AsyncMock(return_value=0)
    exact = MagicMock()
    partial = MagicMock()
    page.get_by_text.side_effect = [exact, partial]
    exact.count = AsyncMock(return_value=0)
    partial.count = AsyncMock(return_value=1)
    candidate = MagicMock()
    candidate.is_visible = AsyncMock(return_value=True)
    partial.nth.return_value = candidate

    result = await DouyinChat(page)._search_result("好友")

    assert result is candidate


@pytest.mark.asyncio
async def test_search_result_ignores_hidden_exact_match() -> None:
    page = MagicMock()
    rows = MagicMock()
    page.locator.return_value.filter.return_value = rows
    rows.count = AsyncMock(return_value=0)
    exact = MagicMock()
    partial = MagicMock()
    page.get_by_text.side_effect = [exact, partial]
    exact.count = AsyncMock(return_value=1)
    hidden = MagicMock()
    hidden.is_visible = AsyncMock(return_value=False)
    exact.nth.return_value = hidden
    partial.count = AsyncMock(return_value=1)
    visible = MagicMock()
    visible.is_visible = AsyncMock(return_value=True)
    partial.nth.return_value = visible

    result = await DouyinChat(page)._search_result("好友")

    assert result is visible
