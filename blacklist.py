# • ترخيص بواسطه : @TopVeGa
# • علامة تجارية : VEGA & Sound
# • حرية التعديل و النشر ©2015 - 2026


from datetime import datetime, timedelta
from pyrogram import filters, types, enums
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
from anony import app, config, db, lang
from anony.helpers.admins import is_owner, banned_check, is_admin, admin_check

# ========== دوال مساعدة ==========
async def extract_user(message: types.Message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    
    if len(message.command) > 1:
        user_input = message.command[1]
        try:
            user_id = int(user_input)
            return await app.get_users(user_id)
        except ValueError:
            try:
                return await app.get_users(user_input)
            except:
                return None
    return None




@app.on_message(filters.command(["تقيد", "/Res"], ""), group=728)
async def user_restrict(client, m: types.Message):
    if await db.is_s_rank(m.from_user.id):
        return await m.reply_text(" انت من رتبة S لا يمكن تطبيق الأوامر عليك")
    if m.reply_to_message and m.reply_to_message.from_user:
        target = m.reply_to_message.from_user.id
        user = await client.get_users(m.reply_to_message.from_user.id)
        user_id = target
    elif len(m.command) > 1:
        target = m.command[1].strip("@")
        try:
            if target.isdigit():
                target = int(target)
            user = await client.get_users(target)
            user_id = user.id
        except:
            await m.reply_text("لا يمكن العثور على المستخدم")
            return
    else:
        await m.reply_text("قم بالرد علي مستخدم او ارسال معرفه")
        return
    
    chat_member = await client.get_chat_member(m.chat.id, m.from_user.id)
    is_s_rank_user = await db.is_s_rank(m.from_user.id)
    
    if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == config.config.OWNER_ID or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text("هذا الامر يخص ❪ الادمن ورتبة S ❫ بس")
        return
    
    if user_id == m.from_user.id:
        await m.reply_text("هييه مايمديك تقيد نفسك ياورع!")
        return

    if await db.is_s_rank(user_id):
        await m.reply_text(" لا يمكنك تقيد عضو من رتبة S")
        return
    
    if user_id == 8368077406:
        await m.reply_text("هييه مايمديك تقيد فيجا ياورع!")
        return
    if user_id == 8165731842:
        await m.reply_text("هييه مايمديك تقيد رو ياورع!")
        return
    
    if user_id == config.OWNER_ID:
        await m.reply_text("هييه مايمديك تقيد مطوري ياورع!")
        return
    
    try:
        member = await m.chat.get_member(user_id)
        if member.status == ChatMemberStatus.OWNER:
            return await m.reply("هييه مايمديك تقيد مالك اساسي ياورع!")
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            return await m.reply("هييه مايمديك تقيد ادمن ياورع!")
    except Exception:
        pass
    
    # التحقق من أنه ليس مقيد بالفعل
    if await db.is_user_restricted(user_id, m.chat.id):
        return await m.reply_text(f"「 {user.mention} 」\nمقيد من قبل.\nㅤ")
    
    # تحديد صلاحية التقييد (منع الكتابة فقط)
    mute_permission = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=False,
    )
    
    try:
        await client.restrict_chat_member(
            chat_id=m.chat.id,
            user_id=user_id,
            permissions=mute_permission
        )
        
        # حفظ التقييد في قاعدة البيانات - إزالة until_date
        reason = "تم التقييد عن طريق الأمر تقيد"
        await db.add_restricted_user(user_id, m.chat.id, reason)
        
        await m.reply_text(f"「 {user.mention} 」\nقييدته\nㅤ")
    except Exception as e:
        await m.reply_text(f"❌ حدث خطأ: {e}")


