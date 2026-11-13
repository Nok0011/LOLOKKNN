# • ترخيص بواسطه : @TopVeGa
# • علامة تجارية : VEGA & Sound
# • حرية التعديل و النشر ©2015 - 2026

import os
import random
import requests
import asyncio
import html
import logging
from datetime import datetime
from pytz import timezone

from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Message,
    InputMediaPhoto
)
from pyrogram.enums import ParseMode, ChatType, ChatMembersFilter, ChatMemberStatus

from anony import app, db, lang, config
from anony.helpers.admins import is_owner, banned_check, admin_check, is_admin


# ========== المتغيرات العامة ==========
OWNER_ID = config.OWNER_ID
SUPPORT_CHANNEL = config.SUPPORT_CHANNEL
SUPPORT_CHAT = config.SUPPORT_CHAT

CURRENT_OWNER_ID = OWNER_ID
group_locks = {}
bot_name_cache = {}

media_cache = {}
active_slideshows = {}

# ⚠️ ضع Userhash الخاص بك هنا إذا كان لديك حساب في Catbox
# يمكنك الحصول عليه من: https://catbox.moe/user/manage.php
CATBOX_USERHASH = ""  # اتركه فارغاً إذا لم يكن لديك حساب


# ========== دوال مساعدة ==========
def get_file_id(msg: Message):
    if msg.media:
        for message_type in ("photo", "animation", "audio", "document", "video", "video_note", "sticker"):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                return obj


def safe_mention(user) -> str:
    """بناء mention آمن يدعم Chat و User"""
    mention = getattr(user, "mention", None)
    if mention:
        return mention
    first_name = getattr(user, "first_name", None) or "مستخدم"
    return f"<a href='tg://user?id={user.id}'>{first_name}</a>"


# ========== قائمة الردود التلقائية ==========
KEEMO_RESPONSES = [
    "هاها {name} أنت مين 😂",
    "شخبارك {name} يالغبي 🐸",
    "أهلاً وسهلاً بك {name} 🤍",
    "تشرفنا {name} نورت 🫡",
    "شو بدك {name} بدي أعملك بلوك 😤",
    "خر {name} تعبت من نداءك ",
    "{name} طلعت حمار 😂🐴",
    "هاي {name} أنت بتعرف تحكي أصلن 🤪",
    "أمرني {name} أنا معاك 🤍",
    "{name} معاك لحد الآخر 🔥"
]


# ========== دالة عامة لعرض الصور مع التقليب التلقائي ==========
async def send_rich_media(client, message, text, btn, user_id):
    try:
        photos = [p.file_id async for p in client.get_chat_photos(user_id, limit=10)]

        if not photos:
            return await message.reply_text(
                text, parse_mode=ParseMode.HTML,
                reply_markup=btn, disable_web_page_preview=True
            )

        if len(photos) == 1:
            return await message.reply_photo(
                photos[0], caption=text,
                parse_mode=ParseMode.HTML, reply_markup=btn
            )

        msg = await message.reply_photo(
            photos[0], parse_mode=ParseMode.HTML, reply_markup=btn
        )
        media_cache[msg.id] = {"photos": photos, "text": text, "btn": btn}
        active_slideshows[msg.id] = asyncio.create_task(
            auto_slide(client, msg, msg.id, len(photos))
        )
    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ: {str(e)}")


async def auto_slide(client, msg, msg_id, total):
    current = 0
    try:
        while msg_id in media_cache:
            await asyncio.sleep(2.5)
            if msg_id not in media_cache:
                break

            d = media_cache[msg_id]
            current = (current + 1) % total

            try:
                await msg.edit_media(
                    media=InputMediaPhoto(
                        media=d["photos"][current],
                        caption=d["text"],
                        parse_mode=ParseMode.HTML
                    ),
                    reply_markup=d["btn"]
                )
            except Exception:
                break
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"خطأ في السلايد شو: {e}")
    finally:
        media_cache.pop(msg_id, None)
        active_slideshows.pop(msg_id, None)


