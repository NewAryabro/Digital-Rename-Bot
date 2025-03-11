# (c) @RknDeveloperr
# Rkn Developer
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr
# Special Thanks To @ReshamOwner
# Update Channel @Digital_Botz & @DigitalBotz_Support

"""
Apache License 2.0
Copyright (c) 2022 @Digital_Botz
"""

# pyrogram imports
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait
from pyrogram.file_id import FileId
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

# hachoir imports
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

# bots imports
from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix
from helper.database import digital_botz
from helper.ffmpeg import change_metadata
from config import Config

# extra imports
from asyncio import sleep
import os, time

UPLOAD_TEXT = "Uploading Started...."
DOWNLOAD_TEXT = "Download Started..."

app = Client("4gb_FileRenameBot", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION)

@Client.on_message(filters.private & (filters.audio | filters.document | filters.video))
async def rename_start(client, message):
    user_id = message.from_user.id
    rkn_file = getattr(message, message.media.value)
    filename = rkn_file.file_name
    filesize = humanbytes(rkn_file.file_size)
    mime_type = rkn_file.mime_type
    dcid = FileId.decode(rkn_file.file_id).dc_id
    extension_type = mime_type.split('/')[1]  

    if client.premium and client.uploadlimit:
        await digital_botz.reset_uploadlimit_access(user_id)
        user_data = await digital_botz.get_user_data(user_id)
        limit = user_data.get('uploadlimit', 0)
        used = user_data.get('used_limit', 0)
        remain = int(limit) - int(used)
        used_percentage = (int(used) / int(limit)) * 100 if limit else 0

        if remain < int(rkn_file.file_size):
            return await message.reply_text(
                f"{used_percentage:.2f}% of Daily Upload Limit {humanbytes(limit)}.\n\n"
                f"Media Size: {filesize}\nYour Used Daily Limit: {humanbytes(used)}\n\n"
                f"You have only **{humanbytes(remain)}** data remaining.\nPlease upgrade to a premium plan.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🪪 Upgrade", callback_data="plans")]])
            )

    if rkn_file.file_size > 2000 * 1024 * 1024 and not Config.STRING_SESSION:
        return await message.reply_text("This bot does not support renaming files larger than 2GB+.")

    await message.reply_text(
        text=f"**Media Info:**\n\n"
             f"◈ Old File Name: `{filename}`\n"
             f"◈ Extension: `{extension_type.upper()}`\n"
             f"◈ File Size: `{filesize}`\n"
             f"◈ MIME Type: `{mime_type}`\n"
             f"◈ DC ID: `{dcid}`\n\n"
             f"Please enter the new filename with extension and reply to this message.",
        reply_to_message_id=message.id,
        reply_markup=ForceReply(True)
    )

@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    reply_message = message.reply_to_message
    if reply_message.reply_markup and isinstance(reply_message.reply_markup, ForceReply):
        new_name = message.text.strip()
        await message.delete()

        msg = await client.get_messages(message.chat.id, reply_message.id)
        file = msg.reply_to_message
        media = getattr(file, file.media.value)

        if "." not in new_name:
            extn = media.file_name.rsplit('.', 1)[-1] if "." in media.file_name else "mkv"
            new_name = f"{new_name}.{extn}"

        await reply_message.delete()

        button = [[InlineKeyboardButton("📁 Document", callback_data="upload_document")]]
        if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
            button.append([InlineKeyboardButton("🎥 Video", callback_data="upload_video")])
        elif file.media == MessageMediaType.AUDIO:
            button.append([InlineKeyboardButton("🎵 Audio", callback_data="upload_audio")])

        await message.reply(
            text=f"**Select The Output File Type**\n**• File Name :-** `{new_name}`",
            reply_to_message_id=file.id,
            reply_markup=InlineKeyboardMarkup(button)
	)
