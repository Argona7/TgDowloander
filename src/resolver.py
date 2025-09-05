import re
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait
from .utils import async_sleep

def parse_private_c_link(value: str):
    """
    https://t.me/c/<digits>/<tail>  → (-100<digits>, tail)
    tail — для форумов это часто topic_id; иногда используется как top_message_id.
    """
    if not value:
        return None, None
    s = value.strip()
    m = re.search(r"(?:https?://)?t\.me/c/(\d+)(?:/(\d+))?$", s)
    if not m:
        return None, None
    digits = int(m.group(1))
    tail_id = int(m.group(2)) if m.group(2) else None
    chat_id = int(f"-100{digits}")
    return chat_id, tail_id

async def resolve_chat_or_fail(app: Client, chat_ref):
    """
    Резолвит чат и, если это приватная супергруппа по числовому id (-100…),
    но в локальном storage нет access_hash — проходит по диалогам (get_dialogs),
    чтобы storage заполнился. Возвращает (chat_obj, resolved_chat_id, tail_id_from_link).
    """
    tail_from_link = None

    if isinstance(chat_ref, str):
        chat_id_from_c, tail_from_c = parse_private_c_link(chat_ref)
        if chat_id_from_c is not None:
            logger.info("[link] Обнаружена /c/ ссылка: chat_id={}  tail_id={}", chat_id_from_c, tail_from_c)
            chat_ref = chat_id_from_c
            tail_from_link = tail_from_c

    peer = chat_ref
    if isinstance(peer, str):
        s = peer.strip()
        if s.startswith("@"):
            s = s[1:]
        try:
            peer = int(s)
        except ValueError:
            peer = s  # username/публичная ссылка

    # 1) Прямая попытка
    try:
        chat = await app.get_chat(peer)
        return chat, chat.id, tail_from_link
    except Exception as e:
        logger.debug("Первый get_chat не удался ({}: {}), пробую через диалоги…", type(e).__name__, e)

    # 2) Если это -100... — ищем в диалогах (чтобы получить access_hash)
    if isinstance(peer, int) and str(peer).startswith("-100"):
        logger.info("Пробую найти чат {} в диалогах, чтобы получить access_hash…", peer)
        try:
            async for dialog in app.get_dialogs():
                c = dialog.chat
                if c and getattr(c, "id", None) == peer:
                    logger.success("Нашёл чат в диалогах: {} (id={})", c.title or c.username or c.id, c.id)
                    return c, c.id, tail_from_link
        except FloodWait as e:
            sec = int(getattr(e, "value", 0) or getattr(e, "x", 0) or 0) or 5
            logger.warning("[FLOOD_WAIT] Сплю {} сек на get_dialogs…", sec)
            await async_sleep(sec)
            # повтор
            async for dialog in app.get_dialogs():
                c = dialog.chat
                if c and getattr(c, "id", None) == peer:
                    logger.success("Нашёл чат в диалогах (повтор): {} (id={})", c.title or c.username or c.id, c.id)
                    return c, c.id, tail_from_link

        raise RuntimeError(
            "Чат по числовому id не найден в ваших диалогах. "
            "Убедись, что аккаунт состоит в супергруппе, и открой её один раз в Telegram-клиенте."
        )

    raise RuntimeError("Не удалось резолвить CHANNEL. Проверь ссылку/username и доступ к чату.")