# ========== 1) أمر المطور ==========
@app.on_message(filters.command(["المطور", "مطور", "مطور البوت", "/dev"], ""), group=1)
@banned_check
async def dev_cmd(client: Client, message: Message):
    global CURRENT_OWNER_ID
    dev_id = CURRENT_OWNER_ID if CURRENT_OWNER_ID else OWNER_ID

    # استخدام get_users للحصول على كائن User (يحتوي على mention)
    try:
        user = await client.get_users(dev_id)
    except Exception:
        user = await client.get_chat(dev_id)

    try:
        chat_title = f"• اسم: {message.from_user.mention}\n• اسم الدردشة: {message.chat.title}" if message.from_user else f"• اسم الدردشة: {message.chat.title}"
        link = f"https://t.me/{message.chat.username}" if message.chat.username else f"https://t.me/{message.chat.id}"
        await client.send_message(
            dev_id,
            f"• عزيزي المطور هناك شخص يريدك\n{chat_title}\n• معرف الدردشة: {message.chat.id}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                f"{message.chat.title or 'الدردشة'}", url=link
            )]])
        )
    except Exception:
        pass

    text = f"""• الاسم: {safe_mention(user)}
• المعرف: @{getattr(user, 'username', None) or 'لا يوجد'}
• البايو: {getattr(user, 'bio', None) or 'لا يوجد'}
• الرتبه: مطور البوت"""

    btn = InlineKeyboardMarkup([[InlineKeyboardButton(user.first_name, copy_text=str(user.id))]])
    await send_rich_media(client, message, text, btn, dev_id)


# ========== 2) أمر تغيير المطور ==========
@app.on_message(filters.command("تغير المطور", "") & filters.private, group=2)
@banned_check
@is_owner
async def change_dev(client: Client, message: Message):
    global CURRENT_OWNER_ID
    try:
        msg = await client.ask(
            chat_id=message.chat.id,
            text="•  أرسل المعرف أو الأيدي الخاص بالمطور الجديد:",
            timeout=60,
            reply_to_message_id=message.id,
            filters=filters.user(message.from_user.id)
        )

        if not msg.text:
            return await message.reply_text("• يجب إرسال معرف أو أيدي صالح")
        new_dev = msg.text.strip()
        if new_dev.startswith("@"):
            user = await client.get_users(new_dev)
        else:
            user = await client.get_users(int(new_dev))

        CURRENT_OWNER_ID = user.id

        await message.reply_text(
            f"• تم تغيير المطور بنجاح\n"
            f"• المطور الجديد: {safe_mention(user)}\n"
            f"• الأيدي:<code> {user.id}</code>\n"
            f"• المعرف: @{user.username if user.username else 'لا يوجد'}"
        )
    except ValueError:
        await message.reply_text("• يجب أن يكون الأيدي أرقام فقط")
    except Exception as e:
        await message.reply_text(f"• لم أتمكن من تغيير المطور: {str(e)}")


# ========== 3) أمر حذف المطور ==========
@app.on_message(filters.command(["حذف المطور"], "") & filters.private, group=3)
@banned_check
@is_owner
async def delete_dev(client: Client, message: Message):
    global CURRENT_OWNER_ID

    if CURRENT_OWNER_ID is None or str(CURRENT_OWNER_ID) == str(OWNER_ID):
        return await message.reply_text("• لا يوجد مطور إضافي ليتم حذفه\n• المطور الحالي هو المطور الأساسي الافتراضي")

    try:
        current_dev = await client.get_chat(CURRENT_OWNER_ID)
        default_dev = await client.get_chat(OWNER_ID)
        dev_name = current_dev.first_name
        dev_id = current_dev.id
        CURRENT_OWNER_ID = None
        await message.reply_text(
            f"• تم حذف المطور الإضافي بنجاح\n"
            f"• الاسم: {dev_name}\n"
            f"• الأيدي: <code>{dev_id}</code>\n\n"
            f"• تم الرجوع إلى المطور الأساسي:\n"
            f"• الاسم: {default_dev.first_name}\n"
            f"• الأيدي: {default_dev.id}"
        )
    except Exception as e:
        await message.reply_text(f"• لم أتمكن من حذف المطور: {str(e)}")


# ========== 4) أوامر قفل وفتح الايدي ==========
@app.on_message(filters.command(["قفل الايدي", "قفل ايدي", "lock_id"], "") & filters.group, group=10)
@banned_check
@admin_check
async def lock_id_command(client, message):
    chat_id = message.chat.id
    group_locks[chat_id] = True
    await message.reply_text("تم قفل أمر الايدي في هذا الجروب على الجميع.")


@app.on_message(filters.command(["فتح الايدي", "فتح ايدي", "unlock_id"], "") & filters.group, group=11)
@banned_check
@admin_check
async def unlock_id_command(client, message):
    chat_id = message.chat.id
    group_locks[chat_id] = False
    await message.reply_text("تم فتح أمر الايدي في هذا الجروب للجميع.")


