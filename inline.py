from pyrogram import types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle
import logging

from anony import app, config, lang

_control_button_text = "VEGA"
_control_button_url = None







    
    
    
    
    
class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton


    def cancel_dl(self, text) -> InlineKeyboardMarkup:
        return self.ikm([[
            self.ikb(text=text, callback_data="cancel_dl", style=ButtonStyle.DANGER)
        ]])

    def close_markup(self, _) -> InlineKeyboardMarkup:

        return self.ikm(
            [[self.ikb(text=_["close"], callback_data="close", style=ButtonStyle.DANGER)]]
        )

    async def controls(
        self,
        chat_id: int,
        status: str = None,
        timer: str = None,
        remove: bool = False,
    ) -> InlineKeyboardMarkup:
        keyboard = []

        # حالة التشغيل / الوقت فقط
        if remove:
            if status:
                keyboard.append([
                    self.ikb(
                        text=status,
                        callback_data=f"controls status {chat_id}",
                        style=ButtonStyle.SUCCESS,
                    )
                ])
            elif timer:
                keyboard.append([
                    self.ikb(
                        text=timer,
                        callback_data=f"controls timer {chat_id}",
                        style=ButtonStyle.SUCCESS,
                    )
                ])
            return self.ikm(keyboard)

        # الصف الأول
        keyboard.append([
            self.ikb(text="ʀᴇsᴜᴍ", callback_data=f"controls resume {chat_id}", style=ButtonStyle.PRIMARY),
            self.ikb(text="ᴘᴀᴜsᴇ", callback_data=f"controls pause {chat_id}", style=ButtonStyle.PRIMARY),
            self.ikb(text="sᴋɪᴘ", callback_data=f"controls skip {chat_id}", style=ButtonStyle.PRIMARY),
            self.ikb(text="sᴛᴏᴘ", callback_data=f"controls stop {chat_id}", style=ButtonStyle.PRIMARY),
        ])

        # الصف الثاني
        played_time = timer if timer else "00:00"
        keyboard.append([
            self.ikb(text="«", callback_data=f"controls seek_back {chat_id}", style=ButtonStyle.PRIMARY),
            self.ikb(text=played_time, callback_data=f"controls timer {chat_id}", style=ButtonStyle.SUCCESS),
            self.ikb(text="»", callback_data=f"controls seek_fwd {chat_id}", style=ButtonStyle.PRIMARY),
        ])
        

            # زر مخصص من قاعدة البيانات
        button_text, button_url = get_control_button()
        keyboard.append(
            [self.ikb(button_text, url=button_url)]
        )
        return self.ikm(keyboard)

    # ─────────────────────────────────────────────
    #  قائمة المساعدة
    # ─────────────────────────────────────────────
    def help_markup(self, _lang: dict, back: bool = False) -> InlineKeyboardMarkup:
        if back:
            rows = [[
                self.ikb(text=_lang["back"], callback_data="help back"),
                self.ikb(text=_lang["close"], callback_data="help close"),
            ]]
        else:
            buttons = [
                self.ikb(text=_lang["help_1"], callback_data="help queue"),
                self.ikb(text=_lang["help_5"], callback_data="help play"),
                self.ikb(text=_lang["help_8"], callback_data="help sudo"),
                self.ikb(text=_lang["help_3"], callback_data="help lang"),
            ]
            rows = [[buttons[0]], [buttons[1], buttons[2]], [buttons[3]]]
        return self.ikm(rows)

    # ─────────────────────────────────────────────
    #  قائمة اللغات
    # ─────────────────────────────────────────────
    def lang_markup(self, _lang: str) -> InlineKeyboardMarkup:
        langs = lang.get_languages()
        buttons = [
            self.ikb(
                text=f"{name} ({code}) {'•' if code == _lang else ''}",
                callback_data=f"lang_change {code}",
            )
            for code, name in langs.items()
        ]
        rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
        return self.ikm(rows)

    # ─────────────────────────────────────────────
    #  ping
    # ─────────────────────────────────────────────
    def ping_markup(self, text: str) -> InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, url=config.SUPPORT_CHAT)]])

    # ─────────────────────────────────────────────
    #  قائمة الانتظار
    # ─────────────────────────────────────────────
    def play_queued(self, chat_id: int, item_id: str, _text: str) -> InlineKeyboardMarkup:
        return self.ikm([[
            self.ikb(text=_text, callback_data=f"controls force {chat_id} {item_id}")
        ]])

    def queue_markup(self, chat_id: int, _text: str, playing: bool) -> InlineKeyboardMarkup:
        _action = "pause" if playing else "resume"
        return self.ikm([[
            self.ikb(text=_text, callback_data=f"controls {_action} {chat_id} q")
        ]])

    # ─────────────────────────────────────────────
    #  الإعدادات
    # ─────────────────────────────────────────────
    def settings_markup(
        self, lang: dict, admin_only: bool, cmd_delete: bool, language: str, chat_id: int
    ) -> InlineKeyboardMarkup:
        from anony.core.lang import lang_codes
        return self.ikm([
            [
                self.ikb(text=lang["play_mode"] + " -", callback_data="settings"),
                self.ikb(text=admin_only, callback_data="settings play"),
            ],
            [
                self.ikb(text=lang["cmd_delete"] + " -", callback_data="settings"),
                self.ikb(text=cmd_delete, callback_data="settings delete"),
            ],
            [
                self.ikb(text=lang["language"] + " -", callback_data="settings"),
                self.ikb(text=lang_codes[language], callback_data="language"),
            ],
        ])

    # ─────────────────────────────────────────────
    #  start
    # ─────────────────────────────────────────────
    async def start_key(self, lang: dict, private: bool = False) -> InlineKeyboardMarkup:
        owner_id = int(config.OWNER_ID)
        owner_name = "Owner"
        try:
            owner = await app.get_users(owner_id)
            owner_name = owner.first_name
        except Exception as e:
            print(f"Failed to get owner: {e}")

        rows = [[InlineKeyboardButton(text=f"{owner_name}", user_id=owner_id)]]
        rows += [[self.ikb(text=lang["language"], callback_data="language")]]
        return self.ikm(rows)

    # ─────────────────────────────────────────────
    #  يوتيوب
    # ─────────────────────────────────────────────
    def yt_key(self, link: str) -> InlineKeyboardMarkup:
        return self.ikm([[
            self.ikb(text="❐", callback_data=f"copy {link}"),
            self.ikb(text="Youtube", url=link),
        ]])



_control_buttons_cache: dict = {}


async def update_control_button_cache(bot_id: int = None):
    global _control_buttons_cache
    from anony import db

    if bot_id is None:
        bot_id = app.me.id

    text = await db.get_control_button_text(bot_id)
    url = await db.get_control_button_url(bot_id)
    _control_buttons_cache[bot_id] = {"text": text, "url": url}
    return _control_buttons_cache[bot_id]


def get_control_button(bot_id: int = None):
    global _control_buttons_cache
    from anony import config

    if bot_id is None:
        bot_id = app.me.id

    if bot_id not in _control_buttons_cache:
        return "𝖲𝖮𝖴𝖭𝖣", config.SUPPORT_CHANNEL

    cached = _control_buttons_cache[bot_id]
    url = cached.get("url") or config.SUPPORT_CHANNEL
    text = cached.get("text") or "ꜱᴏᴜɴᴅ"
    return text, url
    