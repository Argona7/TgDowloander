import sys
from pathlib import Path
from datetime import timezone
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError

from .logging_setup import setup_logging
from .config import load_dotenv, env_int, mask
from .utils import (
    parse_date_range, read_last_saved_id, message_text, author_string,
    normalize_text, to_utc_iso, is_in_date_range, async_sleep
)
from .resolver import resolve_chat_or_fail
from .forum import list_forum_topics

async def dump_channel():
    setup_logging()
    loaded = load_dotenv(override=True)
    if loaded:
        logger.success("[.env] Загружены ключи: {}", ", ".join(sorted(loaded.keys())))
    else:
        logger.warning("[.env] Файлы не найдены или пусты")

    logger.info(
        "[config] API_ID={} SESSION_NAME={} CHANNEL={} OUTPUT_FILE={} DATE_RANGE='{}' LIMIT={} API_HASH={}",
        __import__("os").environ.get("API_ID"),
        __import__("os").environ.get("SESSION_NAME"),
        __import__("os").environ.get("CHANNEL"),
        __import__("os").environ.get("OUTPUT_FILE"),
        __import__("os").environ.get("DATE_RANGE", ""),
        __import__("os").environ.get("LIMIT", ""),
        mask(__import__("os").environ.get("API_HASH"))
    )

    # Параметры
    os = __import__("os")
    api_id = env_int("API_ID")
    api_hash = os.environ.get("API_HASH")
    session_name = os.environ.get("SESSION_NAME")
    channel = os.environ.get("CHANNEL")
    output_file = os.environ.get("OUTPUT_FILE")
    date_range = os.environ.get("DATE_RANGE", "").strip()
    limit = env_int("LIMIT")
    progress_every = env_int("PROGRESS_EVERY", 500)
    page_size = env_int("PAGE_SIZE", 200)

    if not all([api_id, api_hash, session_name, channel, output_file]):
        logger.error("Нужны API_ID, API_HASH, SESSION_NAME, CHANNEL, OUTPUT_FILE")
        sys.exit(2)

    start_utc, end_utc = parse_date_range(date_range) if date_range else (None, None)

    out_path = Path(output_file).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    last_saved_id = read_last_saved_id(out_path)
    if last_saved_id:
        logger.info("[resume] Последний записанный id: {}", last_saved_id)

    app = Client(name=session_name, api_id=api_id, api_hash=api_hash, in_memory=False)

    saved = 0
    seen = 0
    processed_for_log = 0
    skip_stats = {"no_text": 0, "topic_mismatch": 0, "date_out": 0, "already_saved": 0, "no_date": 0}

    f = out_path.open("a", encoding="utf-8", newline="\n")

    try:
        await app.start()

        # 1) Резолв источника (+ поддержка t.me/c/…)
        try:
            chat, resolved_chat_id, tail_from_link = await resolve_chat_or_fail(app, channel)
            chat_title = getattr(chat, "title", None) or getattr(chat, "username", None) or str(resolved_chat_id)
            logger.success("[info] Источник: {} (id={})", chat_title, resolved_chat_id)
        except Exception as e:
            logger.exception("[error] Не удалось резолвить чат: {}", e)
            sys.exit(3)

        # 2) Форум? — определяем выбранную тему (topic_id / top_message_id)
        is_forum = bool(getattr(chat, "is_forum", False))
        selected_topic_id = None
        selected_top_message_id = None

        if is_forum and tail_from_link is not None:
            # tail обычно = topic_id; попробуем замапить в top_message_id среди первых 100 тем
            try:
                topics = await list_forum_topics(app, resolved_chat_id, limit_page=100)
            except RPCError as e:
                logger.error("[forum] Не удалось получить список тем: {}", e)
                topics = []

            for t in topics:
                if t.get("id") == tail_from_link:
                    selected_topic_id = t["id"]
                    selected_top_message_id = t["top_message_id"]
                    break

            if selected_topic_id:
                logger.info("[forum] Тема из ссылки: topic_id={} top_message_id={}", selected_topic_id, selected_top_message_id)
            else:
                # не нашли среди первых 100 — считаем, что tail это top_message_id
                selected_top_message_id = tail_from_link
                logger.info("[forum] Принял из ссылки top_message_id={}", selected_top_message_id)

        if is_forum and (selected_topic_id is None and selected_top_message_id is None):
            logger.info("[forum] Чат в режиме форума. Получаю список тем…")
            topics = []
            try:
                topics = await list_forum_topics(app, resolved_chat_id, limit_page=100)
            except RPCError as e:
                logger.error("[forum] Не удалось получить список тем через raw API: {}", e)

            if topics:
                logger.info("Доступные темы (первые 100):")
                for i, t in enumerate(topics, 1):
                    logger.info("  {:>2}) topic_id={}  top_message_id={}  title={!r}",
                                i, t["id"], t["top_message_id"], t["title"])
                user_choice = input("\nВведите номер из списка или top_message_id (Enter — вся история): ").strip()
                if user_choice:
                    if user_choice.isdigit():
                        num = int(user_choice)
                        if 1 <= num <= len(topics):
                            selected_topic_id = topics[num - 1]["id"]
                            selected_top_message_id = topics[num - 1]["top_message_id"]
                        else:
                            selected_top_message_id = num
                    else:
                        try:
                            selected_top_message_id = int(user_choice)
                        except ValueError:
                            logger.warning("[forum] Не распознал ввод — выгружаю всю историю форума.")
                            selected_topic_id = None
                            selected_top_message_id = None
                else:
                    logger.info("[forum] Выбрана выгрузка всей истории форума.")
            else:
                logger.warning("[forum] Список тем пуст/не получен — выгружаю всю историю форума.")

        if selected_topic_id or selected_top_message_id:
            logger.info("[forum] Фильтр включён: topic_id={} top_message_id={}", selected_topic_id, selected_top_message_id)

        # 3) Основной обход истории (Pyrogram v2: async generator)
        offset_id = 0
        eof = False

        while not eof:
            try:
                batch = []
                async for msg in app.get_chat_history(
                    chat_id=resolved_chat_id,
                    offset_id=offset_id,
                    limit=page_size
                ):
                    batch.append(msg)

            except FloodWait as e:
                sec = int(getattr(e, "value", 0) or getattr(e, "x", 0) or 0) or 5
                logger.warning("[FLOOD_WAIT] Сплю {} сек…", sec)
                await async_sleep(sec)
                continue
            except RPCError as e:
                logger.error("[RPCError] {} — пауза 5 сек и повтор…", e)
                await async_sleep(5)
                continue

            if not batch:
                break

            page_oldest_id = batch[-1].id

            for msg in reversed(batch):
                seen += 1
                processed_for_log += 1
                if msg is None:
                    continue

                # Возобновление
                if last_saved_id and msg.id <= last_saved_id:
                    skip_stats["already_saved"] += 1
                    continue

                # Фильтр по теме (forum: message_thread_id == topic_id; также учитываем top_message_id)
                if selected_topic_id is not None or selected_top_message_id is not None:
                    mtid = getattr(msg, "message_thread_id", None)          # forum topics
                    rtop = getattr(msg, "reply_to_top_message_id", None)    # дискуссии/legacy
                    mid  = getattr(msg, "id", None)

                    ok = False
                    if selected_topic_id is not None and mtid == selected_topic_id:
                        ok = True
                    if selected_top_message_id is not None and (mid == selected_top_message_id or rtop == selected_top_message_id):
                        ok = True

                    if not ok:
                        skip_stats["topic_mismatch"] += 1
                        continue

                txt = message_text(msg)
                if not txt:
                    skip_stats["no_text"] += 1
                    continue

                msg_dt = getattr(msg, "date", None)
                if msg_dt is None:
                    skip_stats["no_date"] += 1
                    continue
                if msg_dt.tzinfo is None:
                    msg_dt = msg_dt.replace(tzinfo=timezone.utc)
                else:
                    msg_dt = msg_dt.astimezone(timezone.utc)

                if not is_in_date_range(msg_dt, start_utc, end_utc):
                    skip_stats["date_out"] += 1
                    continue

                msg_id = getattr(msg, "id", None)
                auth = author_string(msg)
                body = normalize_text(txt)
                dt_iso = to_utc_iso(msg_dt)

                record = (
                    f"---\n"
                    f"id: {msg_id}\n"
                    f"date: {dt_iso}\n"
                    f"author: {auth}\n"
                    f"text:\n"
                    f"{body}\n\n"
                )
                f.write(record)
                saved += 1

                if limit and saved >= limit:
                    eof = True
                    break

                if processed_for_log >= progress_every:
                    logger.info("[progress] scanned={} saved={} last_id={}", seen, saved, msg_id)
                    processed_for_log = 0

            offset_id = page_oldest_id
            if last_saved_id and page_oldest_id <= last_saved_id:
                break

        logger.info(
            "[skips] already_saved={} no_text={} topic_mismatch={} date_out={} no_date={}",
            skip_stats["already_saved"],
            skip_stats["no_text"],
            skip_stats["topic_mismatch"],
            skip_stats["date_out"],
            skip_stats["no_date"],
        )
        logger.success("[done] Просмотрено: {}  Сохранено: {}  Файл: {}", seen, saved, out_path)

    finally:
        try:
            await app.stop()
        except Exception:
            logger.exception("Ошибка при остановке клиента")
        f.close()