import io
import os
import re
import sys
import uuid
import traceback
from html import escape
from typing import Any, Optional, Tuple

from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from anony import anon, app, config, db, lang, userbot
from anony.helpers import format_exception, meval





hmses = {}
SUPPORT_CHANNEL = config.SUPPORT_CHANNEL
pending_users = {}


@app.on_message(filters.reply & filters.regex("همسه") & filters.group, group=579)
async def reply_with_link(client, message):
    user_id = message.reply_to_message.from_user.id
    my_id = message.from_user.id
    bar_id = message.chat.id
    start_link = f"https://t.me/{app.username}?start=hms{my_id}to{user_id}in{bar_id}"
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("꙳. ارسل همستك .꙳", url=start_link)]
        ]
    )
    await message.reply_text(f"\n« ارسل الهمسه من هنا »\n", reply_markup=reply_markup)


@app.on_message(filters.command("start"), group=5790)
async def hms_start(client, message):
    if message.text.split(" ", 1)[-1].startswith("hms"):
        # [إصلاح #2] تخزين حالة الانتظار لكل مستخدم على حدة
        pending_users[message.from_user.id] = {
            "hms_ids": message.text,
            "waiting": True
        }
        await message.reply_text(
            "« أرسل الهمسه الآن »",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("˹✘˼", callback_data="hms_cancel")
            ]])
        )
        return


@app.on_message(filters.private & filters.text & ~filters.command("start"), group=576)
async def send_hms(client, message):
    # [إصلاح #2] التحقق من حالة الانتظار الخاصة بالمستخدم فقط
    data = pending_users.get(message.from_user.id)
    if not data or not data.get("waiting"):
        return

    hms_ids = data["hms_ids"]

    # [إصلاح #6] التحقق من صحة الرابط قبل البارس
    try:
        to_id = int(hms_ids.split("to")[-1].split("in")[0])
        from_id = int(hms_ids.split("hms")[-1].split("to")[0])
        in_id = int(hms_ids.split("in")[-1])
    except (ValueError, IndexError):
        pending_users.pop(message.from_user.id, None)
        return await message.reply_text("» رابط الهمسه غير صالح")

    # [إضافة #8] منع إرسال همسة لنفسك
    if to_id == from_id:
        pending_users.pop(message.from_user.id, None)
        return await message.reply_text("» لا يمكنك إرسال همسه لنفسك")

    # [إضافة #11] حد الطول الأقصى للهمسة
    if len(message.text) > 1000:
        return await message.reply_text("» الهمسه طويله جداً (الحد الأقصى 1000 حرف)")

    # [إصلاح #3] جلب المستخدمين مرة واحدة + استخدام tg://user بدل tg://openmessage
    try:
        to_user = await app.get_users(to_id)
        to_url = f"https://t.me/{to_user.username}" if to_user.username else f"tg://user?id={to_id}"
        to_name = to_user.first_name
    except Exception:
        to_url = f"tg://user?id={to_id}"
        to_name = "مستخدم"

    try:
        from_user = await app.get_users(from_id)
        from_url = f"https://t.me/{from_user.username}" if from_user.username else f"tg://user?id={from_id}"
        from_name = from_user.first_name
    except Exception:
        from_url = f"tg://user?id={from_id}"
        from_name = "مستخدم"

    # [إصلاح #5] التخزين في قاعدة البيانات بدل الذاكرة
    hms_data = {"hms": message.text, "bar": in_id, "from_id": from_id}
    hmses[str(to_id)] = hms_data
    try:
        await db.set_hms(to_id, hms_data)
    except Exception:
        pass

    # اسم المستخدم الحالي
    user = await client.get_chat(message.from_user.id)
    name = user.first_name

    await message.reply_text("تم إرسال الهمسة بنجاح")

    await app.send_message(
        chat_id=in_id,
        text=f"""<b>⭓ᴍᴜꜱɪᴄ✘ᴠᴇɢᴧ♪\n╮⦿ هذه الهمسه لك: <a href="{to_url}">{to_name}</a>\n╯⦿ من هذا الشخص: <a href="{from_url}">{from_name}</a></b>""",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("꙳.افتح.꙳", callback_data="hms_answer"),
            ],
            [
                InlineKeyboardButton("꙳.ᴠᴇɢᴧ.꙳", url=SUPPORT_CHANNEL)
            ]
        ])
    )

    # [إصلاح #2] حذف حالة الانتظار بعد الإرسال
    pending_users.pop(message.from_user.id, None)


@app.on_callback_query(filters.regex("hms_answer"), group=5766565)
async def display_hms(client, callback):
    in_id = callback.message.chat.id
    who_id = callback.from_user.id

    # [إصلاح #5] جلب الهمسه من الذاكرة أو قاعدة البيانات
    hms = hmses.get(str(who_id))
    if hms is None:
        try:
            hms = await db.get_hms(who_id)
        except Exception:
            hms = None

    # [إضافة #9] التحقق من وجود الهمسة
    if hms is None:
        return await callback.answer("» حجي هذه لا تخصك انلقع «", show_alert=True)

    if hms.get("bar") == in_id:
        # [إضافة #10] حذف الهمسه بعد قراءتها
        hmses.pop(str(who_id), None)
        try:
            await db.del_hms(who_id)
        except Exception:
            pass
        await callback.answer(hms.get("hms", ""), show_alert=True)
    else:
        await callback.answer("» حجي هذه لا تخصك انلقع «", show_alert=True)


@app.on_callback_query(filters.regex("hms_cancel"), group=57967)
async def cancel_hms(client, callback):
    # [إصلاح #2] حذف حالة الانتظار الخاصة بالمستخدم
    pending_users.pop(callback.from_user.id, None)

    await client.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=" تم إلغاء الهمسه بنجاح"
    )