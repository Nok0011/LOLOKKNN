# • ترخيص بواسطه : @TopVeGa
# • علامة تجارية : VEGA & Sound
# • حرية التعديل و النشر ©2015 - 2026


import time

from pyrogram import errors, filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from anony import anon, app, db, lang, queue, tg, yt
from anony.helpers import admin_check, buttons, can_manage_vc
from anony.helpers.admins import is_owner, banned_check


@app.on_callback_query(filters.regex("cancel_dl") & ~app.bl_users)
@lang.language()
async def cancel_dl(_, query: types.CallbackQuery):
    await query.answer()
    await tg.cancel(query)


async def _seek_helper(_, query: types.CallbackQuery, chat_id: int, delta: int):
    """دالة موحّدة للتقديم والتأخير"""
    media = queue.get_current(chat_id)
    if not media:
        return await query.answer()

    start = queue.get_start_time(chat_id) or time.time()
    current = int(time.time() - start)
    new_time = current + delta

    if new_time < 0:
        return await query.answer(
            "لا يمكن التأخير أكثر من بداية الأغنية", show_alert=True
        )
    if media.duration_sec and new_time >= media.duration_sec:
        return await query.answer(
            "لا يمكن التقديم أكثر من مدة الأغنية", show_alert=True
        )

    queue.set_start_time(chat_id, time.time() - new_time)
    media.time = new_time
    await anon.seek(chat_id, delta)


@app.on_callback_query(filters.regex("controls") & ~app.bl_users)
@lang.language()
@banned_check
@can_manage_vc
async def _controls(_, query: types.CallbackQuery):
    args = query.data.split()

    # ✅ حماية: أزرار بدون chat_id (timer / status فقط)
    if len(args) < 3:
        return await query.answer()

    action, chat_id = args[1], int(args[2])
    qaction = len(args) == 4
    user = query.from_user.mention

    if not await db.get_call(chat_id):
        try:
            return await query.answer(query.lang["not_playing"], show_alert=True)
        except errors.QueryIdInvalid:
            try:
                await query.message.delete()
            except Exception:
                pass
            return

    if action == "status":
        return await query.answer()
    if action == "timer":
        return await query.answer()

    await query.answer(query.lang["processing"], show_alert=True)

    if action == "pause":
        if not await db.playing(chat_id):
            return await query.answer(
                query.lang["play_already_paused"], show_alert=True
            )
        await anon.pause(chat_id)
        if qaction:
            return await query.message.reply_text(
                query.lang["paused"],
                reply_markup=buttons.close_markup(query.lang)
            )
        await query.message.reply_text(
            query.lang["play_paused"].format(user),
            reply_markup=buttons.close_markup(query.lang)
        )
        return

    elif action == "resume":
        if await db.playing(chat_id):
            return await query.answer(query.lang["play_not_paused"], show_alert=True)
        await anon.resume(chat_id)
        media = queue.get_current(chat_id)
        if media and not queue.get_start_time(chat_id):
            queue.set_start_time(chat_id, time.time() - media.time)
        if qaction:
            return await query.message.reply_text(
                query.lang["playing"],
                reply_markup=buttons.close_markup(query.lang)
            )
        await query.message.reply_text(
            query.lang["play_resumed"].format(user),
            reply_markup=buttons.close_markup(query.lang)
        )
        return

    elif action == "skip":
        await anon.play_next(chat_id)
        await query.message.reply_text(
            query.lang["play_skipped"].format(user),
            reply_markup=buttons.close_markup(query.lang)
        )
        return

    # ✅ زر التكرار
    elif action == "loop":
        loop = await db.get_loop(chat_id)
        new_loop = loop + 1
        await db.set_loop(chat_id, new_loop)
        return await query.answer(f"🔁 Loop: {new_loop}", show_alert=True)

    # ✅ التقديم 10 ثوانٍ
    elif action == "seek_fwd":
        return await _seek_helper(_, query, chat_id, +10)

    # ✅ التأخير 10 ثوانٍ
    elif action == "seek_back":
        return await _seek_helper(_, query, chat_id, -10)

    # ✅ الإعادة
    elif action == "replay":
        media = queue.get_current(chat_id)
        if media:
            media.user = user
        await anon.replay(chat_id)
        await query.message.reply_text(
            query.lang["play_replayed"].format(user),
            reply_markup=buttons.close_markup(query.lang)
        )
        return

    elif action == "force":
        pos, media = queue.check_item(chat_id, args[3])
        if not media or pos == -1:
            return await query.message.reply_text(query.lang["play_expired"])

        m_id = queue.get_current(chat_id).message_id
        queue.force_add(chat_id, media, remove=pos)
        try:
            await app.delete_messages(
                chat_id=chat_id, message_ids=[m_id, media.message_id], revoke=True
            )
            media.message_id = None
        except Exception:
            pass

        msg = await app.send_message(chat_id=chat_id, text=query.lang["play_next"])
        if not media.file_path:
            media.file_path = await yt.download(media.id, video=media.video)
        media.message_id = msg.id
        return await anon.play_media(chat_id, msg, media)

    elif action == "stop":
        await anon.stop(chat_id)
        await query.message.reply_text(
            query.lang["play_stopped"].format(user),
            reply_markup=buttons.close_markup(query.lang)
        )
        return


@app.on_callback_query(filters.regex("help") & ~app.bl_users)
@lang.language()
@banned_check
async def _help(_, query: types.CallbackQuery):
    data = query.data.split()
    if len(data) == 1:
        return await query.answer(url=f"https://t.me/{app.username}?start=help")

    if data[1] == "back":
        return await query.edit_message_text(
            text=query.lang["help_menu"], reply_markup=buttons.help_markup(query.lang)
        )
    elif data[1] == "close":
        try:
            await query.message.delete()
            return await query.message.reply_to_message.delete()
        except Exception:
            return

    await query.edit_message_text(
        text=query.lang[f"help_{data[1]}"],
        reply_markup=buttons.help_markup(query.lang, True),
    )


@app.on_callback_query(filters.regex("settings") & ~app.bl_users)
@lang.language()
@admin_check
@banned_check
async def _settings_cb(_, query: types.CallbackQuery):
    cmd = query.data.split()
    if len(cmd) == 1:
        return await query.answer()
    await query.answer(query.lang["processing"], show_alert=True)

    chat_id = query.message.chat.id
    _admin = await db.get_play_mode(chat_id)
    _delete = await db.get_cmd_delete(chat_id)
    _language = await db.get_lang(chat_id)

    if cmd[1] == "delete":
        _delete = not _delete
        await db.set_cmd_delete(chat_id, _delete)
    elif cmd[1] == "play":
        await db.set_play_mode(chat_id, _admin)
        _admin = not _admin
    await query.edit_message_reply_markup(
        reply_markup=buttons.settings_markup(
            query.lang,
            _admin,
            _delete,
            _language,
            chat_id,
        )
    )


@app.on_callback_query(filters.regex("close") & ~app.bl_users)
async def close_callback(_, query: types.CallbackQuery):
    try:
        await query.message.delete()
    except Exception:
        pass