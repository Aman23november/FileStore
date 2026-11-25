from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from helper_func import admin
from database.database import db


@Bot.on_message(filters.private & admin & filters.command("addpremium"))
async def add_premium_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> <code>/addpremium user_id</code>")
    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("<b>Invalid user_id.</b> Please pass a numeric Telegram user ID.")

    await db.add_premium_user(user_id)
    await message.reply_text(f"✅ User <code>{user_id}</code> added to <b>Premium</b>.")


@Bot.on_message(filters.private & admin & filters.command("rempremium"))
async def rem_premium_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> <code>/rempremium user_id</code>")
    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("<b>Invalid user_id.</b> Please pass a numeric Telegram user ID.")

    await db.remove_premium_user(user_id)
    await message.reply_text(f"🗑 User <code>{user_id}</code> removed from <b>Premium</b>.")


@Bot.on_message(filters.private & admin & filters.command("listpremium"))
async def list_premium_cmd(client: Client, message: Message):
    users = await db.get_all_premium_users()
    if not users:
        return await message.reply_text("ℹ️ No premium users found.")

    text = "<b>👑 Premium Users List:</b>\n\n" + "\n".join(f"• <code>{uid}</code>" for uid in users)
    await message.reply_text(text)
