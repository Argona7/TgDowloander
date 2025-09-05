from pyrogram import Client
from pyrogram.raw.functions.channels import GetForumTopics
from pyrogram.raw.types import InputChannel, InputPeerChannel

async def list_forum_topics(app: Client, chat_id: int, limit_page: int = 100):
    """
    Возвращает список тем форума (id, title, top_message_id).
    """
    peer = await app.resolve_peer(chat_id)
    if not isinstance(peer, InputPeerChannel):
        return []

    input_channel = InputChannel(channel_id=peer.channel_id, access_hash=peer.access_hash)

    res = await app.invoke(GetForumTopics(
        channel=input_channel,
        q="",
        offset_date=0,
        offset_id=0,
        offset_topic=0,
        limit=limit_page
    ))

    topics = []
    for t in getattr(res, "topics", []) or []:
        topics.append({
            "id": getattr(t, "id", None),
            "title": getattr(t, "title", "") or "",
            "top_message_id": getattr(t, "top_message", None)
        })
    return topics