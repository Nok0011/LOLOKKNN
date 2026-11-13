# • ترخيص بواسطه : @TopVeGa
# • علامة تجارية : VEGA & Sound
# • حرية التعديل و النشر ©2015 - 2026


import random
import string
import json
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import os
import random
from datetime import datetime
from pytz import timezone
from pyrogram import Client, filters, enums
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
from anony import app, db, lang, config


BANK_NAME = "بنك فيجا"
CURRENCY = "ريال"
BANK_OWNER = 7654641648


# متغيرات التوقيت
SALARY_COOLDOWN = 20 * 60  # 20 دقيقة
TIP_COOLDOWN = 10 * 60  # 10 دقائق
STEAL_COOLDOWN = 10 * 60  # 10 دقائق
INVEST_COOLDOWN = 30 * 60  # 30 دقيقة
LUCK_COOLDOWN = 15 * 60  # 15 دقيقة
TREASURE_COOLDOWN = 6 * 60 * 60
WHEEL_COOLDOWN = 4 * 60 * 60  # 4 ساعات
PROTECTION_COOLDOWN = 60 * 60  # 60 دقيقة
CODE_COOLDOWN = 24 * 60 * 60  # 24 ساعة لكل كود
MAX_ACTIVE_CODES = 100  # الحد الأقصى للأكواد النشطة