@app.on_message(filters.command(["الغاء تقيد", "الغاء التقيد", "/delres"], ""), group=94)
async def user_unrestrict(client, m: types.Message):
    """رفع التقييد عن المستخدم"""
    
    # التحقق من رتبة S - لا يتم تطبيق الأمر عليهم
    if await db.is_s_rank(m.from_user.id):
        return await m.reply_text(" انت من رتبة S لا يمكن تطبيق الأوامر عليك")
    
    if m.reply_to_message and m.reply_to_message.from_user:
        target = m.reply_to_message.from_user.id
        user = await client.get_users(m.reply_to_message.from_user.id)
    elif len(m.command) > 1:
        target = m.command[1].strip("@")
        try:
            user = await client.get_users(target)
        except:
            await m.reply_text("لا يمكن العثور على المستخدم")
            return
    else:
        await m.reply_text("لا يمكن العثور على المستخدم")
        return
    
    # التحقق من صلاحيات المستخدم المنفذ للأمر
    chat_member = await client.get_chat_member(m.chat.id, m.from_user.id)
    
    is_s_rank_user = await db.is_s_rank(m.from_user.id)
    
    if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == config.OWNER_ID or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text("هذا الامر يخص ❪ الادمن ورتبة S ❫ بس")
        return
    
    # === بلوكات منع إلغاء التقييد ===
    
    # منع إلغاء تقييد النفس
    if user.id == m.from_user.id:
        await m.reply_text("هييه ما متقيده نفسك ياورع!")
        return
    
    # منع إلغاء تقييد رتبة S
    if await db.is_s_rank(user.id):
        await m.reply_text(" لا يمكنك التعامل مع عضو من رتبة S")
        return
    
    # منع إلغاء تقييد المطور
    if user.id == config.OWNER_ID:
        await m.reply_text("هييه ما متقيد مطوري ياورع!")
        return
    
    # التحقق من صلاحيات المستخدم المستهدف في المجموعة
    try:
        member = await m.chat.get_member(user.id)
        if member.status == ChatMemberStatus.OWNER:
            return await m.reply("هييه ما متقيد المالك الاساسي ياورع!")
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            return await m.reply("هييه ما متقيد الادمن ياورع!")
    except Exception:
        pass
    
    if not await db.is_user_restricted(user.id, m.chat.id):
        return await m.reply_text(f"「 {user.mention} 」\nهييه ما متقيد\nㅤ")
    
    # إعادة جميع الصلاحيات
    unmute_permissions = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=False,
    )
    
    try:
        await client.restrict_chat_member(
            chat_id=m.chat.id,
            user_id=user.id,
            permissions=unmute_permissions
        )
        
        await db.remove_restricted_user(user.id, m.chat.id)
        await m.reply_text(f"「 {user.mention} 」\nابشر الغيت تقيدته\nㅤ")
    except Exception as e:
        await m.reply_text(f"❌ حدث خطأ: {e}")



@app.on_message(filters.command(["المقيدين","/listres"], ""), group=4770)
async def restricted_users_list(_, m: types.Message):
    chat_member = await app.get_chat_member(m.chat.id, m.from_user.id)
    is_s_rank_user = await db.is_s_rank(m.from_user.id)
    
    if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text("هذا الامر يخص ❪ الادمن ورتبة S ❫ بس")
        return
    
    restricted_list = await db.get_restricted_users(m.chat.id)
    
    if not restricted_list:
        await m.reply_text("لا يوجد أعضاء مقيدين")
        return
    
    count = len(restricted_list)
    response = f"<u>قائمة المقيدين وعددهم :</u> {count}\n"
    
    for restricted_user in restricted_list:
        try:
            user_id = restricted_user["user_id"]
            user = await app.get_users(user_id)
            response += f"{user.mention}\n"
        except Exception:
            response += f"المستخدم {restricted_user['user_id']}\n"
    
    await m.reply_text(response)



@app.on_message(filters.command(["مسح المقيدين", "/delress"], ""), group=40)
async def clear_restricted_users(client, m: types.Message):
    get = await client.get_chat_member(m.chat.id, m.from_user.id)
    is_s_rank_user = await db.is_s_rank(m.from_user.id)
    
    if not (get.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == config.OWNER_ID or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text("هذا الامر يخص ❪ الادمن وفوق ❫ بس")
        return
    
    restricted_list = await db.get_restricted_users(m.chat.id)
    
    if not restricted_list:
        return await m.reply_text("لا يوجد أعضاء مقيدين")
    
    unmute_permissions = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=False,
    )
    
    count = 0
    for restricted_user in restricted_list:
        try:
            await client.restrict_chat_member(
                chat_id=m.chat.id,
                user_id=restricted_user["user_id"],
                permissions=unmute_permissions
            )
            await db.remove_restricted_user(restricted_user["user_id"], m.chat.id)
            count += 1
        except Exception:
            continue
    
    await m.reply_text(f"↢ مسحت {count} من المقيدين")



