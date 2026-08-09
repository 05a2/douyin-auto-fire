from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


MessageType = Literal["text", "image", "douyin_sticker", "random"]


@dataclass(frozen=True)
class Message:
    type: MessageType
    content: str | None = None
    path: Path | None = None
    sticker: str | None = None
    choices: tuple["Message", ...] = ()


@dataclass(frozen=True)
class Target:
    name: str
    messages: tuple[Message, ...]


@dataclass(frozen=True)
class Sticker:
    name: str
    category: str | None = None
    accessible_name: str | None = None
    fallback_index: int | None = None


@dataclass(frozen=True)
class TaskConfig:
    task_id: str
    timezone: str
    targets: tuple[Target, ...]
    stickers: dict[str, Sticker]
    interval_min: float
    interval_max: float
    continue_on_error: bool


@dataclass(frozen=True)
class Settings:
    task_config_path: Path
    storage_state: str | None
    cookie: str | None
    headless: bool
    browser_path: str | None
    artifacts_dir: Path
    trace: bool


@dataclass(frozen=True)
class TargetResult:
    target: str
    status: Literal["success", "failed", "skipped", "duplicate", "unknown"]
    sent: int = 0
    error: str | None = None
