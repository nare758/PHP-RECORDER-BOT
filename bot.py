import os
import asyncio
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Setup ---
API_ID = "20918855"
API_HASH = "c511716301ab7675a39409a55408eb02"
BOT_TOKEN = "8537051456:AAF3AuGaideOrRKL2aslYMUjVzBSMj9_5Us"

bot = Client("ProStreamer", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def welcome(client, message):
    text = (
        "**🔥 StreamVault Pro v2.0**\n\n"
        "Link record karne ke liye format use karein:\n"
        "`/record [URL] [TIME_IN_SECONDS]`\n\n"
        "**Example:**\n"
        "`/record http://link.com/live.php 300` (for 5 mins)"
    )
    await message.reply_text(text)

@bot.on_message(filters.command("record"))
async def start_recording(client, message):
    # User input check karte hain
    input_data = message.text.split(" ")
    
    if len(input_data) < 3:
        return await message.reply_text("❌ **Format galat hai!**\nUse: `/record [link] [seconds]`")

    target_url = input_data[1]
    duration = input_data[2] # User jitna time bolega
    
    status = await message.reply_text("🔍 **Link verify ho raha hai...**")
    
    # Filename with User ID to avoid mixing files
    file_path = f"stream_{message.from_user.id}.mp4"

    # FFmpeg Command with Dynamic Duration
    # '-t' flag decide karta hai ki kitni der record karna hai
    ffmpeg_cmd = [
        "ffmpeg", "-reconnect", "1", "-reconnect_streamed", "1", 
        "-reconnect_delay_max", "5", "-i", target_url,
        "-t", duration, "-c", "copy", "-bsf:a", "aac_adtstoasc",
        file_path, "-y"
    ]

    try:
        await status.edit(f"🔴 **Recording Start...**\n⏳ Duration: `{duration}s`")
        
        # Background process execution
        process = await asyncio.create_subprocess_exec(
            *ffmpeg_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Wait for FFmpeg to finish
        await process.communicate()

        if not os.path.exists(file_path):
            return await status.edit("❌ **Recording failed!** Link expire ho gaya ya invalid hai.")

        await status.edit("⚡ **Encoding done! Uploading now...**")
        
        # Video upload logic
        await message.reply_video(
            video=file_path,
            caption=f"✅ **Recorded Successfully!**\n\n🔗 URL: `{target_url}`\n⏱ Duration: `{duration}s`"
        )
        
        # Cleanup file after upload
        os.remove(file_path)
        await status.delete()

    except Exception as err:
        await status.edit(f"⚠️ **Technical Error:** `{err}`")

bot.run()