@app.on_message(filters.command(["كتم", "/mute"], ""), group=726262728)
async def mute_user(client, m: types.Message):
    
    if await db.is_s_rank(m.from_user.id):
        return await m.reply_text(" انت من رتبة S لا يمكن تطبيق الأوامر عليك")
    
    if m.reply_to_message and m.reply_to_message.from_user:
        user = m.reply_to_message.from_user
        user_id = user.id
        if user.is_bot:
            return await m.reply_text("مايمديك تكتم البوت ياورع!")
    elif len(m.command) > 2:
        target = m.command[2]
        try:
            user = await client.get_users(target)
            user_id = user.id
            if user.is_bot:
                return await m.reply_text("مايمديك تكتم البوت ياورع!")
        except:
            await m.reply_text("لا يمكن العثور على المستخدم")
            return
    elif len(m.command) > 1:
        target = m.command[1].strip("@")
        try:
            user = await client.get_users(target)
            user_id = user.id
            if user.is_bot:
                return await m.reply_text("مايمديك تكتم البوت ياورع!")
        except:
            await m.reply_text("لا يمكن العثور على المستخدم")
            return
    else:
        await m.reply_text("قم بالرد علي مستخدم او ارسال معرفه")
        return
    
    chat_member = await client.get_chat_member(m.chat.id, m.from_user.id)
    
    is_s_rank_user = await db.is_s_rank(m.from_user.id)
    
    if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == config.OWNER_ID or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text("هذا الامر يخص ❪ الادمن ورتبة S ❫ بس")
        return
    if user_id == m.from_user.id:
        await m.reply_text("هييه مايمديك تكتم نفسك ياورع!")
        return
    
    if await db.is_s_rank(user_id):
        await m.reply_text(" لا يمكنك كتم عضو من رتبة S")
        return
    
    if user_id == 8368077406:
        await m.reply_text("هييه مايمديك تكتم نظام ياورع!")
        return
    if user_id == 8165731842:
        await m.reply_text("هييه مايمديك تكتم رو ياورع!")
        return
    
    # منع كتم المطور
    if user_id == config.OWNER_ID:
        await m.reply_text("هييه مايمديك تكتم مطور ياورع!")
        return
    
    try:
        member = await m.chat.get_member(user_id)
        if member.status == ChatMemberStatus.OWNER:
            return await m.reply("هييه مايمديك تكتم مالك اساسي ياورع!")
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            return await m.reply("هييه مايمديك تكتم ادمن ياورع!")
    except Exception:
        pass
    
    if await db.is_user_muted(user_id, m.chat.id):
        return await m.reply_text(f"「 {user.mention} 」\n⇜مكتوم من قبل\nㅤ")
    
    reason = "تم الكتم عن طريق الأمر كتم"
    await db.add_muted_user(user_id, m.chat.id, reason)
    
    await m.reply_text(f"「 {user.mention} 」\n⇜كتمته\nㅤ")
    
            
@app.on_message(filters.group & ~filters.bot)
async def delete_muted_messages(client, message):
    if message.from_user:
        if await db.is_s_rank(message.from_user.id):
            return
        if await db.is_user_muted(message.from_user.id, message.chat.id):
            try:
                await message.delete()
            except:
                pass


