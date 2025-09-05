import asyncio
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from pyrogram.enums import ChatType
except Exception:
    ChatType = None  # fallback

def normalize_text(s: Optional[str]) -> str:
    if s is None:
        return ""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\u00A0", " ")
    s = "\n".join(line.rstrip() for line in s.split("\n"))
    return s

def to_utc_iso(dt: Optional[datetime]) -> str:
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    iso = dt.isoformat()
    if iso.endswith("+00:00"):
        iso = iso[:-6] + "Z"
    return iso

def parse_iso_datetime(value: str, is_end: bool = False) -> datetime:
    s = value.strip().upper().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        dt = datetime.fromisoformat(s + "T00:00:00")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    if "T" not in s and is_end:
        dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    return dt

def parse_date_range(range_str: str):
    if not range_str:
        return (None, None)
    s = range_str.strip()
    if ".." in s:
        left, right = s.split("..", 1)
        start = parse_iso_datetime(left, is_end=False) if left.strip() else None
        end = parse_iso_datetime(right, is_end=True) if right.strip() else None
    else:
        start = parse_iso_datetime(s, is_end=False)
        end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end

def read_last_saved_id(path: Path) -> int:
    if not path.exists():
        return 0
    last_id = 0
    chunk = 8192
    pattern = re.compile(rb"\nid:\s*(\d+)\s*\n")
    with path.open("rb") as f:
        f.seek(0, os.SEEK_END)
        pos = f.tell()
        buf = b""
        while pos > 0:
            read = min(chunk, pos)
            pos -= read
            f.seek(pos)
            data = f.read(read)
            buf = data + buf
            for m in re.finditer(pattern, buf):
                last_id = int(m.group(1))
            if last_id:
                break
    return last_id or 0

def author_string(msg) -> str:
    try:
        if getattr(msg, "author_signature", None):
            return msg.author_signature
        if getattr(msg, "forward_sender_name", None):
            return msg.forward_sender_name
        fwd_chat = getattr(msg, "forward_from_chat", None)
        if fwd_chat is not None:
            return getattr(fwd_chat, "title", None) or getattr(fwd_chat, "username", None) or "N/A"
        fwd_user = getattr(msg, "forward_from", None)
        if fwd_user is not None:
            if getattr(fwd_user, "username", None):
                return f"@{fwd_user.username}"
            name = " ".join(x for x in [getattr(fwd_user, "first_name", None), getattr(fwd_user, "last_name", None)] if x)
            return name or "N/A"
        chat = getattr(msg, "chat", None)
        if chat is not None:
            ctype = getattr(chat, "type", None)
            is_channel = False
            if ChatType is not None:
                is_channel = (ctype == ChatType.CHANNEL)
            else:
                is_channel = (str(ctype).lower() == "channel")
            if is_channel:
                return getattr(chat, "title", None) or "N/A"
        from_user = getattr(msg, "from_user", None)
        if from_user is not None:
            if getattr(from_user, "username", None):
                return f"@{from_user.username}"
            name = " ".join(x for x in [getattr(from_user, "first_name", None), getattr(from_user, "last_name", None)] if x)
            return name or "N/A"
        sender_chat = getattr(msg, "sender_chat", None)
        if sender_chat is not None:
            return getattr(sender_chat, "title", None) or getattr(sender_chat, "username", None) or "N/A"
    except Exception:
        pass
    return "N/A"

def message_text(msg) -> str:
    return getattr(msg, "text", None) or getattr(msg, "caption", None) or ""

def is_in_date_range(msg_dt_utc: datetime, start_utc, end_utc) -> bool:
    if start_utc and msg_dt_utc < start_utc:
        return False
    if end_utc and msg_dt_utc > end_utc:
        return False
    return True

async def async_sleep(seconds: int):
    seconds = max(1, int(seconds))
    seconds = min(seconds, 24 * 3600)
    await asyncio.sleep(seconds)