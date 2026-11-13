# • ترخيص بواسطه : @TopVeGa
# • علامة تجارية : VEGA & Sound
# • حرية التعديل و النشر ©2015 - 2026

from pyrogram import Client, filters
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall
from pyrogram.raw.types import InputPeerChat, InputPeerChannel
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatPrivileges
from anony import app, db, lang, config
import pyrogram
import time
from datetime import datetime, timedelta
import pytz
import asyncio
from pyrogram import filters, types, Client, enums
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import PeerIdInvalid, UserNotParticipant, FloodWait
from anony import app, db, lang, config
from anony.helpers import admin_check, is_admin, utils
from anony.helpers.admins import is_owner, banned_check
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pytgcalls import PyTgCalls, types
from pytgcalls.exceptions import NoActiveGroupCall
from anony import app, db, config, userbot
import asyncio
import os
import aiohttp
import requests


cairo_timezone = pytz.timezone('Africa/Cairo')


prayer_stickers = {
    "الفجر": "CAACAgQAAyEFAATaodfYAAIMiGq1StMbeCnKQg7GOAa3ki8AAQdqgQACrh0AAonPQVH9wZgaar_fYB4E",
    "الظهر": "CAACAgQAAxkBAAEBXTpqtUr_I2Xyd7l91jAvz3xxdDEvLwACoyMAAuuaQFHNqlEhYcMDGx4E",
    "العصر": "CAACAgQAAxkBAAEBXT1qtUsRzUPCW7dpUAgsz3mXH7JphAACAx8AAoEBQVFWCuSsm76H9B4E",
    "المغرب": "CAACAgQAAxkBAAEBXUBqtUsldv6xcEYijaiijxZMVjHutwACbioAAsKAQFFEvsQ5yETPlB4E",
    "العشاء": "CAACAgQAAxkBAAEBXUNqtUs8Rv_GSvXMSjyUbjYq7rrL3wACmSIAAsi6QFGcx7Lqz6kjRB4E",
}

_played_prayers = {}
_azan_file_path = None


async def get_assistant(num: int = 1):
    if num == 1 and userbot.one:
        return userbot.one
    elif num == 2 and userbot.two:
        return userbot.two
    elif num == 3 and userbot.three:
        return userbot.three
    elif userbot.clients:
        return userbot.clients[0]
    return None


# ━━━ دالة تهيئة PyTgCalls ━━━
async def get_pytgcalls(chat_id: int):
    assistant = await db.get_assistant_userbot(chat_id) or await get_assistant(1)
    if not assistant:
        return None, None
    p = PyTgCalls(assistant, cache_duration=100)
    await p.start()
    return p, assistant


# ━━━ دالة جلب المكالمة ━━━
async def get_group_call(assistant_client, chat_id: int):
    try:
        if str(chat_id).startswith("-100"):
            peer = await assistant_client.resolve_peer(chat_id)
            full_chat = await assistant_client.invoke(
                pyrogram.raw.functions.channels.GetFullChannel(channel=peer)
            )
        else:
            peer = await assistant_client.resolve_peer(chat_id)
            full_chat = await assistant_client.invoke(
                pyrogram.raw.functions.messages.GetFullChat(chat_id=peer.chat_id)
            )
        
        call = getattr(full_chat.full_chat, 'call', None)
        if call:
            return call
        return None
    except Exception:
        return None


# ━━━ دالة ترقية المساعد ━━━
async def promote_assistant(client, chat_id):
    try:
        assistant_client = await db.get_assistant_userbot(chat_id)
        if not assistant_client:
            return None, "لا يوجد حساب مساعد لهذه المجموعة"
        assistant_info = await assistant_client.get_me()
        try:
            await db.join_assistant_to_channel(chat_id)
            await asyncio.sleep(2)
        except Exception as e:
            print(f"خطأ في انضمام المساعد: {e}")
        try:
            chat_member = await client.get_chat_member(chat_id, assistant_info.id)
            if chat_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return None, " لم يتمكن المساعد من الانضمام للمجموعة"
        except:
            return None, "لم يتمكن المساعد من الانضمام للمجموعة"

        await client.promote_chat_member(
            chat_id,
            assistant_info.id,
            privileges=ChatPrivileges(
                can_delete_messages=True,
                can_restrict_members=True,
                can_promote_members=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_video_chats=True
            )
        )
        
        return assistant_client, "✅ تم ترقية المساعد بنجاح"
        
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await promote_assistant(client, chat_id)
    except ChatAdminRequired:
        return None, "البوت ليس أدمن أو لا يملك صلاحية الترقية"
    except Exception as e:
        return None, f"فشل الترقية: {str(e)}"