@app.on_message(filters.command(["الغاء الكتم", "الغاء كتم", "/Unmute"], ""), group=2)
async def unmute_user(client, m: types.Message):
    if await db.is_s_rank(m.from_user.id):
        return await m.reply_text(" انت من رتبة S لا يمكن تطبيق الأوامر عليك")
    
    if m.reply_to_message:
        user = m.reply_to_message.from_user
    elif len(m.command) > 2:
        target = m.command[2]
        try:
            user = await client.get_users(target)
        except:
            await m.reply_text("لا يمكن العثور على المستخدم")
            return
    elif len(m.command) > 1:
        target = m.command[1].strip("@")
        try:
            user = await client.get_users(target)
        except:
            await m.reply_text("لا يمكن العثور على المستخدم")
            return
    else:
        await m.reply_text("لا يمكن العثور على المستخدم")
        return
    
    # التحقق من صلاحيات المستخدم المنفذ للأمر
    chat_member = await client.get_chat_member(m.chat.id, m.from_user.id)
    
    is_s_rank_user = await db.is_s_rank(m.from_user.id)
    
    if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == config.OWNER_ID or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text("هذا الامر يخص ❪ الادمن وفوق ❫ بس")
        return
    
    # التحقق من أنه مكتوم بالفعل
    if not await db.is_user_muted(user.id, m.chat.id):
        return await m.reply_text(f"「 {user.mention} 」\n⇜ولك مو مكتوم\nㅤ")
    
    # حذف المستخدم من قاعدة البيانات
    await db.remove_muted_user(user.id, m.chat.id)
    
    await m.reply_text(f"「 {user.mention} 」\n⇜ابشر الغيت كتمه\nㅤ")



@app.on_message(filters.command(["المكتومين", "/mutes"], ""), group=137762627)
async def muted_users_list(_, m: types.Message):
    chat_member = await app.get_chat_member(m.chat.id, m.from_user.id)
    is_s_rank_user = await db.is_s_rank(m.from_user.id)
    
    if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text("هذا الأمر يخص ❪ الأدمن وفوق ❫ بس")
        return
    
    muted_list = await db.get_muted_users(m.chat.id)
    
    if not muted_list:
        return await m.reply_text("لا يوجد مستخدمين مكتومينً")
    
    count = len(muted_list)
    response = f"<u>قائمة المكتومين وعددهم:</u> {count}\n"
    response += "..." * 15 + "\n"
    
    for i, muted_user in enumerate(muted_list, start=1):
        try:
            user_id = muted_user["user_id"]
            user = await app.get_users(user_id)
            mention = user.mention if user.mention else user.first_name
            response += f"{i}- {mention}\n"
        except Exception:
            response += f"{i}- المستخدم {muted_user['user_id']}\n"
    
    await m.reply_text(response)