@app.on_message(filters.command(["ايدي", "الايدي", "ا", "id", "/id", "/ID"], "") & (filters.group | filters.private), group=12)
@banned_check
async def user_id(client, message):
    chat_id = message.chat.id
    if group_locks.get(chat_id, False):
        return await message.reply_text("الامر معطل من قبل الادمن")
    
    user = message.from_user
    chat = message.chat  
    photo = None    
    
    if user.photo:
        photo = await client.download_media(user.photo.big_file_id, in_memory=True)    
    
    text = f"""<b>
• الاسم: {user.mention}
• المعرف: @{user.username or 'لا يوجد'}
• الايدي: <code>{user.id}</code>
• الدردشه: {chat.title or 'خاص'}
• ايدي الدردشه: <code>{chat.id}</code></b>\nㅤ"""   
    
    btn = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            user.first_name,
            url=f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
        )
    ]])    
    
    if photo:
        await message.reply_photo(
            photo, 
            caption=text, 
            reply_markup=btn
        )
    else:
        await message.reply_text(text, reply_markup=btn)
        
        
        
# ========== 6) أمر المالك ==========
@app.on_message(filters.command(["المالك", "صاحب الخرابه", "المنشي"], "") & filters.group, group=13)
@banned_check
async def owner_cmd(client, message):
    owner = None
    async for m in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if m.status == enums.ChatMemberStatus.OWNER:
            owner = m.user
            break

    if not owner:
        return await message.reply_text("الحساب الخاص بالدردشة محذوف")

    text = f"""• المالك: {safe_mention(owner)}
• المعرف: @{owner.username or 'لا يوجد'}
• الايدي: <code>{owner.id}</code>
• الدردشه: {message.chat.title}
• ايدي الدردشه: <code>{message.chat.id}</code>"""

    btn = InlineKeyboardMarkup([[InlineKeyboardButton(owner.first_name, copy_text=str(owner.id))]])
    await send_rich_media(client, message, text, btn, owner.id)


# ========== 7) أمر الكشف ==========
@app.on_message(filters.command(["كشف", "مين دا", "الكشف"], "") & filters.group, group=14)
@banned_check
async def kashf_cmd(client, message):
    chat_id = message.chat.id
    if group_locks(chat_id, False):
        return await message.reply_text("الامر معطل من قبل الادمن")

    if not message.reply_to_message:
        return

    target = message.reply_to_message.from_user
    text = f"""• المستخدم: {safe_mention(target)}
• المعرف: @{target.username or 'لا يوجد'}
• الايدي: <code>{target.id}</code>
• الدردشه: {message.chat.title or 'خاص'}
• معرف الدردشه: @{message.chat.username or 'لا يوجد'}
• ايدي الدردشه: <code>{message.chat.id}</code>"""

    btn = InlineKeyboardMarkup([[InlineKeyboardButton(target.first_name, copy_text=str(target.id))]])
    await send_rich_media(client, message, text, btn, target.id)


# ========== 8) أمر كيمي (مبرمج السورس) ==========
@app.on_message(filters.command(
    ["كيمي", "مطور فيجا", "صاحب سورس فيجا", "مبرمج السورس",
     "مطور السورس", "/kim", "KIM", "كيم", "مبرمج", "المبرمج"], ""), group=16)