# دوال مساعدة لنظام الأكواد
def generate_random_code(length=10):
    """إنشاء كود عشوائي"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def load_codes_data():
    """تحميل بيانات الأكواد"""
    try:
        with open('codes_data.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            'active_codes': {},
            'used_codes': {}
        }

def save_codes_data(data):
    """حفظ بيانات الأكواد"""
    with open('codes_data.json', 'w') as f:
        json.dump(data, f, indent=4)

def generate_new_codes(count=10):
    """إنشاء أكواد جديدة"""
    codes_data = load_codes_data()
    
    # تنظيف الأكواد المنتهية
    current_time = int(time.time())
    for code in list(codes_data['active_codes'].keys()):
        if codes_data['active_codes'][code]['expires_at'] < current_time:
            del codes_data['active_codes'][code]
    
    # إنشاء أكواد جديدة
    new_codes = []
    for _ in range(count):
        code = generate_random_code()
        reward = random.choice([
            random.randint(500, 1000),
            random.randint(1000, 2000),
            random.randint(2000, 5000),
            random.randint(5000, 10000)
        ])
        
        codes_data['active_codes'][code] = {
            'reward': reward,
            'created_at': current_time,
            'expires_at': current_time + (24 * 60 * 60),
            'used': False
        }
        new_codes.append((code, reward))
    
    save_codes_data(codes_data)
    return new_codes

def load_data():
    try:
        with open('bank_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            'accounts': {},
            'transactions': [],
            'thieves': {},
            'cooldowns': {},
            'protected': {},
            'treasure': 1000000
        }

def save_data(data):
    with open('bank_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# دوال المساعدة
def format_money(amount):
    return f"{amount:,} {CURRENCY}"

def get_account(user_id):
    data = load_data()
    return data['accounts'].get(str(user_id))

def update_account(user_id, account):
    data = load_data()
    data['accounts'][str(user_id)] = account
    save_data(data)

def check_cooldown(user_id, action):
    data = load_data()
    cooldowns = data.get('cooldowns', {})
    last_time = cooldowns.get(f"{user_id}_{action}", 0)
    remaining = max(0, (last_time + globals()[f"{action.upper()}_COOLDOWN"]) - int(time.time()))
    return remaining

def update_cooldown(user_id, action):
    data = load_data()
    data['cooldowns'][f"{user_id}_{action}"] = int(time.time())
    save_data(data)

# أوامر المطور












last_added = {}

@app.on_message(filters.command("اضف فلوس", "") & filters.user(BANK_OWNER), group=588)
async def add_money(client, message):
    try:
        user_id = BANK_OWNER
        current_time = datetime.now()
        last_time = last_added.get(user_id)
        
        if last_time and (current_time - last_time) < timedelta(hours=12):
            remaining_time = timedelta(hours=12) - (current_time - last_time)
            hours = remaining_time.seconds // 3600
            minutes = (remaining_time.seconds % 3600) // 60
            await message.reply(f"⏳ يمكنك استخدام هذه الميزة مرة كل 12 ساعة!\nالوقت المتبقي: {hours} ساعة و {minutes} دقيقة")
            return
        
        # تعيين المبلغ التلقائي (مليون ريال)
        amount = 1000000
        
        # تحميل البيانات ومعالجة الإضافة
        data = load_data()
        if str(user_id) not in data['accounts']:
            await message.reply("⚠️ ليس لديك حساب بنكي! يرجى إنشاء حساب أولاً")
            return
        
        # حفظ الرصيد القديم
        old_balance = data['accounts'][str(user_id)]['balance']
        bank_type = data['accounts'][str(user_id)]['bank']
        
        # إضافة المبلغ الجديد
        data['accounts'][str(user_id)]['balance'] += amount
        new_balance = data['accounts'][str(user_id)]['balance']
        save_data(data)
        
        # تحديث وقت آخر إضافة
        last_added[user_id] = current_time
        
        # جلب معلومات المستخدم
        try:
            user = await client.get_users(user_id)
            user_name = user.first_name
            user_mention = f"<a href='tg://user?id={user_id}'>{user_name}</a>"
        except:
            user_name = "المدير"
            user_mention = "المدير"
        
        # جلب معلومات البنك
        bank_info = BANKS.get(bank_type, {})
        bank_name = bank_info.get('name', 'بنك غير معروف')
        bank_emoji = bank_info.get('emoji', '🏦')
        
        # إعداد رسالة التفاصيل
        response = (
            f"💰 <b>إضافة تلقائية لرصيد المدير</b>\n\n"
            f"⇝ المستخدم: {user_mention}\n"
            f"⇝ نوع البنك: {bank_emoji} {bank_name}\n"
            f"⇝ المبلغ المضاف: <b>({format_money(amount)})</b>💰 \n\n"
            f"⇝ الرصيد السابق: <b>({format_money(old_balance)})</b>💵\n"
            f"⇝ الرصيد الجديد: <b>({format_money(new_balance)})</b>💸\n\n"
            f" تمت الإضافة التلقائية بنجاح\n"
        )
        
        await message.reply(response, parse_mode=enums.ParseMode.HTML)
        
    except Exception as e:
        print(f"Error in add_money: {e}")
        await message.reply("❌ حدث خطأ أثناء محاولة إضافة الرصيد!")



@app.on_message(filters.command("حذف حسابه", "") & filters.user(BANK_OWNER), group=5688)
async def delete_account(client, message):
    if not message.reply_to_message:
        await message.reply("⇜ رد على الشخص عشان تحذف حسابه")
        return
    
    user_id = message.reply_to_message.from_user.id
    data = load_data()
    
    if str(user_id) not in data['accounts']:
        await message.reply("⇜ ماعنده حساب أساساً!")
        return
    
    del data['accounts'][str(user_id)]
    save_data(data)
    
    await message.reply("⇜ تم ⇜ حذفت حسابه")

@app.on_message(filters.command("تصفير البنك", "") & filters.user(BANK_OWNER), group=5577)
async def reset_bank(client, message):
    data = {
        'accounts': {},
        'transactions': [],
        'thieves': {},
        'cooldowns': {},
        'protected': {},
        'treasure': 1000000
    }
    save_data(data)
    
    await message.reply("⇜ تم ⇜ سويت تصفير للبنك كله")

# تعريف البنوك المتاحة
BANKS = {
    "الاهلي": {
        "name": "بنك الاهلي",
        "emoji": "🏦",
        "min_balance": 1000,
        "visa_fee": 50
    },
    "بلو_سكاي": {
        "name": "بنك بلو سكاي",
        "emoji": "🏛️",
        "min_balance": 2000,
        "visa_fee": 100
    },
    "كريديت": {
        "name": "بنك كريديت",
        "emoji": "🏬",
        "min_balance": 5000,
        "visa_fee": 200
    }
}

# إنشاء حساب بنكي
@app.on_message(filters.regex("^انشاء حساب بنكي$"), group=67899)
async def create_account(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    data = load_data()
    
    if str(user_id) in data['accounts']:
        await message.reply("⇜ عندك حساب بنكي خلاص!")
        return
    
    # عرض خيارات البنوك
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{BANKS['الاهلي']['emoji']} {BANKS['الاهلي']['name']}", callback_data="bank_الاهلي"),
            InlineKeyboardButton(f"{BANKS['بلو_سكاي']['emoji']} {BANKS['بلو_سكاي']['name']}", callback_data="bank_بلو_سكاي")
        ],
        [
            InlineKeyboardButton(f"{BANKS['كريديت']['emoji']} {BANKS['كريديت']['name']}", callback_data="bank_كريديت")
        ]
    ])
    
    await message.reply(
        f"⇜ أهلًا {user_name}\n⇜ اختر البنك اللي تبيه:\n\n"
        "🏦 بنك الاهلي\n"
        "🏬 بنك بلو سكاي\n"
        "💳 بنك كريديت\n\n"
        "⇜ اضغط على اسم البنك اللي تبيه:\n"
        "⇜ استخدم امر `بنك` معرفتة الاوامر",
        reply_markup=keyboard
    )


@app.on_callback_query(filters.regex(r"^bank_(.*)$"), group=59980088)
async def handle_bank_selection(client, callback_query):
    bank_key = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name    
    if bank_key not in BANKS:
        await callback_query.answer("⇜ هذا البنك مو متوفر")
        return    
    bank = BANKS[bank_key]
    account_number = str(random.randint(1000000000, 9999999999))
    visa_number = f"4{random.randint(100000000000000, 999999999999999)}"
    
    data = load_data()
    data['accounts'][str(user_id)] = {
        'bank': bank_key,
        'account_number': account_number,
        'balance': bank['min_balance'],
        'visa': {
            'number': visa_number,
            'expiry': f"{random.randint(1, 12):02d}/{random.randint(23, 30)}",
            'cvv': f"{random.randint(100, 999)}"
        },
        'created_at': int(time.time()),
        'user_name': user_name
    }
    save_data(data)    
    await callback_query.message.edit_text(
        f"⇜ تم ⇜ سويت لك حساب في {bank['name']} {user_name}!\n\n"
        f"⇜ اسمك: {user_name}\n"
        f"⇜ رقم الحساب: `{account_number}`\n"
        f"⇜ رصيدك الأولي: {bank['min_balance']} ريال 💸\n\n"
        f"💳 **فيزا:**\n"
        f"⇜ رقمها: `{visa_number}`\n"
        f"⇜ تاريخ الانتهاء: {data['accounts'][str(user_id)]['visa']['expiry']}\n"
        f"⇜ السري: {data['accounts'][str(user_id)]['visa']['cvv']}\n\n"
        f"⇜ استخدم `حسابي` عشان تشوف معلومات حسابك"
    )


@app.on_message(filters.command("حسابي", ""), group=59009)
async def my_account(client, message):
    user_id = message.from_user.id
    data = load_data()
    
    if str(user_id) not in data['accounts']:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك` عشان تسوي حساب")
        return
    account = data['accounts'][str(user_id)]
    bank = BANKS[account['bank']]    
    await message.reply(
        f"💼 **معلومات حسابك في {bank['name']}**\n\n"
        f"⇜ رقم الحساب: `{account['account_number']}`\n"
        f"⇜ رصيدك: **({account['balance']})**ريال 💸\n\n"
        f"💳 **فيزا:**\n"
        f"⇜ رقمها: `{account['visa']['number']}`\n"
        f"⇜ تنتهي: {account['visa']['expiry']}\n"
        f"⇜ السري: {account['visa']['cvv']}\n\n"
        f"⇜ أنشئت: {time.strftime('%Y-%m-%d', time.localtime(account['created_at']))}"
    )

@app.on_message(filters.command("حذف حسابي", ""), group=54433)
async def delete_my_account(client, message):
    user_id = message.from_user.id
    data = load_data()
    
    if str(user_id) not in data['accounts']:
        await message.reply("⇜ ماعندك حساب أساساً!")
        return    
    del data['accounts'][str(user_id)]
    save_data(data)    
    await message.reply("⇜ تم ⇜ حذفت حسابك")



@app.on_message(filters.command(["فلوسي", "رصيدي"], ""), group=5433)
async def my_balance(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return    
    await message.reply(f"⇜ فلوسك الحالية: **({format_money(account['balance'])})** 💸")

@app.on_message(filters.command(["فلوسه", "رصيده"], ""), group=53223)
async def user_balance(client, message):
    if not message.reply_to_message:
        await message.reply("⇜ رد على الشخص عشان تشوف رصيده")
        return    
    user_id = message.reply_to_message.from_user.id
    account = get_account(user_id)    
    if not account:
        await message.reply("⇜ ماعنده حساب!")
        return    
    await message.reply(f"⇜ فلوسه: **({format_money(account['balance'])})** 💸")



@app.on_message(filters.command("تحويل", ""), group=5578)
async def transfer(client, message):
    user_id = message.from_user.id
    sender_account = get_account(user_id)
    
    if not sender_account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return    
    try:
        _, account_number, amount = message.text.split()
        amount = int(amount)
    except:
        await message.reply("⇜ استخدمها كذا:\nتحويل رقم الحساب المبلغ")
        return    
    if amount <= 0:
        await message.reply("⇜ المبلغ لازم يكون أكثر من صفر")
        return    
    if sender_account['balance'] < amount:
        await message.reply(f"⇜ فلوسك ماتكفي! عندك: {format_money(sender_account['balance'])}")
        return
    
    data = load_data()
    receiver_id = None
    
    for uid, acc in data['accounts'].items():
        if str(acc['account_number']) == account_number:
            receiver_id = uid
            break
    
    if not receiver_id:
        await message.reply("⇜ رقم الحساب غلط!")
        return    
    if int(receiver_id) == user_id:
        await message.reply("⇜ ماتقدر تحول لنفسك!")
        return
    data['accounts'][str(user_id)]['balance'] -= amount
    data['accounts'][receiver_id]['balance'] += amount    
    data['transactions'].append({
        'from': user_id,
        'to': int(receiver_id),
        'amount': amount,
        'time': int(time.time())
    })    
    save_data(data)    
    await message.reply(
        f"⇜ تم ⇜ سويت تحويل!\n"
        f"⇜ المبلغ: **({format_money(amount)})**💰\n"
        f"⇜ للحساب: {account_number}\n\n"
        f"⇜ رصيدك الجديد: {format_money(data['accounts'][str(user_id)]['balance'])} 💸"
    )


JOBS = {
    "حداد": {"رمز": "🔨", "راتب": (1000, 2000)},
    "طبيب": {"رمز": "🩺", "راتب": (2000, 3000)},
    "مهندس": {"رمز": "📐", "راتب": (1500, 2500)},
    "مبرمج": {"رمز": "💻", "راتب": (1700, 2700)},
    "طباخ": {"رمز": "👨‍🍳", "راتب": (800, 1500)},
    "سائق": {"رمز": "🚗", "راتب": (700, 1200)},
    "نجار": {"رمز": "🪵", "راتب": (900, 1800)},
    "شرطي": {"رمز": "👮", "راتب": (1200, 2200)},
    "معلم": {"رمز": "📚", "راتب": (1100, 2100)},
    "فلاح": {"رمز": "🌾", "راتب": (600, 1300)}
}


@app.on_message(filters.command("راتب", ""), group=50988)
async def salary(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    account = get_account(user_id)    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `انشاء` لإنشاء حساب")
        return    
    remaining = check_cooldown(user_id, 'salary')
    if remaining > 0:
        mins, secs = divmod(remaining, 60)
        await message.reply(f"⇜ مايمديك تاخذ راتب الحين!\n⇜ تعال بعد {mins} دقائق و {secs} ثانية")
        return
    job_name, job_info = random.choice(list(JOBS.items()))
    salary_amount = random.randint(job_info["راتب"][0], job_info["راتب"][1])
    data = load_data()
    old_balance = data['accounts'][str(user_id)]['balance']
    data['accounts'][str(user_id)]['balance'] += salary_amount
    new_balance = old_balance + salary_amount
    save_data(data)
    update_cooldown(user_id, 'salary')
    user_mention = f"<a href='tg://user?id={user_id}'>{user_name}</a>"
    
    await message.reply(
        f"اشعار ايداع | {user_mention}\n\n"
        f"المبلغ: <b>({format_money(salary_amount)})</b>ريال\n"
        f"وظيفتك: {job_name} {job_info['رمز']}\n"
        f"نوع العملية: اضافة راتب\n"
        f"رصيدك الحين: <b>({format_money(new_balance)})</b> ريال 💸",
        parse_mode=enums.ParseMode.HTML
    )
    
    
@app.on_message(filters.command("بخشيش", ""), group=554330)
async def tip(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    remaining = check_cooldown(user_id, 'tip')
    if remaining > 0:
        mins = remaining // 60
        await message.reply(f"⇜ مايمدي اعطيك بخشيش الحين ! \n⇜ تعال بعد {mins}  دقائق و 48 ثانية")
        return
    
    tip_amount = random.randint(100, 500)
    data = load_data()
    data['accounts'][str(user_id)]['balance'] += tip_amount
    save_data(data)
    update_cooldown(user_id, 'tip')
    
    await message.reply(
        f"⇜ خلاص ⇜ جاك بخشيش!\n"
        f"⇜ المبلغ: **({format_money(tip_amount)})**💰\n"
        f"⇜ رصيدك الحين: **({format_money(data['accounts'][str(user_id)]['balance'])})**💸 "
    )

@app.on_message(filters.command(["زرف", "سرقه", "اسرق"], ""), group=53456)
async def steal(client, message):
    user_id = message.from_user.id
    thief_account = get_account(user_id)
    
    if not thief_account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    remaining = check_cooldown(user_id, 'steal')
    if remaining > 0:
        mins = remaining // 60
        await message.reply(f"⇜ مايمدي اعطيك تسرق الحين ! \n⇜ تعال بعد {mins}  دقائق و 48 ثانية")
        return
    
    if not message.reply_to_message:
        await message.reply("⇜ رد على الشخص اللي تبيه تسرقه!")
        return
    
    victim_id = message.reply_to_message.from_user.id
    if victim_id == user_id:
        await message.reply("⇜ ماتقدر تسرق نفسك!")
        return
    
    victim_account = get_account(victim_id)
    if not victim_account:
        await message.reply("⇜ ماعنده حساب أساساً!")
        return
    
    if victim_account.get('protected', False):
        await message.reply("⇜ عنده حماية موقفة السرقة!")
        return
    
    if victim_account['balance'] < 100:
        await message.reply("⇜ الفلوس اللي عنده ماتسوى!")
        return
    
    steal_amount = random.randint(50, min(500, victim_account['balance']))
    
    if random.random() > 0.5:
        data = load_data()
        data['accounts'][str(user_id)]['balance'] += steal_amount
        data['accounts'][str(victim_id)]['balance'] -= steal_amount
        
        if str(user_id) not in data['thieves']:
            data['thieves'][str(user_id)] = 0
        data['thieves'][str(user_id)] += steal_amount
        
        save_data(data)
        update_cooldown(user_id, 'steal')
        
        await message.reply(
            f"⇜ خلاص ⇜ سرقت منه!\n"
            f"⇜ المبلغ: **({format_money(steal_amount)})**💰\n"
            f"⇜ رصيدك الحين: **({format_money(data['accounts'][str(user_id)]['balance'])})**💸 "
        )
    else:
        update_cooldown(user_id, 'steal')
        await message.reply("⇜ خسرت ⇜ مسكوك بالسرقة! ماجاك شيء")

@app.on_message(filters.command("استثمار", ""), group=5333)
async def invest(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    remaining = check_cooldown(user_id, 'invest')
    if remaining > 0:
        mins = remaining // 60
        await message.reply(f"⇜ مايمدي اعطيك تستثمر الحين ! \n⇜ تعال بعد {mins} دقائق و 48 ثاني")
        return
    
    try:
        _, amount = message.text.split()
        amount = int(amount)
    except:
        await message.reply("⇜ استخدمها كذا:\nاستثمار المبلغ")
        return
    
    if amount <= 0:
        await message.reply("⇜ المبلغ لازم يكون أكثر من صفر")
        return
    
    if account['balance'] < amount:
        await message.reply(f"⇜ فلوسك ماتكفي! عندك: {format_money(account['balance'])}")
        return
    
    # حساب نسبة الربح العشوائية بين -20% إلى 50%
    profit_percent = random.randint(-10, 20)
    profit_amount = int(amount * profit_percent / 100)
    
    data = load_data()
    data['accounts'][str(user_id)]['balance'] += profit_amount
    save_data(data)
    update_cooldown(user_id, 'invest')
    
    if profit_amount >= 0:
        await message.reply(
            f"⇜ استثمار ناجح!\n"
            f"⇜ نسبة الربح ↢ {profit_percent}%\n"
            f"⇜ مبلغ الربح ↢ ({format_money(profit_amount)} )\n"
            f"⇜ فلوسك صارت ↢ ({format_money(data['accounts'][str(user_id)]['balance'])} 💸 )"
        )
    else:
        await message.reply(
            f"⇜ استثمار خاسر!\n"
            f"⇜ نسبة الخسارة ↢ **({abs(profit_percent)}%)**\n"
            f"⇜ مبلغ الخسارة ↢ ({format_money(abs(profit_amount))} )\n"
            f"⇜ فلوسك صارت ↢ ({format_money(data['accounts'][str(user_id)]['balance'])} 💸 )"
        )


STOCK_TYPES = {
    "نفط": {"رمز": "🛢️", "تقلب": 15, "وصف": "شركات النفط والغاز"},
    "مجوهرات": {"رمز": "💎", "تقلب": 10, "وصف": "المجوهرات والأحجار الكريمة"},
    "ماس": {"رمز": "💠", "تقلب": 12, "وصف": "تجارة الماس العالمي"},
    "ساعات": {"رمز": "⌚", "تقلب": 8, "وصف": "شركات الساعات الفاخرة"},
    "اجهزة": {"رمز": "💻", "تقلب": 20, "وصف": "شركات الإلكترونيات"},
    "مباني": {"رمز": "🏢", "تقلب": 5, "وصف": "شركات المقاولات والعقارات"},
    "طائرات": {"رمز": "✈️", "تقلب": 18, "وصف": "شركات الطيران والفضاء"},
    "سفن": {"رمز": "🛳️", "تقلب": 12, "وصف": "شركات الشحن والنقل البحري"},
    "انفيديا": {"رمز": "🎮", "تقلب": 25, "وصف": "شركة إنفيديا للتكنولوجيا"},
    "ميكروسوفت": {"رمز": "🖥️", "تقلب": 15, "وصف": "شركة مايكروسوفت"},
    "ابل": {"رمز": "📱", "تقلب": 18, "وصف": "شركة آبل"},
    "ذهب": {"رمز": "🥇", "تقلب": 7, "وصف": "تجارة الذهب العالمي"},
    "فضة": {"رمز": "🥈", "تقلب": 5, "وصف": "تجارة الفضة العالمي"}
}

@app.on_message(filters.command("شراء سهم", ""), group=5336)
async def buy_stock(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `انشاء` عشان تسوي حساب")
        return
    if len(message.text.split()) <= 2:
        stocks_list = "\n".join(
            f"{info['رمز']} {name} - {info['وصف']} (تقلب: {info['تقلب']}%)"
            for name, info in STOCK_TYPES.items()
        )
        
        await message.reply(
            f"<b>⇜ أنواع الأسهم المتاحة للشراء:\n\n{stocks_list}\n\n"
            "⇜ استخدم الأمر كذا:\n`شراء سهم` النوع المبلغ\n"
            "مثال: `شراء سهم نفط 1000`</b>"
        )
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 4:
            await message.reply("⇜ استخدم الأمر كذا:\n`شراء سهم` النوع المبلغ")
            return
            
        stock_type = parts[2]
        amount = int(parts[3])
        
        if stock_type not in STOCK_TYPES:
            await message.reply("⇜ نوع السهم غير صحيح! استخدم `شراء سهم` لعرض الخيارات")
            return
            
        if amount < 100:
            await message.reply("⇜ الحد الأدنى لشراء الأسهم هو 100 ريال")
            return
            
        if account['balance'] < amount:
            await message.reply(f"⇜ فلوسك ماتكفي! عندك: {format_money(account['balance'])}")
            return
        volatility = STOCK_TYPES[stock_type]["تقلب"]
        profit_percent = random.randint(-volatility, volatility)
        profit_amount = int(amount * profit_percent / 100)
        
        data = load_data()
        if 'investments' not in data:
            data['investments'] = {}            
        if str(user_id) not in data['investments']:
            data['investments'][str(user_id)] = {}
            
        stock_id = str(int(time.time())) 
        data['investments'][str(user_id)][stock_id] = {
            'type': stock_type,
            'amount': amount,
            'profit': profit_amount,
            'time': int(time.time()),
            'sold': False
        }
        data['accounts'][str(user_id)]['balance'] -= amount 
        data['accounts'][str(user_id)]['balance'] += (amount + profit_amount)
        save_data(data)        
        if profit_amount >= 0:
            await message.reply(
                f"⇜ شراء ناجح!\n"
                f"⇜ نوع السهم: {STOCK_TYPES[stock_type]['رمز']} {stock_type}\n"
                f"⇜ المبلغ المستثمر: {format_money(amount)}\n"
                f"⇜ نسبة الربح: **({profit_percent}%)**\n"
                f"⇜ مبلغ الربح: **({format_money(profit_amount)})** 💰\n"
                f"⇜ فلوسك الحين: **({format_money(data['accounts'][str(user_id)]['balance'])})** 💸"
            )
        else:
            await message.reply(
                f"⇜ شراء خاسر!\n"
                f"⇜ نوع السهم: {STOCK_TYPES[stock_type]['رمز']} {stock_type}\n"
                f"⇜ المبلغ المستثمر: **({format_money(amount)})**\n"
                f"⇜ نسبة الخسارة: **({abs(profit_percent)}%)**\n"
                f"⇜ مبلغ الخسارة: **({format_money(abs(profit_amount))})**💰\n"
                f"⇜ فلوسك الحين: **({format_money(data['accounts'][str(user_id)]['balance'])})** 💸"
            )
            
    except ValueError:
        await message.reply("⇜ المبلغ لازم يكون رقم صحيح!")
    except Exception as e:
        print(f"Error: {e}")
        await message.reply("⇜ حدث خطأ! تأكد من استخدام الأمر بشكل صحيح:\n`شراء سهم النوع المبلغ`")

@app.on_message(filters.command("بيع سهم", ""), group=5337)
async def sell_stock(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `انشاء` عشان تسوي حساب")
        return
    
    if len(message.text.split()) < 3:
        await message.reply("⇜ استخدم الأمر كذا:\n`بيع سهم` رقم السهم\nمثال: `بيع سهم 1754355053`")
        return
    
    try:
        stock_id = message.text.split()[2]
        data = load_data()
        if 'investments' not in data or str(user_id) not in data['investments'] or not data['investments'][str(user_id)]:
            await message.reply("⇜ ماعندك أسهم أساساً!")
            return
        user_stocks = data['investments'][str(user_id)]
        if stock_id not in user_stocks:
            await message.reply("⇜ رقم السهم غير صحيح أو لا ينتمي إليك!")
            return
            
        stock = user_stocks[stock_id]
        total_value = stock['amount'] + stock['profit']
        data['accounts'][str(user_id)]['balance'] += total_value
        del data['investments'][str(user_id)][stock_id]
        
       
        if not data['investments'][str(user_id)]:
            del data['investments'][str(user_id)]
        
        save_data(data)
        
        stock_type = stock['type']
        stock_info = STOCK_TYPES[stock_type]
        
        if stock['profit'] >= 0:
            await message.reply(
                f"⇜ بيع ناجح!\n"
                f"⇜ نوع السهم: {stock_info['رمز']} {stock_type}\n"
                f"⇜ المبلغ المستثمر: **({format_money(stock['amount'])})**\n"
                f"⇜ الربح المحقق: **({format_money(stock['profit'])})**\n"
                f"⇜ القيمة الإجمالية: **({format_money(total_value)})**\n"
                f"⇜ فلوسك الحين: **({format_money(data['accounts'][str(user_id)]['balance'])})** 💸"
            )
        else:
            await message.reply(
                f"⇜ بيع خاسر!\n"
                f"⇜ نوع السهم: {stock_info['رمز']} {stock_type}\n"
                f"⇜ المبلغ المستثمر: **({format_money(stock['amount'])})**\n"
                f"⇜ الخسارة المحققة: **({format_money(abs(stock['profit']))})**\n"
                f"⇜ القيمة الإجمالية: **({format_money(total_value)})**\n"
                f"⇜ فلوسك الحين: **({format_money(data['accounts'][str(user_id)]['balance'])})** 💸"
            )
            
    except Exception as e:
        print(f"Error in sell_stock: {e}")
        await message.reply("⇜ حدث خطأ! تأكد من استخدام الأمر بشكل صحيح:\n`بيع سهم رقم السهم`")

@app.on_message(filters.command("اسهمي", ""), group=5338)
async def my_stocks(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `انشاء`")
        return    
    data = load_data()    
    if 'investments' not in data or str(user_id) not in data['investments'] or not data['investments'][str(user_id)]:
        await message.reply("⇜ ماعندك أسهم أساساً!")
        return    
    stocks = data['investments'][str(user_id)]
    response = "⇜ **محفظتك الاستثمارية:**\n\n"    
    for stock_id, stock in stocks.items():
        stock_info = STOCK_TYPES[stock['type']]
        current_value = stock['amount'] + stock['profit']
        profit_percent = int((stock['profit'] / stock['amount']) * 100) if stock['amount'] > 0 else 0
        
        response += (
            f"{stock_info['رمز']} **{stock['type']}**\n"
            f"⇜ رقم السهم: `{stock_id}`\n"
            f"⇜ القيمة الحالية: {format_money(current_value)}\n"
            f"⇜ الربح/الخسارة: {profit_percent}% ({format_money(stock['profit'])})\n"
            f"⇜ تاريخ الشراء: {time.strftime('%Y-%m-%d %H:%M', time.localtime(stock['time']))}\n\n"
        )    
    response += "⇜ استخدم:\n"
    response += "⇜ `بيع سهم` رقم السهم لبيع سهم معين\n"
    response += "⇜ `بيع كل الاسهم` لبيع كل أسهمك مرة واحدة"
    
    await message.reply(response)
    
    
    
@app.on_message(filters.command("بيع كل الاسهم", ""), group=5339)
async def sell_all_stocks(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `انشاء`")
        return
    
    data = load_data()
    
    if 'investments' not in data or str(user_id) not in data['investments'] or not data['investments'][str(user_id)]:
        await message.reply("⇜ ماعندك أسهم أساساً!")
        return   
    
    total_amount = 0
    stocks_count = 0
    
    for stock_id, stock in list(data['investments'][str(user_id)].items()):
        stock_value = int((stock['amount'] + stock['profit']) * 0.8)
        total_amount += stock_value
        stocks_count += 1
        del data['investments'][str(user_id)][stock_id]
    
    data['accounts'][str(user_id)]['balance'] += total_amount
    
    if not data['investments'][str(user_id)]:
        del data['investments'][str(user_id)]
    
    save_data(data)   
    
    await message.reply(
        f"⇜ تم بيع جميع الأسهم!\n\n"
        f"⇜ عدد الأسهم المباعة: {stocks_count}\n"
        f"⇜ المبلغ الإجمالي: **({format_money(total_amount)})** 💸\n"
        f"⇜ رصيدك الحالي: **({format_money(data['accounts'][str(user_id)]['balance'])})** 💸"
    )

@app.on_message(filters.command(["مضاربه", "مضاعفة"], ""), group=56788)
async def gamble(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    try:
        _, amount = message.text.split()
        amount = int(amount)
    except:
        await message.reply("⇜ استخدمها كذا:\nمضاربة المبلغ")
        return
    
    if amount <= 0:
        await message.reply("⇜ المبلغ لازم يكون أكثر من صفر")
        return
    
    if account['balance'] < amount:
        await message.reply(f"⇜ فلوسك ماتكفي! عندك: {format_money(account['balance'])}")
        return
    
    result_percent = random.randint(-90, 90)
    result_amount = int(amount * result_percent / 100)
    
    data = load_data()
    data['accounts'][str(user_id)]['balance'] += result_amount
    save_data(data)
    
    if result_amount >= 0:
        await message.reply(
            f"⇜ ربحت بالمضاربة!\n"
            f"⇜ المبلغ: **({format_money(amount)})**\n"
            f"⇜ النسبة: (+{result_percent}%)\n"
            f"⇜ الربح: ({format_money(result_amount)})💰\n"
            f"⇜ فلوسك الحين:**({format_money(data['accounts'][str(user_id)]['balance'])})**💸 "
        )
    else:
        await message.reply(
            f"⇜ خسرت بالمضاربة ياهطف!\n"
            f"⇜ المبلغ: **({format_money(amount)})**\n"
            f"⇜ النسبة: {result_percent}%\n"
            f"⇜ الخسارة: {format_money(abs(result_amount))}\n"
            f"⇜ فلوسك صارت: {format_money(data['accounts'][str(user_id)]['balance'])} 💸"
        )

@app.on_message(filters.command("حظ", ""), group=56788)
async def luck(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    remaining = check_cooldown(user_id, 'luck')
    if remaining > 0:
        mins = remaining // 60
        await message.reply(f"⇜ انتظر {mins} دقيقة عشان تلعب حظك مره ثانية")
        return
    
    try:
        _, amount = message.text.split()
        amount = int(amount)
    except:
        await message.reply("⇜ استخدمها كذا:\nحظ المبلغ")
        return
    
    if amount <= 0:
        await message.reply("⇜ المبلغ لازم يكون أكثر من صفر")
        return
    
    if account['balance'] < amount:
        await message.reply(f"⇜ فلوسك ماتكفي! عندك: {format_money(account['balance'])}💸 ")
        return
    
    if random.random() > 0.5:
        win_multiplier = random.uniform(1.0, 3.0)
        win_amount = int(amount * win_multiplier)
        
        data = load_data()
        data['accounts'][str(user_id)]['balance'] += win_amount
        save_data(data)
        update_cooldown(user_id, 'luck')
        
        await message.reply(
            f"⇜ ربحت بلعبة الحظ!\n"
            f"⇜ المبلغ: **({format_money(amount)})**\n"
            f"⇜ المضاعف: {win_multiplier:.1f}x\n"
            f"⇜ الربح: **({format_money(win_amount)})**💰\n"
            f"⇜ فلوسك الحين: **({format_money(data['accounts'][str(user_id)]['balance'])})**💸 "
        )
    else:
        data = load_data()
        data['accounts'][str(user_id)]['balance'] -= amount
        save_data(data)
        update_cooldown(user_id, 'luck')
        
        await message.reply(
            f"⇜ خسرت بلعبة الحظ!\n"
            f"⇜ المبلغ: **({format_money(amount)})**\n"
            f"⇜ فلوسك الحين: **({format_money(data['accounts'][str(user_id)]['balance'])})** 💸"
        )

@app.on_message(filters.command("عجلة الحظ", ""), group=59988)
async def wheel_of_fortune(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    remaining = check_cooldown(user_id, 'wheel')
    if remaining > 0:
        hours = remaining // 3600
        mins = (remaining % 3600) // 60
        await message.reply(f"⇜ انتظر {hours} ساعة و {mins} دقيقة عشان تدور العجلة مره ثانية")
        return
    
    prizes = [
        ("💰 جائزة صغيرة", random.randint(100, 500)),
        ("🎁 جائزة متوسطة", random.randint(500, 1000)),
        ("🏆 جائزة كبيرة", random.randint(1000, 2000)),
        ("💎 جائزة الذهب", random.randint(2000, 5000)),
        ("💔 لا شيء", 0),
        ("🔄 حاول مرة أخرى", 0)
    ]
    
    prize_name, prize_amount = random.choice(prizes)
    
    data = load_data()
    data['accounts'][str(user_id)]['balance'] += prize_amount
    save_data(data)
    update_cooldown(user_id, 'wheel')
    
    if prize_amount > 0:
        await message.reply(
            f"⇜ نتيجة العجلة:\n"
            f"⇜ {prize_name}\n"
            f"⇜ المكسب: **({format_money(prize_amount)})**💰\n"
            f"⇜ فلوسك الحين:** ({format_money(data['accounts'][str(user_id)]['balance'])})**💸 "
        )
    else:
        await message.reply(
            f"⇜ نتيجة العجلة:\n"
            f"⇜ {prize_name}\n"
            f"⇜ ماجاك شيء هالمرة!"
        )

@app.on_message(filters.command(["حمايه", "حماية اموال"], ""), group=5999)
async def protect_money(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    remaining = check_cooldown(user_id, 'protection')
    if remaining > 0:
        hours = remaining // 3600
        mins = (remaining % 3600) // 60
        await message.reply(f"⇜ انتظر {hours} ساعة و {mins} دقيقة عشان تحمي فلوسك مره ثانية")
        return
    
    protection_cost = 500
    if account['balance'] < protection_cost:
        await message.reply(f"⇜ فلوسك ماتكفي! تحتاج {format_money(protection_cost)} عشان تشتري الحماية")
        return
    
    data = load_data()
    data['accounts'][str(user_id)]['balance'] -= protection_cost
    data['accounts'][str(user_id)]['protected'] = True
    save_data(data)
    update_cooldown(user_id, 'protection')
    
    await message.reply(
        f"⇜ خلاص ⇜ حماية فلوسك شغالة!\n"
        f"⇜ التكلفة: **({format_money(protection_cost)})**\n"
        f"⇜ فلوسك الحين: **({format_money(data['accounts'][str(user_id)]['balance'])})**💸 \n\n"
        f"⇜ الحماية بتنتهي بعد 24 ساعة أو بعد سرقة وحدة"
    )

@app.on_message(filters.command(["شرطه", "شرطة"], ""), group=56789)
async def police(client, message):
    if not message.reply_to_message:
        await message.reply("⇜ رد على الشخص عشان تبلغ عنه")
        return
    
    user_id = message.from_user.id
    reporter_account = get_account(user_id)
    
    if not reporter_account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    thief_id = message.reply_to_message.from_user.id
    if thief_id == user_id:
        await message.reply("⇜ ماتقدر تبلغ على نفسك!")
        return
    
    thief_account = get_account(thief_id)
    if not thief_account:
        await message.reply("⇜ ماعنده حساب أساساً!")
        return
    
    if random.random() < 0.3:
        stolen_amount = random.randint(100, min(1000, thief_account['balance']))
        
        data = load_data()
        if data['accounts'][str(thief_id)]['balance'] >= stolen_amount:
            data['accounts'][str(thief_id)]['balance'] -= stolen_amount
            data['accounts'][str(user_id)]['balance'] += stolen_amount
            
            if str(thief_id) in data['protected']:
                del data['protected'][str(thief_id)]
            
            save_data(data)
            
            await message.reply(
                f"⇜ خلاص ⇜ الشرطة مسكت اللص!\n"
                f"⇜ استرجعوا لك: **({format_money(stolen_amount)})**\n"
                f"⇜ فلوسك الحين: **({format_money(data['accounts'][str(user_id)]['balance'])})** 💸"
            )
        else:
            await message.reply("⇜ الفلوس اللي عنده ماتسوى!")
    else:
        await message.reply("⇜ الشرطة ماقدرت تمسكه هالمرة!")

@app.on_message(filters.command("كنز", ""), group=5899)
async def treasure(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    remaining = check_cooldown(user_id, 'treasure')
    if remaining > 0:
        hours = remaining // 3600
        mins = (remaining % 3600) // 60
        await message.reply(f"⇜ انتظر {hours} ساعة و {mins} دقيقة عشان تدور على كنز مره ثانية")
        return
    
    data = load_data()
    if data['treasure'] <= 0:
        await message.reply("⇜ الكنز خلص الحين، جرب بكرا!")
        return
    
    if random.random() < 0.2:
        treasure_amount = random.randint(1000, min(5000, data['treasure']))
        data['accounts'][str(user_id)]['balance'] += treasure_amount
        data['treasure'] -= treasure_amount
        save_data(data)
        update_cooldown(user_id, 'treasure')
        
        await message.reply(
            f"⇜ لقيت كنز!\n"
            f"⇜ المبلغ: **({format_money(treasure_amount)})**💰\n"
            f"⇜ فلوسك الحين: **({format_money(data['accounts'][str(user_id)]['balance'])})** 💸\n"
            f"⇜ الكنز المتبقي: {format_money(data['treasure'])}"
        )
    else:
        update_cooldown(user_id, 'treasure')
        await message.reply("⇜ مالقيت شيء هالمرة، جرب بكرا!")

@app.on_message(filters.command(["توب الفلوس", "توب فلوس"], ""), group=5008)
async def top_balances(client, message):
    data = load_data()
    accounts = data['accounts']
    
    if not accounts:
        await message.reply("⇜ مافي حسابات بنكية للحين!")
        return
    filtered_accounts = {k: v for k, v in accounts.items() if v['balance'] >= 50000}    
    if not filtered_accounts:
        await message.reply("⇜ مافي أحد رصيده وصل 50,000 ريال للحين!")
        return
    sorted_accounts = sorted(filtered_accounts.items(), key=lambda x: x[1]['balance'], reverse=True)    
    response = "⇜ **هادول اغني 20 شخص باللعبة** 💰\n\n"    
    for idx, (user_id, account) in enumerate(sorted_accounts, 1):
        try:
            user = await client.get_users(int(user_id))
            name = user.first_name
        except:
            name = "مجهول"
        medal = ""
        if idx == 1:
            medal = "🎖️ "
        elif idx == 2:
            medal = "🥈 "
        elif idx == 3:
            medal = "🥉 "   
        response += f"{medal}{idx}. {name}: {format_money(account['balance'])}\n"    
    await message.reply(response)





@app.on_message(filters.command("ميداليات", ""), group=5009)
async def my_medals(client, message):
    user_id = message.from_user.id
    data = load_data()
    accounts = data['accounts']
    if str(user_id) not in accounts:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم انشاء عشان تسوي حساب")
        return
    user_balance = accounts[str(user_id)]['balance']
    if user_balance < 50000:
        await message.reply("⇜ ماعندك أي ميداليات بعد! رصيدك الحالي: " + format_money(user_balance))
        return
    
    filtered_accounts = {k: v for k, v in accounts.items() if v['balance'] >= 50000}
    sorted_accounts = sorted(filtered_accounts.items(), key=lambda x: x[1]['balance'], reverse=True)[:3]  
    user_in_top = any(str(user_id) == account[0] for account in sorted_accounts)   
    if not user_in_top:
        await message.reply(f"⇜ رصيدك {format_money(user_balance)} لكنك مو من الأوائل الثلاثة!")
        return
    
    response = "🏆 **أقوى 3 لاعبين في البنك** 🏆\n\n"
    
    for idx, (account_id, account) in enumerate(sorted_accounts, 1):
        try:
            user = await client.get_users(int(account_id))
            name = user.first_name
        except:
            name = "مجهول"
        
        medal = ""
        if idx == 1:
            medal = "🎖️ بطل البنك "
        elif idx == 2:
            medal = "🥈 وصيف البطل "
        elif idx == 3:
            medal = "🥉 مركز ممتاز "
        is_me = " (أنت) " if str(user_id) == account_id else ""      
        response += f"{medal}{is_me}\n⇜ الاسم: {name}\n⇜ الرصيد: {format_money(account['balance'])}💸 \n\n"
    
    # إضافة معلومات إضافية للمستخدم
    if str(user_id) in [x[0] for x in sorted_accounts]:
        user_position = [i+1 for i, x in enumerate(sorted_accounts) if x[0] == str(user_id)][0]
        response += f"⇜ أنت في المركز {user_position}! ⇜ فلوسك: {format_money(user_balance)}"
    
    await message.reply(response)




@app.on_message(filters.command(["توب الحراميه", "توب سرقه"], ""), group=5877755)
async def top_thieves(client, message):
    data = load_data()
    thieves = data.get('thieves', {})
    
    if not thieves:
        await message.reply("⇜ مافي حرامية مسجلين للحين!")
        return
    
    sorted_thieves = sorted(thieves.items(), key=lambda x: x[1], reverse=True)[:10]
    
    response = "⇜ **أكبر 10 حرامية:**\n\n"
    for idx, (user_id, amount) in enumerate(sorted_thieves, 1):
        try:
            user = await client.get_users(int(user_id))
            name = user.first_name
        except:
            name = "مجهول"
        
        response += f"{idx}. {name}: **({format_money(amount)})** مسروقة\n"
    
    await message.reply(response)

@app.on_message(filters.command("رشوه", ""), group=5334)
async def bribe(client, message):
    user_id = message.from_user.id
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    if not message.reply_to_message:
        await message.reply("⇜ رد على الشخص عشان ترشوه")
        return
    
    target_id = message.reply_to_message.from_user.id
    if target_id == user_id:
        await message.reply("⇜ ماتقدر ترشو نفسك!")
        return
    
    bribe_amount = random.randint(300, 1000)
    if account['balance'] < bribe_amount:
        await message.reply(f"⇜ فلوسك ماتكفي! تحتاج {format_money(bribe_amount)} عشان ترشوه")
        return
    
    if random.random() < 0.7:
        data = load_data()
        data['accounts'][str(user_id)]['balance'] -= bribe_amount
        
        if str(target_id) in data['accounts']:
            data['accounts'][str(target_id)]['balance'] += bribe_amount // 2
        
        save_data(data)
        
        await message.reply(
            f"⇜ خلاص ⇜ الرشوة نجحت!\n"
            f"⇜ المبلغ: {format_money(bribe_amount)}\n"
            f"⇜ فلوسك الحين: {format_money(data['accounts'][str(user_id)]['balance'])}"
        )
    else:
        await message.reply("⇜ الرشوة فشلت وتم الإبلاغ عنك!")



user_last_show_codes = {}  
user_last_use_any_code = {} 

@app.on_message(filters.command("اكشط", ""), group=54333)
async def scratch_codes(client, message):
    user_id = message.from_user.id
    
    # التحقق من وقت الانتظار لعرض الأكواد
    if user_id in user_last_show_codes:
        last_time = user_last_show_codes[user_id]
        current_time = time.time()
        elapsed_time = current_time - last_time
        remaining_time = 12 * 3600 - elapsed_time
        
        if elapsed_time < 12 * 3600:
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            seconds = int(remaining_time % 60)
            
            if hours > 0:
                wait_msg = f"⇜ انتظر {hours} ساعة و {minutes} دقيقة عشان تشوف أكواد جديدة"
            elif minutes > 0:
                wait_msg = f"⇜ انتظر {minutes} دقيقة و {seconds} ثانية عشان تشوف أكواد جديدة"
            else:
                wait_msg = f"⇜ انتظر {seconds} ثانية عشان تشوف أكواد جديدة"
                
            await message.reply(wait_msg)
            return
    
    account = get_account(user_id)
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    new_codes = generate_new_codes(10)
    
    codes_message = "**هالحين جوك 10 اكواد كشط 💸**\n\n"
    codes_message += "⇜ تقدر تكشط كود واحد فقط من هاللسته كل 12 ساعة\n\n"
    
    for idx, (code, reward) in enumerate(new_codes, 1):
        codes_message += f"{idx}. `{code}`\n"
    
    codes_message += "\n⇜ استخدم: `كشط الكود` عشان تكشط (كود واحد كل 12 ساعة)"
    
    user_last_show_codes[user_id] = time.time()
    
    await message.reply(codes_message)


@app.on_message(filters.command("كشط", ""), group=578)
async def use_code(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    account = get_account(user_id)

    # التحقق من وقت الانتظار لاستخدام الأكواد
    if user_id in user_last_use_any_code:
        last_time = user_last_use_any_code[user_id]
        current_time = time.time()
        elapsed_time = current_time - last_time
        remaining_time = 12 * 3600 - elapsed_time
        
        if elapsed_time < 12 * 3600:
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            seconds = int(remaining_time % 60)
            
            if hours > 0:
                wait_msg = f"⇜ ماتقدر تكشط كود ثاني إلا بعد {hours} ساعة و {minutes} دقيقة"
            elif minutes > 0:
                wait_msg = f"⇜ ماتقدر تكشط كود ثاني إلا بعد {minutes} دقيقة و {seconds} ثانية"
            else:
                wait_msg = f"⇜ ماتقدر تكشط كود ثاني إلا بعد {seconds} ثانية"
                
            await message.reply(wait_msg)
            return
    
    if not account:
        await message.reply("⇜ ماعندك حساب بنكي! استخدم `بنك`")
        return
    
    try:
        _, code = message.text.split()
    except:
        await message.reply("⇜ استخدمها كذا:\nكشط الكود")
        return
    
    codes_data = load_codes_data()
    
    if code not in codes_data['active_codes']:
        await message.reply("⇜ الكود غلط أو منتهي!")
        return
    
    if codes_data['active_codes'][code]['used']:
        await message.reply("⇜ هذا الكود مستخدم خلاص!")
        return
    
    if codes_data['active_codes'][code]['expires_at'] < int(time.time()):
        await message.reply("⇜ الكود منتهي الصلاحية!")
        return
    
    reward = codes_data['active_codes'][code]['reward']
    data = load_data()
    data['accounts'][str(user_id)]['balance'] += reward
    
    codes_data['active_codes'][code]['used'] = True
    codes_data['used_codes'][code] = {
        'user_id': user_id,
        'reward': reward,
        'used_at': int(time.time())
    }
    
    save_data(data)
    save_codes_data(codes_data)
    
    # تحديث وقت آخر استخدام لأي كود
    user_last_use_any_code[user_id] = time.time()
    
    user_mention = f"<a href='tg://user?id={user_id}'>{user_name}</a>"   
    await message.reply(
        f"⇜ تهانينا! {user_mention} ربحت!\n\n"
        f"⇜ المبلغ: <b>({format_money(reward)})</b>💰\n"
        f"⇜ فلوسك الحين: <b>({format_money(data['accounts'][str(user_id)]['balance'])})</b>💸\n\n"
        f"⇜ تقدر تكشط كود ثاني بعد 12 ساعة",
        parse_mode=enums.ParseMode.HTML
    )    
    
    
    
@app.on_message(filters.command("بنك", ""), group=59999)
async def bank_help(client, message):
    help_text = """
