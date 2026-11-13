# • ترخيص بواسطه : @TopVeGa
# • علامة تجارية : VEGA & Sound
# • حرية التعديل و النشر ©2015 - 2026


import time
from datetime import datetime
import pytz
from pyrogram import filters, types, Client, enums
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import PeerIdInvalid, UserNotParticipant
from typing import Optional
from PIL import Image, ImageFilter
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMembersFilter
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, Message, CallbackQuery
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired
from anony import app, db, lang, config
from anony.helpers import admin_check, is_admin, utils
from anony.helpers.admins import is_owner, banned_check


# ========== المتغيرات العامة ==========
OWNER_ID = config.OWNER_ID

s_rank_cooldown = {}
rel_hist = {}


@app.on_message(filters.command(["رتبتي", "/myrank", "رتبتِي"], "") & ~app.bl_users, group=799)
@lang.language()
@banned_check
async def my_rank(_, m: types.Message):
    user = m.from_user
    user_id = user.id
    rank = "👤 عضو عادي"
    rank_emoji = "👤"
    description = "ليس لديك أي صلاحيات خاصة في البوت"
    
    # التحقق من المطور الأساسي
    if user_id == OWNER_ID or str(user_id) == str(OWNER_ID):
        rank = "👑 • المطور الأساسي (Owner)"
        rank_emoji = "👑"
        description = "• لديك كامل الصلاحيات في البوت\n•  يمكنك التحكم بجميع الإعدادات\n• يمكنك رفع وتنزيل المطورين\n• يمكنك التحكم برتبة 𝐒"
    elif await db.is_s_rank(user_id):
        rank = "⭐ • رتبة  𝐒 (Super User)"
        rank_emoji = "⭐"
        description = "<b>• لديك صلاحيات خاصة في كل المجموعات\n• يمكنك استخدام أوامر الحظر والطرد\n• ترحيب مميز عند الانضمام\n• صلاحياتك تتبعك في كل المجموعات</b>"
    elif m.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        try:
            member = await app.get_chat_member(m.chat.id, user_id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                rank = "🛡️ مشرف (Admin)"
                rank_emoji = "🛡️"
                description = "✅ لديك صلاحيات إدارة في هذه المجموعة\n✅ يمكنك استخدام أوامر التحكم بالبوت هنا"
        except:
            pass
    rank_message = f"""<b>
{rank_emoji} معلومات رتبتك {rank_emoji}

•  الاسم: {user.mention}
• الايدي: <code>{user_id}</code>

{rank}

• الوصف:
{description}
• ملاحظة: رتبة S تمنحك صلاحيات خاصة في كل المجموعات</b>
"""
    keyboard = []
    
    if user_id == OWNER_ID or str(user_id) == str(OWNER_ID):
        keyboard.append([InlineKeyboardButton("👑 قائمة رتب 𝐒", callback_data="show_s_list")])
        keyboard.append([InlineKeyboardButton("📊 الإحصائيات", callback_data="show_stats")])
    elif await db.is_s_rank(user_id):
        keyboard.append([InlineKeyboardButton("⭐ صلاحيات رتبة 𝐒", callback_data="show_s_benefits")])
    
    if keyboard:
        await m.reply_text(
            rank_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True
        )
    else:
        await m.reply_text(rank_message, disable_web_page_preview=True)


@app.on_message(filters.command(["صلاحياتي", "my_s", "/mys"], "") & ~app.bl_users, group=803)
@lang.language()
@banned_check
async def my_benefits(_, m: types.Message):
    user_id = m.from_user.id
    if user_id == OWNER_ID or str(user_id) == str(OWNER_ID):
        await m.reply_text(
            f"<b>صلاحيات المطور الأساسي 👑\n\n"
            f"• مرحباً {m.from_user.mention}\n\n"
            f"• الامتيازات الكاملة:\n"
            f"• لتحكم الكامل بجميع إعدادات البوت\n"
            f"• إدارة المطورين (رفع تنزيل)\n"
            f"• إدارة رتبة 𝐒 (رفع تنزيل)\n"
            f"• الإذاعة لجميع المستخدمين والمجموعات\n"
            f"• تغيير إعدادات السورس\n"
            f"• الإحصائيات الكاملة للنظام\n"
            f"• حماية كاملة من الحظر\n"
            f"• جميع أوامر البوت متاحة لك</b>"
        )
        return
    
    # التحقق من رتبة S
    if not await db.is_s_rank(user_id):
        return await m.reply_text("هذا الأمر فقط لأعضاء رتبة S والمطور الأساسي!")
    
    await m.reply_text(
        f"<b>⭐ مزايا رتبة S ⭐\n\n"
        f"•  مرحباً {m.from_user.mention}\n\n"
        f"• الامتيازات الحصرية:\n"
        f"• ترحيب مميز في كل المجموعات\n"
        f"• استخدام أوامر التحكم بالبوت بدون صلاحيات\n"
        f"• حماية من العقوبات (باند كتم طرد)\n"
        f"• أوامر خاصة متاحة لك فقط\n"
        f"• إمكانية طرد وحظر المخالفين\n"
        f"• تنظيف الرسائل بسرعة\n\n"
        f"• ملاحظة: صلاحياتك تتبعك في كل المجموعات</b>"
    )


@app.on_message(filters.command(["/ups", "ترقيه s"], "") & ~app.bl_users, group=800)
@is_owner
async def give_s_rank(_, m: Message):
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(" المستخدم غير موجود!")    
    if user.id == (await app.get_me()).id:
        return await m.reply_text(" لا يمكن منح رتبة S للبوت نفسه!")
    
    if await db.is_s_rank(user.id):
        return await m.reply_text(f"• المستخدم {user.mention} لديه بالفعل رتبة S!")    
    await db.add_s_rank(user.id)
    await m.reply_text(
        f"<b>👑 تم منح رتبة 𝐒👑\n\n"
        f"•  المستخدم: {user.mention}\n"
        f"•  الايدي: <code>{user.id}</code>\n\n"
        f"•  يمكنه الآن استخدام صلاحيات البوت الخاصة في كل المجموعات</b>"
    )


# ============================================
# أمر سحب رتبة S (للمالك فقط)
# ============================================
@app.on_message(filters.command(["/dels", "سحب اس"], "") & ~app.bl_users, group=801)
@is_owner
async def take_s_rank(_, m: Message):
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text("المستخدم غير موجود!")
    
    if not await db.is_s_rank(user.id):
        return await m.reply_text(f"المستخدم {user.mention} ليس لديه رتبة S!")
    
    await db.rm_s_rank(user.id)
    await m.reply_text(
        f"<b>•  تم سحب رتبة 𝐒\n\n"
        f"•  المستخدم: {user.mention}\n"
        f"•  الايدي: <code>{user.id}</code></b>"
    )


# ============================================
# أمر عرض قائمة رتب S (للمالك والأدمن)
# ============================================
@app.on_message(filters.command(["s_list", "قائمة اس"], "") & ~app.bl_users, group=802)
async def s_rank_list(_, m: Message):
    # التحقق من المطور الأساسي أو المشرف
    if m.from_user.id != OWNER_ID and str(m.from_user.id) != str(OWNER_ID):
        if m.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            if not await is_admin(m.chat.id, m.from_user.id):
                return await m.reply_text("❌ هذا الأمر للمشرفين ومالك البوت فقط!")
        else:
            return await m.reply_text("❌ هذا الأمر للمشرفين ومالك البوت فقط!")
    
    s_ranks = await db.get_all_s_ranks()
    if not s_ranks:
        return await m.reply_text(" لا يوجد أعضاء برتبة S حالياً.")
    
    txt = f"👑 قائمة رتبة 𝐒👑\n\n📊 العدد: {len(s_ranks)}\n"
    for i, user_id in enumerate(s_ranks, start=1):
        try:
            user = await app.get_users(user_id)
            mention = user.mention if user.mention else user.first_name
            username = f"@{user.username}" if user.username else "لا يوجد معرف"
            txt += f"{i}. {mention}\n   └ 🆔 `{user_id}` | {username}\n\n"
        except:
            txt += f"{i}. <a href='tg://user?id={user_id}'>المستخدم</a>\n   └ 🆔 <code>{user_id}</code>\n\n"
    
    # إضافة زر لتحديث الكاش
    if m.from_user.id == OWNER_ID or str(m.from_user.id) == str(OWNER_ID):
        keyboard = [[InlineKeyboardButton("🔄 تحديث الكاش", callback_data="reload_s_ranks")]]
        await m.reply_text(txt, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await m.reply_text(txt, disable_web_page_preview=True)



@app.on_message(filters.command(["reload_s", "تحديث s"], "") & ~app.bl_users, group=804)
@is_owner
async def reload_s_rank_cache(_, m: Message):
    if m.from_user.id in s_rank_cooldown:
        if time.time() < s_rank_cooldown[m.from_user.id]:
            return await m.reply_text("⏳ يرجى الانتظار 5 دقائق قبل إعادة التحديث!")
    
    s_rank_cooldown[m.from_user.id] = time.time() + 300
    sent = await m.reply_text("🔄 جاري تحديث كاش رتبة S...")
    await db.load_s_ranks_cache()
    count = await db.get_s_ranks_count()
    await sent.edit_text(f"✅ تم التحديث!\n👑 عدد حاملي الرتبة: {count}")


# ============================================
# معالجة الأزرار (Callback Queries)
# ============================================
@app.on_callback_query(group=820)
async def s_rank_callbacks(client, callback_query):
    data = callback_query.data
    
    if data == "show_s_list":
        s_ranks = await db.get_all_s_ranks()
        if not s_ranks:
            await callback_query.answer("📭 لا يوجد أعضاء برتبة S حالياً", show_alert=True)
            return
        
        txt = f"👑 قائمة رتبة S 👑\n\n📊 العدد: {len(s_ranks)}\n"
        for i, user_id in enumerate(s_ranks, start=1):
            try:
                user = await app.get_users(user_id)
                mention = user.mention if user.mention else user.first_name
                txt += f"{i}. {mention}\n   └ 🆔 `{user_id}`\n\n"
            except:
                txt += f"{i}. <a href='tg://user?id={user_id}'>المستخدم</a>\n   └ 🆔 `{user_id}`\n\n"
        
        await callback_query.message.edit_text(txt, disable_web_page_preview=True)
        await callback_query.answer()
    
    elif data == "show_s_benefits":
        await callback_query.message.edit_text(
            f"<b>•  مزايا رتبة S ⭐\n\n"
            f"•  الامتيازات الحصرية:\n"
            f"• ترحيب مميز في كل المجموعات\n"
            f"• استخدام أوامر التحكم بالبوت بدون صلاحيات\n"
            f"• حماية من العقوبات (باند كتم طرد)\n"
            f"• أوامر خاصة متاحة لك فقط\n"
            f"• إمكانية طرد وحظر المخالفين\n"
            f"• تنظيف الرسائل بسرعة\n\n"
            f"• ملاحظة: صلاحياتك تتبعك في كل المجموعات</b>"
        )
        await callback_query.answer()
    
    elif data == "show_stats":
        users_count = len(await db.get_users())
        chats_count = len(await db.get_chats())
        s_ranks_count = await db.get_s_ranks_count()
        
        await callback_query.message.edit_text(
            f"• إحصائيات البوت 📊\n\n"
            f"• المستخدمين: {users_count}\n"
            f"• المجموعات: {chats_count}\n"
            f"•  رتبة S: {s_ranks_count}\n"
            f"• المطور: {len(app.sudoers)}\n\n"
            f"•  آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await callback_query.answer()
    
    elif data == "reload_s_ranks":
        await db.load_s_ranks_cache()
        count = await db.get_s_ranks_count()
        await callback_query.answer(f"✅ تم التحديث! عدد حاملي الرتبة: {count}", show_alert=True)
        await callback_query.message.delete()


# ============================================
# رسالة ترحيب مميزة لرتبة S
# ============================================
@app.on_chat_member_updated(group=805)
async def s_rank_welcome(client: Client, chat_member_updated):
    if chat_member_updated.new_chat_member and chat_member_updated.new_chat_member.status == ChatMemberStatus.MEMBER:
        user = chat_member_updated.new_chat_member.user
        
        if await db.is_s_rank(user.id):
            group_id = chat_member_updated.chat.id
            username = f"@{user.username}" if user.username else "لا يوجد معرف"
            cairo_tz = pytz.timezone('Africa/Cairo')
            cairo_time = datetime.now(cairo_tz).strftime("%Y-%m-%d %I:%M:%S %p")
            
            welcome_message = (
                f"⭐ ترحيب خاص برتبة S ⭐\n\n"
                f"☆ يتشرف المجموعة بانضمامك ☆\n"
                f"ɴᴧᴍᴇ ⌯ {user.mention()}\n"
                f"ᴜѕᴇꝛɴᴧᴍᴇ ⌯ {username}\n"
                f"ᴅᴀᴛᴇ ⌯ {cairo_time}\n\n"
                f"•  لديك صلاحيات خاصة في البوت ✨\n"
                f"•  استخدم `صلاحياتي` لعرض صلاحياتك"
            )
            
            keyboard = [[InlineKeyboardButton(text=user.first_name or "المستخدم", url=f"https://t.me/{user.username}")]] if user.username else None
            
            try:
                if keyboard:
                    await client.send_message(
                        chat_id=group_id,
                        text=welcome_message,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        disable_web_page_preview=True
                    )
                else:
                    await client.send_message(
                        chat_id=group_id,
                        text=welcome_message,
                        disable_web_page_preview=True
                    )
            except Exception as e:
                print(f"[S_RANK] خطأ في الترحيب: {e}")



@app.on_message(filters.command(["auth", "unauth"]) & filters.group & ~app.bl_users, group=809)
@lang.language()
@admin_check
async def _auth(_, m: types.Message):
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(m.lang["user_not_found"])

    if m.command[0] == "auth":
        if await is_admin(m.chat.id, user.id):
            return await m.reply_text(m.lang["auth_is_admin"])

        await db.add_auth(m.chat.id, user.id)
        await m.reply_text(m.lang["auth_added"].format(user.mention))
    else:
        await db.rm_auth(m.chat.id, user.id)
        await m.reply_text(m.lang["auth_removed"].format(user.mention))


# ============================================
# عرض قائمة المصادقة (authlist)
# ============================================
@app.on_message(filters.command(["authlist"]) & filters.group & ~app.bl_users, group=810)
@lang.language()
@admin_check
async def _authlist(_, m: types.Message):
    auth = await db._get_auth(m.chat.id)
    if not auth:
        return await m.reply_text(m.lang["auth_empty"])

    auth_txt = m.lang["auth_list"].format(m.chat.title)
    for i, user in enumerate(auth, start=1):
        auth_txt += f"\n{i}. <a href=tg://user?id={user}>{user}</a>"
    await m.reply_text(auth_txt)


# ============================================
# تحديث كاش الأدمن
# ============================================
@app.on_message(filters.command(["تحديث الادمن", "/reload"], "") & filters.group & ~app.bl_users, group=811)
@lang.language()
async def _admincache(_, m: types.Message):
    if m.from_user.id in rel_hist:
        if time.time() < rel_hist[m.from_user.id]:
            return await m.reply_text(m.lang["admin_cache_wait"])

    rel_hist[m.from_user.id] = time.time() + 600
    sent = await m.reply_text(m.lang["admin_cache_reloading"])
    await db.get_admins(m.chat.id, reload=True)
    await sent.edit_text(m.lang["admin_cache_reloaded"])




# ============================================
# رسالة ترحيب عند انضمام عضو جديد
# ============================================
@app.on_chat_member_updated(group=815)
async def tr1hib(client, chat_member_updated):
    if chat_member_updated.new_chat_member and chat_member_updated.new_chat_member.status == ChatMemberStatus.MEMBER:
        if await db.is_s_rank(chat_member_updated.new_chat_member.user.id):
            return
        
        group_id = chat_member_updated.chat.id
        user = chat_member_updated.new_chat_member.user
        user_mention = user.mention()
        username = f"@{user.username}" if user.username else "لا يوجد معرف"
        cairo_tz = pytz.timezone('Africa/Cairo')
        cairo_time = datetime.now(cairo_tz).strftime("%I:%M %p")
        if chat_member_updated.old_chat_member is None or chat_member_updated.old_chat_member.status == ChatMemberStatus.LEFT:
            welcome_message = (
                f"• لا تُسِئ اللفظ وإن ضَاق عليك الرَّد\n"
                f"• ɴᴧᴍᴇ ⌯ {user_mention}\n"
                f"• ᴜѕᴇꝛɴᴧᴍᴇ ⌯ {username}\n"
                f"• ᴅᴀᴛᴇ ⌯ {cairo_time}"
            )
            keyboard = [[InlineKeyboardButton(text=user.first_name, url=f"https://t.me/{user.username}")]] if user.username else None
            
            try:
                if keyboard:
                    await client.send_message(
                        chat_id=group_id,
                        text=welcome_message,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        disable_web_page_preview=True
                    )
                else:
                    await client.send_message(
                        chat_id=group_id,
                        text=welcome_message,
                        disable_web_page_preview=True
                    )
            except Exception as e:
                print(f"حدث خطأ في إرسال الترحيب: {str(e)}")


# ============================================
# رسالة مغادرة عند خروج عضو
# ============================================
@app.on_chat_member_updated(group=816)
async def tr1hibi(client, chat_member_updated):
    if chat_member_updated.old_chat_member and chat_member_updated.old_chat_member.status == ChatMemberStatus.MEMBER:
        if chat_member_updated.new_chat_member and chat_member_updated.new_chat_member.status == ChatMemberStatus.LEFT:
            group_id = chat_member_updated.chat.id
            user = chat_member_updated.new_chat_member.user
            user_mention = user.mention()
            username = f"@{user.username}" if user.username else "لا يوجد معرف"
            cairo_tz = pytz.timezone('Africa/Cairo')
            cairo_time = datetime.now(cairo_tz).strftime("%I:%M %p")  
            
            goodbye_message = (
                f"غادر المجموعة\n"
                f"ɴᴧᴍᴇ ⌯ {user_mention}\n"
                f"ᴜѕᴇꝛɴᴧᴍᴇ ⌯ {username}\n"
                f"ᴅᴀᴛᴇ ⌯ {cairo_time}"
            )
            
            keyboard = [[InlineKeyboardButton(text=user.first_name, url=f"https://t.me/{user.username}")]] if user.username else None
            
            try:
                if keyboard:
                    await client.send_message(
                        chat_id=group_id,
                        text=goodbye_message,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        disable_web_page_preview=True
                    )
                else:
                    await client.send_message(
                        chat_id=group_id,
                        text=goodbye_message,
                        disable_web_page_preview=True
                    )
            except Exception as e:
                print(f"حدث خطأ في إرسال رسالة المغادرة: {str(e)}")




@app.on_message(filters.video_chat_started, group=812)
async def call_started(client: Client, message: Message): 
    Startt = "<b>↵ تم بدء المكالمة الصوتية</b>"
    await message.reply_text(Startt)


@app.on_message(filters.video_chat_ended, group=813)
async def call_ended(client: Client, message): 
    Enddd = "<b>↵ تم إنهاء المكالمة الصوتية</b>"
    await message.reply_text(Enddd)


@app.on_message(filters.video_chat_members_invited, group=814)
async def members_invited(client: Client, message: Message): 
    text = f"<b>• قـام: {message.from_user.mention}\n• بـدعـوه : </b>"
    x = 0
    for user in message.video_chat_members_invited.users:
        try:
            text += f"<a href=\"tg://user?id={user.id}\">{user.first_name}</a> "
            x += 1
        except Exception:
            pass
    try:
        await message.reply_text(f"{text}")
    except Exception:
        pass