async def demote_assistant(client, chat_id):
    try:
        assistant_client = await db.get_assistant_userbot(chat_id)
        if not assistant_client:
            return True
        
        assistant_info = await assistant_client.get_me()        
        await client.promote_chat_member(
            chat_id,
            assistant_info.id,
            privileges=ChatPrivileges(
                can_delete_messages=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_manage_video_chats=False
            )
        )
        return True
    except:
        return True


# ━━━ دالة فتح المكالمة تلقائياً ━━━
async def open_voice_chat_auto(chat_id: int):
    try:
        assistant_client = await db.get_assistant_userbot(chat_id)
        if not assistant_client:
            return False            
        existing_call = await get_group_call(assistant_client, chat_id)
        if existing_call:
            return True        
        try:
            peer = await assistant_client.resolve_peer(chat_id)
            
            if isinstance(peer, InputPeerChannel):
                await assistant_client.invoke(
                    CreateGroupCall(
                        peer=InputPeerChannel(
                            channel_id=peer.channel_id,
                            access_hash=peer.access_hash,
                        ),
                        random_id=assistant_client.rnd_id() // 9000000000,
                    )
                )
            elif isinstance(peer, InputPeerChat):
                await assistant_client.invoke(
                    CreateGroupCall(
                        peer=InputPeerChat(chat_id=peer.chat_id),
                        random_id=assistant_client.rnd_id() // 9000000000,
                    )
                )         
            await db.add_call(chat_id)
            return True
            
        except Exception as e:
            error_str = str(e)
            if "CHAT_ADMIN_REQUIRED" in error_str or "ADMIN" in error_str:
                assistant_client, result = await promote_assistant(app, chat_id)
                if assistant_client:
                    peer = await assistant_client.resolve_peer(chat_id)
                    if isinstance(peer, InputPeerChannel):
                        await assistant_client.invoke(
                            CreateGroupCall(
                                peer=InputPeerChannel(
                                    channel_id=peer.channel_id,
                                    access_hash=peer.access_hash,
                                ),
                                random_id=assistant_client.rnd_id() // 9000000000,
                            )
                        )
                    elif isinstance(peer, InputPeerChat):
                        await assistant_client.invoke(
                            CreateGroupCall(
                                peer=InputPeerChat(chat_id=peer.chat_id),
                                random_id=assistant_client.rnd_id() // 9000000000,
                            )
                        )
                    await db.add_call(chat_id)
                    return True
            return False
            
    except Exception:
        return False