⌯**أوامر لعبة البنك** 
• `انشاء حساب بنكي` ⇜ تسوي حساب بنكي جديد
• `حسابي` ⇜ تشوف معلومات حسابك
• `فلوسي` أو `رصيدي` ⇜ تشوف رصيدك
• `فلوسه` أو `رصيده` بالرد ⇜ تشوف رصيد غيرك

⌯ **التحويلات والأسهم**:
• `تحويل` رقم الحساب المبلغ ⇜ تحول فلوس
• `شراء سهم` ⇜ لعرض قائمة الاسهم
• شراء سهم النوع المبلغ لشراء سهم الي تبيه
• `اسهمي` ⇜ تشوف محفظتك
• `بيع سهم` رقم السهم ⇜ تبيع سهم معين
• `بيع كل الاسهم` ⇜ تبيّع كل أسهمك

⌯ **جني الفلوس**:
• `راتب` ⇜ تاخذ راتبك (كل 20 دقيقة)
• `بخشيش` ⇜ هبة مجانية (كل 10 دقائق)
• `استثمار المبلغ` ⇜ استثمار آمن (كل 30 دقيقة)
• `مضاربه` المبلغ ⇜ مضاربة عالية المخاطرة
• `حظ المبلغ` ⇜ لعبة حظ (50٪ فرصة ربح)
• `عجلة الحظ` ⇜ جائزة كل 4 ساعات
• `كنز` ⇜ كنز كل 6 ساعات

⌯ **الحماية والسرقة**:
• `زرف` أو `سرقه` بالرد ⇜ تسرق (كل 10 دقائق)
• `حماية` ⇜ حماية حسابك (كل ساعة)
• `شرطة` بالرد ⇜ تبلغ على حرامي
• `رشوة` بالرد ⇜ تحاول ترشو أحد

⌯ **الأكواد**:
• `اكشط` ⇜ تشوف الأكواد المتاحة (كل 12 ساعة)
• `كشط الكود` ⇜ تكشط كود وتربح (كل 12 ساعة)

⌯ **التوبات**:
• `توب الفلوس` ⇜ أقوى 20 لاعب
• `توب الحرامية` ⇜ أكبر سراق
• `ميداليات` ⇜ المتصدرين
"""
    await message.reply(help_text)