@banned_check
async def handle_user_kim(client, message):
    command = message.text.split()[0].lower()
    if command in ["مطور", "مطور البوت", "المطور"]:
        return
    try:
        user = await client.get_chat("TopVeGa")
        name = user.first_name
        username = user.username if user.username else "لا يوجد"
        bio = user.bio if user.bio else "لا يوجد"
        caption = (
            f"<b>ㅤ\n"
            f"• الاسم : {name}\n"
            f"• المعرف : @{username}\n"
            f"• الايدي : <code>{user.id}</code>\n"
            f"• البايو : {bio}</b>\n"
            f"• الرتبه : مؤسس النظام</b>\nㅤ"
        )

        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton(name, url=f"https://t.me/{username}")]]
        )
        if user.photo:
            photo_file = await client.download_media(user.photo.big_file_id)
            await message.reply_photo(
                photo=photo_file,
                caption=caption,
                reply_markup=button,
                show_caption_above_media=True,
                parse_mode=ParseMode.HTML
            )
            if photo_file and os.path.exists(photo_file):
                os.remove(photo_file)
        else:
            await message.reply_text(
                caption,
                reply_markup=button,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        print(f"Error: {e}")
        await message.reply_text("حدث خطأ في جلب المعلومات")


# ========== 9) تعيين اسم البوت ==========
@app.on_message(filters.regex(r"تعين اسم البوت|set bot name") & filters.private, group=30)
async def set_bot_name(client, message):
    try:
        ask = await app.ask(message.chat.id, "ارسل الاسم الجديد للبوت", timeout=300)
        bot_name_cache['name'] = ask.text
        await message.reply_text(f"✅ تم تعيين الاسم {bot_name_cache['name']}")
    except Exception as e:
        await message.reply_text(f"حدث خطأ: {e}")


# ========== 10) أوامر البوت التلقائية ==========
@app.on_message(filters.command(["بوت", "البوت", "بوتي", "بوتك", "/bot"], "") & filters.group, group=31)
@banned_check
async def bot_name_command(client, message):
    if 'name' not in bot_name_cache:
        me = await app.get_me()
        bot_name_cache['name'] = me.first_name
        bot_name_cache['username'] = me.username

    name = bot_name_cache['name']
    bot_username = bot_name_cache['username']

    bar = random.choice(KEEMO_RESPONSES).format(name=name)

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("أشواقي", url=f"https://t.me/{bot_username}?startgroup=True")
    ]])

    await message.reply_text(bar, disable_web_page_preview=True, reply_markup=keyboard)


@app.on_message(filters.text & filters.group, group=32)
async def bot_name_mention(client, message):
    if 'name' not in bot_name_cache:
        me = await app.get_me()
        bot_name_cache['name'] = me.first_name
        bot_name_cache['username'] = me.username
    name = bot_name_cache['name']
    if message.text and message.text.strip().lower() == name.lower():
        bot_username = bot_name_cache['username']

        bar = random.choice(KEEMO_RESPONSES).format(name=name)

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("أضفني", url=f"https://t.me/{bot_username}?startgroup=True")
        ]])

        await message.reply_text(bar, disable_web_page_preview=True, reply_markup=keyboard)


# ========== دالة رفع على catbox.moe مع دعم Userhash ==========
def upload_to_catbox(file_path):
    """
    رفع الملف إلى catbox.moe
    يدعم Userhash إذا تم تعيينه في CATBOX_USERHASH
    """
    try:
        url = "https://catbox.moe/user/api.php"

        # تحضير البيانات
        data = {'reqtype': 'fileupload'}
        if CATBOX_USERHASH and CATBOX_USERHASH.strip():
            data['userhash'] = CATBOX_USERHASH.strip()

        with open(file_path, 'rb') as f:
            files = {'fileToUpload': f}

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            response = requests.post(
                url,
                files=files,
                data=data,
                headers=headers,
                timeout=180
            )

        if response.status_code == 200:
            result = response.text.strip()

            if "error" in result.lower():
                return False, f"خطأ من الموقع: {result}"

            if result.startswith("http"):
                return True, result

            if result and not result.startswith("http"):
                return True, f"https://files.catbox.moe/{result}"

            return False, f"رد غير مفهوم من الموقع: {result}"

        elif response.status_code == 412:
            return False, "الحظر على مستوى الشبكة (412) - Catbox محظور في منطقتك. جرب استخدام VPN أو Proxy على الخادم."

        elif response.status_code == 403:
            return False, "ممنوع (403) - الوصول إلى Catbox محظور من خادمك."

        else:
            return False, f"خطأ HTTP: {response.status_code} - {response.text[:100]}"

    except requests.exceptions.Timeout:
        return False, "انتهت مهلة الاتصال بالموقع (180 ثانية)"
    except requests.exceptions.ConnectionError:
        return False, "فشل الاتصال بالموقع - تحقق من الشبكة أو استخدم VPN"
    except Exception as e:
        return False, str(e)


def fix_url_extension(url, file_ext):
    base_url = url.split('?')[0]
    current_ext = os.path.splitext(base_url)[1].lower()
    valid_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mkv', '.avi', '.mp3', '.wav', '.flac', '.aac', '.ogg']
    if not current_ext or current_ext not in valid_exts:
        return base_url + file_ext
    return url


def smart_upload(file_path):
    """رفع على catbox.moe فقط"""
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        media_type = '.jpg'
    elif file_ext in ['.mp4', '.mkv', '.avi', '.mov']:
        media_type = '.mp4'
    elif file_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
        media_type = '.mp3'
    else:
        media_type = file_ext

    success, url = upload_to_catbox(file_path)
    if success:
        return True, fix_url_extension(url, media_type)

    return False, url