@app.on_message(filters.command(["مسح المكتومين", "/delmutes"], ""), group=136)
async def clear_muted_users(client, m: types.Message):
    get = await client.get_chat_member(m.chat.id, m.from_user.id)
    is_s_rank_user = await db.is_s_rank(m.from_user.id)
    
    if not (get.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == config.OWNER_ID or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text("هذا الامر يخص ❪ الادمن وفوق ❫ بس")
        return
    
    muted_list = await db.get_muted_users(m.chat.id)
    
    if not muted_list:
        return await m.reply_text("⇜ مافيه مكتومين")
    
    count = 0
    for muted_user in muted_list:
        try:
            await db.remove_muted_user(muted_user["user_id"], m.chat.id)
            count += 1
        except Exception:
            continue
    
    await m.reply_text(f"مسحت {count} من المكتومين")



@app.on_message(filters.command(["حظر", "/ban"], "") & filters.group, group=726262728660)
async def ban_user_only(client, m: types.Message):
    if await db.is_s_rank(m.from_user.id):
        return await m.reply_text(" انت من رتبة S لا يمكن تطبيق الأوامر عليك")
    
    # استخراج المستخدم
    if m.reply_to_message and m.reply_to_message.from_user:
        user = m.reply_to_message.from_user
        user_id = user.id
        if user.is_bot:
            return await m.reply_text(" مايمديك تحظر البوت ياورع!")
    elif len(m.command) > 1:
        target = m.command[1].strip("@")
        try:
            if target.isdigit():
                target = int(target)
            user = await client.get_users(target)
            user_id = user.id
            if user.is_bot:
                return await m.reply_text(" مايمديك تحظر البوت ياورع!")
        except:
            await m.reply_text(" لا يمكن العثور على المستخدم")
            return
    else:
        await m.reply_text(" يجب الرد على المستخدم أو ذكر معرفه\nمثال: `.حظر @username`")
        return
    
    # التحقق من صلاحيات المستخدم المنفذ للأمر
    chat_member = await client.get_chat_member(m.chat.id, m.from_user.id)
    is_s_rank_user = await db.is_s_rank(m.from_user.id)
    
    if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == config.OWNER_ID or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text(" هذا الامر يخص ❪ الادمن ورتبة S ❫ بس")
        return
    
    # === منع حظر بعض المستخدمين ===
    
    # منع حظر النفس
    if user_id == m.from_user.id:
        await m.reply_text(" مايمديك تحظر نفسك ياورع!")
        return
    
    # منع حظر رتبة S
    if await db.is_s_rank(user_id):
        await m.reply_text(" لا يمكنك حظر عضو من رتبة S")
        return
    
    # منع حظر المطور
    if user_id == config.OWNER_ID:
        await m.reply_text(" مايمديك تحظر المطور ياورع!")
        return
    
    # منع حظر المستخدمين المحميين
    if user_id == 8368077406:
        await m.reply_text(" مايمديك تحظر فيجا ياورع!")
        return
    if user_id == 8165731842:
        await m.reply_text(" مايمديك تحظر رو ياورع!")
        return
    
    # التحقق من صلاحيات المستخدم المستهدف
    try:
        member = await m.chat.get_member(user_id)
        if member.status == ChatMemberStatus.OWNER:
            return await m.reply(" مايمديك تحظر المالك الاساسي ياورع!")
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            return await m.reply(" مايمديك تحظر مشرف!")
    except Exception:
        pass
    
    try:
        # حظر العضو من المجموعة
        await client.ban_chat_member(m.chat.id, user_id)
        await m.reply_text(f"{user.mention}\n• حظرته")
    except Exception as e:
        await m.reply_text(f"❌ حدث خطأ: {e}")


@app.on_message(filters.command(["الغاء حظر", "رفع الحظر", "/unban"], "") & filters.group, group=726262728661)
async def unban_user_only(client, m: types.Message):
    if m.reply_to_message and m.reply_to_message.from_user:
        user = m.reply_to_message.from_user
        user_id = user.id
    elif len(m.command) > 1:
        target = m.command[1].strip("@")
        try:
            if target.isdigit():
                target = int(target)
            user = await client.get_users(target)
            user_id = user.id
        except:
            await m.reply_text(" لا يمكن العثور على المستخدم")
            return
    else:
        await m.reply_text(" يجب الرد على المستخدم أو ذكر معرفه\nمثال: `.الغاء الحظر @username`")
        return
    
    # التحقق من صلاحيات المستخدم المنفذ
    chat_member = await client.get_chat_member(m.chat.id, m.from_user.id)
    is_s_rank_user = await db.is_s_rank(m.from_user.id)
    
    if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == config.OWNER_ID or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text(" هذا الامر يخص ❪ الادمن ورتبة S ❫ بس")
        return
    
    try:
        # رفع الحظر عن العضو
        await client.unban_chat_member(m.chat.id, user_id)
        await m.reply_text(f"{user.mention}\n• لغيت حظره")
    except Exception as e:
        await m.reply_text(f"❌ حدث خطأ: {e}")



@app.on_message(filters.command(["مسح المحظورين", "رفع الكل", "/delbans"], "") & filters.group, group=726262728662)
async def unban_all_users(client, m: types.Message):
    chat_member = await client.get_chat_member(m.chat.id, m.from_user.id)
    is_s_rank_user = await db.is_s_rank(m.from_user.id)
    
    if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == config.OWNER_ID or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text(" هذا الامر يخص ❪ الادمن ورتبة S ❫ بس")
        return
    
    try:
        # الحصول على قائمة المحظورين
        banned_users = []
        async for member in client.get_chat_members(m.chat.id, filter=ChatMembersFilter.BANNED):
            banned_users.append(member.user.id)
        
        if not banned_users:
            return await m.reply_text(" لا يوجد أعضاء محظورين في هذه المجموعة")
        
        count = 0
        for user_id in banned_users:
            try:
                await client.unban_chat_member(m.chat.id, user_id)
                count += 1
            except:
                continue
        
        await m.reply_text(f"• تم رفع الحظر عن {count} عضو بنجاح")
        
    except Exception as e:
        await m.reply_text(f"حدث خطأ: {e}")


@app.on_message(filters.command(["المحظورين", "قائمة المحظورين", "/listban"], "") & filters.group, group=726262728663)
async def banned_users_list_only(_, m: types.Message):
    chat_member = await _.get_chat_member(m.chat.id, m.from_user.id)
    is_s_rank_user = await db.is_s_rank(m.from_user.id)    
    if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            m.from_user.id == config.OWNER_ID or 
            m.from_user.id == 8368077406 or
            is_s_rank_user):
        await m.reply_text(" هذا الأمر يخص ❪ الأدمن ورتبة S وفوق ❫ بس")
        return
    
    try:
        banned_list = []
        async for member in _.get_chat_members(m.chat.id, filter=ChatMembersFilter.BANNED):
            banned_list.append(member.user)
        
        if not banned_list:
            return await m.reply_text(" لا يوجد أعضاء محظورين")
        
        count = len(banned_list)
        response = f"قائمة المحظورين\nالعدد: {count}\n\n"
        
        for i, user in enumerate(banned_list, start=1):
            mention = user.mention if user.mention else user.first_name
            user_id = user.id
            username = f"@{user.username}" if user.username else "لا يوجد معرف"
            response += f"{i}• {mention}\n• {username}\n\n"
        if len(response) > 4000:
            for x in range(0, len(response), 4000):
                await m.reply_text(response[x:x+4000])
        else:
            await m.reply_text(response)
            
    except Exception as e:
        await m.reply_text(f"❌ حدث خطأ: {e}")