# ━━━ دالة جلب ملف الأذان ━━━
async def get_azan_file():
    global _azan_file_path    
    if _azan_file_path and os.path.exists(_azan_file_path):
        return _azan_file_path    
    paths = ["./anony/helpers/azan.mp3"]    
    for path in paths:
        if os.path.exists(path):
            _azan_file_path = path
            return path    
    try:
        azan_file = "./anony/helpers/azan.mp3"
        os.makedirs(os.path.dirname(azan_file), exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://files.catbox.moe/azan.mp3", timeout=30) as resp:
                if resp.status == 200:
                    with open(azan_file, 'wb') as f:
                        f.write(await resp.read())
                    _azan_file_path = azan_file
                    return azan_file
    except Exception:
        pass    
    return None


# ━━━ دالة جلب وقت الصلاة ━━━
def get_prayer_time():
    try:
        response = requests.get(
            "http://api.aladhan.com/v1/timingsByAddress?address=Cairo&method=4&school=0",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        timings = data['data']['timings']        
        current_time = datetime.now(cairo_timezone)        
        prayer_map = {
            'Fajr': 'الفجر',
            'Dhuhr': 'الظهر',
            'Asr': 'العصر',
            'Maghrib': 'المغرب',
            'Isha': 'العشاء'
        }        
        for prayer_en, prayer_ar in prayer_map.items():
            if prayer_en in timings:
                prayer_time_str = timings[prayer_en][:5]
                prayer_hour, prayer_minute = map(int, prayer_time_str.split(':'))    
                prayer_datetime = current_time.replace(
                    hour=prayer_hour,
                    minute=prayer_minute,
                    second=0,
                    microsecond=0
                )                      
                time_diff = abs((current_time - prayer_datetime).total_seconds())                
                if time_diff <= 90:
                    return prayer_ar, prayer_time_str                   
    except Exception:
        pass    
    return None, None


# ━━━ دالة تشغيل الأذان في المجموعة ━━━
async def play_azan_in_chat(chat_id: int, prayer_name: str):
    try:    
        pytgcalls, assistant = await get_pytgcalls(chat_id)
        if not pytgcalls or not assistant:
            return False               
        existing_call = await get_group_call(assistant, chat_id)
        if not existing_call:
            opened = await open_voice_chat_auto(chat_id)
            if not opened:
                await pytgcalls.stop()
                return False
            await asyncio.sleep(3)           
        azan_file = await get_azan_file()
        if not azan_file:
            await pytgcalls.stop()
            return False             
        try:
            await pytgcalls.leave_call(chat_id)
            await asyncio.sleep(1)
        except:
            pass            
        stream = types.MediaStream(
            azan_file,
            audio_parameters=types.AudioQuality.STUDIO,
            video_parameters=types.VideoQuality.SD_360p,
            video_flags=types.MediaStream.Flags.IGNORE
        )           
        await pytgcalls.play(chat_id, stream)        
        # try:
            # message = f"<b>🕌 حان الآن وقت أذان {prayer_name} 🤍🍁</b>"
            # await app.send_message(chat_id, message)
        # except:
            # pass             
        if prayer_name in prayer_stickers:
            try:
                await app.send_sticker(chat_id, prayer_stickers[prayer_name])
            except:
                pass        
        await asyncio.sleep(190)
        try:
            await pytgcalls.leave_call(chat_id)
        except:
            pass        
        await pytgcalls.stop()
        await db.remove_call(chat_id)
        return True        
    except NoActiveGroupCall:
        opened = await open_voice_chat_auto(chat_id)
        if opened:
            await asyncio.sleep(2)
            return await play_azan_in_chat(chat_id, prayer_name)
        return False
    except Exception:
        return False


# ━━━ نظام الأذان التلقائي ━━━
async def azan_scheduler():       
    played_today = {}    
    while True:
        try:     
            prayer_name, prayer_time = get_prayer_time()            
            if prayer_name:
                today = datetime.now(cairo_timezone).strftime('%Y-%m-%d')
                key = f"{today}_{prayer_name}"                           
                if key not in played_today:        
                    chats_ids = await db.get_chats()                    
                    if chats_ids:
                        for chat_id in chats_ids:
                            try:
                                await play_azan_in_chat(chat_id, prayer_name)
                                await asyncio.sleep(5)
                            except Exception:
                                continue                    
                    played_today[key] = True                    
                    today_date = datetime.now(cairo_timezone).strftime('%Y-%m-%d')
                    for old_key in list(played_today.keys()):
                        if not old_key.startswith(today_date):
                            del played_today[old_key]            
            await asyncio.sleep(30)            
        except Exception:
            await asyncio.sleep(60)


# ━━━ أوامر فتح وإغلاق المكالمة ━━━
@app.on_message(filters.regex(r"^(افتح الكول|فتح الكول)$") & filters.group, group=900)
async def start_group_call(_, message):
    try:
        if not message.from_user:
            return await message.reply("ما أقدر أعرف مينك")
        
        chat_member = await app.get_chat_member(message.chat.id, message.from_user.id)
        is_s_rank_user = await db.is_s_rank(message.from_user.id)
        
        if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            message.from_user.id == config.OWNER_ID or 
            message.from_user.id == 8368077406 or
            is_s_rank_user):
            return await message.reply_text("هذا الامر يخص الادمن ورتبة S بس")
        
        chat_id = message.chat.id        
        assistant_client = await db.get_assistant_userbot(chat_id)        
        if not assistant_client:
            assistant_client, result = await promote_assistant(app, chat_id)
            if not assistant_client:
                return await message.reply(result)
        else:
            try:
                assistant_info = await assistant_client.get_me()
                chat_member = await app.get_chat_member(chat_id, assistant_info.id)
                if chat_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    assistant_client, result = await promote_assistant(app, chat_id)
                    if not assistant_client:
                        return await message.reply(result)
            except:
                assistant_client, result = await promote_assistant(app, chat_id)
                if not assistant_client:
                    return await message.reply(result)
        
        ass = await assistant_client.get_me()        
        existing_call = await get_group_call(assistant_client, chat_id)
        if existing_call:
            return await message.reply("المكالمة مفتوحة من قبل")        
        msg = await message.reply("جاري فتح المكالمة...")        
        try:
            peer = await assistant_client.resolve_peer(chat_id)
            
            if isinstance(peer, InputPeerChannel):
                await assistant_client.invoke(
                    CreateGroupCall(
                        peer=InputPeerChannel(
                            channel_id=peer.channel_id,
                            access_hash=peer.access_hash,
                        ),
                        random_id=assistant_client.rnd_id() // 9000000000,
                    )
                )
            elif isinstance(peer, InputPeerChat):
                await assistant_client.invoke(
                    CreateGroupCall(
                        peer=InputPeerChat(chat_id=peer.chat_id),
                        random_id=assistant_client.rnd_id() // 9000000000,
                    )
                )
            
            await msg.edit("تم فتح المكالمة بنجاح")
            
        except Exception as e:
            error_str = str(e)
            if "CHAT_ADMIN_REQUIRED" in error_str or "ADMIN" in error_str:
                try:
                    assistant_client, result = await promote_assistant(app, chat_id)
                    if assistant_client:
                        peer = await assistant_client.resolve_peer(chat_id)
                        if isinstance(peer, InputPeerChannel):
                            await assistant_client.invoke(
                                CreateGroupCall(
                                    peer=InputPeerChannel(
                                        channel_id=peer.channel_id,
                                        access_hash=peer.access_hash,
                                    ),
                                    random_id=assistant_client.rnd_id() // 9000000000,
                                )
                            )
                        elif isinstance(peer, InputPeerChat):
                            await assistant_client.invoke(
                                CreateGroupCall(
                                    peer=InputPeerChat(chat_id=peer.chat_id),
                                    random_id=assistant_client.rnd_id() // 9000000000,
                                )
                            )
                        
                        await msg.edit("تم فتح المكالمة بنجاح")
                    else:
                        await msg.edit("يحتاج الحساب المساعد صلاحية إدارة المكالمات")
                except Exception as e2:
                    await msg.edit("يحتاج الحساب المساعد صلاحية إدارة المكالمات")
            else:
                await msg.edit(f"خطأ: {error_str[:50]}")
                
    except Exception as e:
        await message.reply(f"حدث خطأ: {str(e)[:50]}")


@app.on_message(filters.regex(r"^(اقفل الكول|قفل الكول)$") & filters.group, group=9000)
async def stop_group_call(_, message):
    try:
        if not message.from_user:
            return await message.reply("ما أقدر أعرف مينك")
        
        chat_member = await app.get_chat_member(message.chat.id, message.from_user.id)
        is_s_rank_user = await db.is_s_rank(message.from_user.id)
        
        if not (chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or 
            message.from_user.id == config.OWNER_ID or 
            message.from_user.id == 8368077406 or
            is_s_rank_user):
            return await message.reply_text("هذا الامر يخص الادمن ورتبة S بس")
        
        chat_id = message.chat.id
        
        assistant_client = await db.get_assistant_userbot(chat_id)
        if not assistant_client:
            assistant_client, result = await promote_assistant(app, chat_id)
            if not assistant_client:
                return await message.reply(result)
        else:
            try:
                assistant_info = await assistant_client.get_me()
                chat_member = await app.get_chat_member(chat_id, assistant_info.id)
                if chat_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    assistant_client, result = await promote_assistant(app, chat_id)
                    if not assistant_client:
                        return await message.reply(result)
            except:
                assistant_client, result = await promote_assistant(app, chat_id)
                if not assistant_client:
                    return await message.reply(result)
        
        ass = await assistant_client.get_me()
        
        group_call = await get_group_call(assistant_client, chat_id)
        if not group_call:
            return await message.reply("مافي مكالمة شغالة")
        
        msg = await message.reply("جاري إغلاق المكالمة...")
        
        try:
            await assistant_client.invoke(DiscardGroupCall(call=group_call))
            await msg.edit("تم إغلاق المكالمة بنجاح")
            
        except Exception as e:
            error_str = str(e)
            if "GROUPCALL_FORBIDDEN" in error_str or "ADMIN" in error_str:
                try:
                    assistant_client, result = await promote_assistant(app, chat_id)
                    if assistant_client:
                        group_call = await get_group_call(assistant_client, chat_id)
                        if group_call:
                            await assistant_client.invoke(DiscardGroupCall(call=group_call))
                        await msg.edit("تم إغلاق المكالمة بنجاح")
                    else:
                        await msg.edit("يحتاج الحساب المساعد صلاحية إدارة المكالمات")
                except Exception:
                    await msg.edit("يحتاج الحساب المساعد صلاحية إدارة المكالمات")
            else:
                await msg.edit(f"خطأ: {error_str[:50]}")
                
    except Exception as e:
        await message.reply(f"حدث خطأ: {str(e)[:50]}")


# ━━━ أمر عرض المشاركين في المكالمة ━━━
@app.on_message(filters.regex("مين في الكول") & filters.group, group=817)
async def strcall(client: app, message: Message):
    cid = message.chat.id
    msg = await message.reply("👀")
    p = None
    try:
        p, a = await get_pytgcalls(cid)
        if not p or not a:
            await msg.edit("لا يوجد حساب مساعد متاح!")
            return
        is_playing = await db.get_call(cid)        
        if is_playing:
            try:
                parts = await p.get_participants(cid)
            except Exception:
                await msg.edit("فشل في جلب المشاركين")
                return
            
            if not parts:
                await msg.edit("لا يوجد أحد في المكالمة الصوتية حالياً!")
            else:
                t = f" <u><b>المستخدمين بالمحادثة  {len(parts)}:</b></u>\n\n"
                k = 0
                for pt in parts:
                    try:
                        m = "يتحدث" if not pt.muted else "صامت"
                        u = await client.get_users(pt.user_id)
                        k += 1
                        t += f"{k}- {u.mention} - {m}\n"
                    except Exception:
                        k += 1
                        t += f"{k}- مستخدم صامت\n"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("دفع 5⭐", url=f"https://t.me/{client.me.username}?start=call_{cid}")]
                ])
                await msg.edit(t, reply_markup=keyboard)
            return  
        af = "./anony/helpers/vgaa.mp3"
        if not os.path.exists(af):
            af = "./anony/helpers/vgaa.mp3"
            if not os.path.exists(af):
                af = "/tmp/silence.mp3"
                open(af, 'wb').write(b'\xFF\xFB\x90\x00\x00\x00\x00\x00')
        try:
            await p.play(cid, types.MediaStream(af, audio_parameters=types.AudioQuality.HIGH,
                                               video_parameters=types.VideoQuality.HD_720p,
                                               audio_flags=types.MediaStream.Flags.REQUIRED,
                                               video_flags=types.MediaStream.Flags.IGNORE),
                         types.GroupCallConfig(auto_start=False))
            await asyncio.sleep(2)
        except NoActiveGroupCall:
            await msg.edit("لا توجد محادثه صوتية مفتوحة!")
            return
        except Exception:
            try:
                await p.join_group_call(cid, af, stream_type=1)
                await asyncio.sleep(2)
            except Exception:
                await msg.edit("فشل الانضمام للمكالمة")
                return
        try:
            parts = await p.get_participants(cid)
        except Exception:
            await msg.edit("فشل في جلب المشاركين")
            return
        if not parts:
            await msg.edit("لا يوجد أحد في المكالمة الصوتية حالياً!")
        else:
            t = f" <u><b>المستخدمين بالمحادثة  {len(parts)}:</b></u>\n\n"
            k = 0
            for pt in parts:
                try:
                    m = "يتحدث" if not pt.muted else "صامت"
                    u = await client.get_users(pt.user_id)
                    k += 1
                    t += f"{k}- {u.mention} - {m}\n"
                except Exception:
                    k += 1
                    t += f"{k}- مستخدم صامت\n"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("دفع 5⭐", url=f"https://t.me/{client.me.username}?start=call_{cid}")]
            ])
            await msg.edit(t, reply_markup=keyboard)
        try:
            await asyncio.sleep(3)
            await p.leave_call(cid, close=False)
        except Exception:
            pass
    except NoActiveGroupCall:
        await msg.edit("• تنويه : قم بفتح محادثه صوتيه اولا")
    except Exception as e:
        await msg.edit(f" حدث خطأ: {str(e)[:50]}")
    finally:
        if p:
            try:
                await p.stop()
            except Exception:
                pass


# ━━━ دالة تشغيل نظام الأذان ━━━
async def start_azan():
    try:
        task = asyncio.create_task(azan_scheduler())
        from anony import tasks
        tasks.append(task)
        return True
    except Exception as e:
        print(f"⚠️ فشل في تشغيل نظام الأذان: {e}")
        return False