@app.on_message(filters.command(["tgm", "تلجراف", "/telegraph", "تلغراف", "ميديا"], ""))
async def upload_media(client, message):
    if not message.reply_to_message:
        return await message.reply_text("**قم بالرد على الصورة أو الفيديو أو الملف أو الصوت**")

    media = message.reply_to_message
    if not (media.photo or media.video or media.document or media.sticker or media.animation or media.audio or media.voice):
        return await message.reply_text("**الرجاء الرد على صورة أو فيديو أو ملف أو ملصق أو صوت**")

    if media.photo:
        file_size = media.photo.file_size
        file_ext = '.jpg'
    elif media.video:
        file_size = media.video.file_size
        file_ext = '.mp4'
    elif media.audio:
        file_size = media.audio.file_size
        file_ext = '.mp3'
    elif media.voice:
        file_size = media.voice.file_size
        file_ext = '.mp3'
    elif media.document:
        file_size = media.document.file_size
        if media.document.file_name:
            doc_ext = os.path.splitext(media.document.file_name)[1].lower()
            if doc_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
                file_ext = '.mp3'
            else:
                file_ext = doc_ext or '.file'
        else:
            file_ext = '.file'
    elif media.sticker:
        file_size = media.sticker.file_size
        file_ext = '.webp'
    else:  # animation
        file_size = media.animation.file_size
        file_ext = '.mp4'

    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("**❌ الحد المسموح به هو 200MB فقط (حد catbox.moe)**")

    try:
        msg = await message.reply("⏳ جاري المعالجة...")
        file_path = await media.download()
        await msg.edit_text("📤 جاري الرفع على catbox.moe...")
        success, result = smart_upload(file_path)

        try:
            os.remove(file_path)
        except Exception:
            pass

        if success:
            await msg.edit_text(
                f"<b>• تم انشاء رابط الميديا بنجاح ✅\n\n"
                f"• الرابط:\n{result}</b>",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("نسخ الرابط", copy_text=result),
                        InlineKeyboardButton("مشاركة", url=f"https://t.me/share/url?url={result}"),
                    ],
                ]),
                link_preview_options=None
            )
        else:
            await msg.edit_text(
                f"❌ **فشل الرفع على catbox.moe**\n\n"
                f"**السبب:** `{result}`\n\n"
                f"⚠️ **ملاحظة:** خطأ 412 يعني أن Catbox محظور في منطقة خادمك أو من مزود الخدمة.\n"
                f"**الحل:** يجب تشغيل VPN أو Proxy على الخادم نفسه، أو تغيير DNS إلى 8.8.8.8"
            )

    except Exception as e:
        await message.reply_text(f"❌ **حدث خطأ:** `{str(e)}`")


# ========== أمر إنشاء رابط المجموعة ==========
@app.on_message(filters.command(["رابط", "انشاء رابط", "لينك"], "") & filters.group, group=283277)
async def create_invite_link(client, message):
    try:
        user_id = message.from_user.id
        get = await client.get_chat_member(message.chat.id, user_id)
        if get.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or user_id == OWNER_ID or user_id == 7654641648:
            link = await client.create_chat_invite_link(
                chat_id=message.chat.id,
                name="رابط تم انشاؤه بواسطة البوت",
                member_limit=300,
                expire_date=None
            )

            share_url = (
                f"https://t.me/share/url?"
                f"url={link.invite_link}&"
                f"text=انضم%20الينا"
            )

            btn = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("نسخ الرابط", copy_text=link.invite_link),
                    InlineKeyboardButton("مشاركة", url=share_url),
                ]
            ])

            await message.reply_text(
                f"<b>• تم إنشاء رابط جديد للمجموعة\n\n"
                f"• الحد الأقصى: {link.member_limit if link.member_limit else 'لا محدود'}\n"
                f"• الصلاحية:</b> {'لا تنتهي' if not link.expire_date else link.expire_date}",
                disable_web_page_preview=True,
                reply_markup=btn
            )

            await message.delete()

        else:
            await message.reply_text(
                "❌ **هذا الأمر يخص المشرفين فقط!**\n"
                "🚫 غير مسموح لك باستخدام هذا الأمر.",
                quote=True
            )

    except Exception as e:
        print(f"خطأ في انشاء الرابط: {e}")
        await message.reply_text("⚠️ **حدث خطأ أثناء انشاء الرابط، تأكد من صلاحيات البوت**")