@app.on_message(filters.command(["/block"], "") & ~filters.private, group=1120)
@is_owner
@lang.language()
async def user_block(_, m: types.Message):
    if not m.reply_to_message and len(m.command) < 2:
        return await m.reply_text(m.lang["general_1"])
    user = await extract_user(m)
    if not user:
        return await m.reply_text(m.lang["general_2"])
    if await db.is_user_banned(user.id):
        return await m.reply_text(m.lang["block_1"].format(user.mention if user.mention else user.first_name))
    reason = " ".join(m.command[2:]) if len(m.command) > 2 else "No reason provided"
    await db.add_banned_user(user.id, reason)
    await m.reply_text(m.lang["block_2"].format(user.mention if user.mention else user.first_name))


@app.on_message(filters.command(["/unblock"], "") & ~filters.private, group=1110)
@is_owner
@lang.language()
async def user_unblock(_, m: types.Message):
    if not m.reply_to_message and len(m.command) < 2:
        return await m.reply_text(m.lang["general_1"])
    user = await extract_user(m)
    if not user:
        return await m.reply_text(m.lang["general_2"])
    if not await db.is_user_banned(user.id):
        return await m.reply_text(m.lang["block_3"].format(user.mention if user.mention else user.first_name))
    await db.remove_banned_user(user.id)
    await m.reply_text(m.lang["block_4"].format(user.mention if user.mention else user.first_name))


@app.on_message(filters.command(["blocked", "blockedusers", "blusers"]) & ~filters.private, group=90901)
@is_owner
@lang.language()
async def blocked_users_list(_, m: types.Message):
    banned_users_list = await db.get_banned_users()   
    if not banned_users_list:
        return await m.reply_text(m.lang["block_5"])
    mystic = await m.reply_text(m.lang["block_6"])
    msg = m.lang["block_7"]
    count = 0
    for banned_user in banned_users_list:
        try:
            user_id = banned_user["user_id"]
            user = await app.get_users(user_id)
            mention = user.mention if user.mention else user.first_name
            count += 1
            reason = banned_user.get("reason", "No reason")
            msg += f"{count}➤ {mention}\n   └ سبب الحظر: {reason}\n"
        except:
            count += 1
            msg += f"{count}➤ المستخدم {banned_user['user_id']}\n   └ سبب الحظر: {banned_user.get('reason', 'No reason')}\n"
    return await mystic.edit_text(msg)        