import utils
import pathlib
import pyrogram
import tiktok_downloader
import time
import re
import os
import json
import pytz
from load import *
from datetime import datetime, timezone
from broadcast import Broadcaster, get_broadcast_handlers
# Import language module
import language

# Define Kenya timezone
KENYA_TZ = pytz.timezone("Africa/Nairobi")

# File paths for user tracking and admin management
USERS_LOG_FILE = "users.log"
ADMIN_FILE = "admin.json"

cwd = pathlib.Path(__file__).parent

bot = pyrogram.Client(
    name="tiktok-bot", api_id=api_id, api_hash=api_hash, bot_token=token_bot
)

user_cooldowns = {}
COOLDOWN_TIME = 2  # Cooldown time in seconds

# Create broadcaster instance
broadcaster = Broadcaster(USERS_LOG_FILE, ADMIN_FILE)

# Admin and user tracking functions
def get_admin():
    """Get the admin user ID from the admin file"""
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "r") as file:
            return json.load(file).get("admin_id")
    return None

def set_admin(user_id):
    """Set a user as the admin"""
    if not os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "w") as file:
            json.dump({"admin_id": user_id}, file)

def log_user_data(user):
    """Log user activity to the users log file"""
    server_time = datetime.now()
    kenya_time = server_time.astimezone(KENYA_TZ)

    user_data = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "timestamp": kenya_time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    try:
        if os.path.exists(USERS_LOG_FILE):
            with open(USERS_LOG_FILE, "r") as file:
                users = json.load(file)
        else:
            users = []

        # Update existing user or add new user
        for existing_user in users:
            if existing_user["user_id"] == user_data["user_id"]:
                existing_user["timestamp"] = user_data["timestamp"]
                break
        else:
            users.append(user_data)

        with open(USERS_LOG_FILE, "w") as file:
            json.dump(users, file, indent=4)

    except Exception as e:
        print(f"Error logging user data: {e}")

# Fixed reaction function using the older Pyrogram API format
async def set_reaction(client, message, emoji):
    try:
        # Use the string emoji directly with Pyrogram's send_reaction
        await client.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id, 
            emoji=emoji
        )
        print(f"Set reaction {emoji} on message {message.id}")
    except Exception as e:
        print(f"Failed to set reaction: {e}")
        # If the above fails, try an alternative approach for older Pyrogram versions
        try:
            # For older Pyrogram versions that may not support reactions directly
            await message.react(emoji)
            print(f"Set reaction using message.react() method: {emoji}")
        except Exception as e2:
            print(f"Both reaction methods failed: {e2}")

def extract_tiktok_url(text):
    pattern = r"""
        (?:https?://)?
        (?:www\.|m\.)?
        (?:
            tiktok\.com
            |vm\.tiktok\.com
            |tiktok\.\w{2,3}(?:\.\w{2})?
        )
        /[^\s]+
    """
    match = re.search(pattern, text, re.VERBOSE)
    
    if match:
        url = match.group(0)
        if not url.startswith("http"):
            url = "https://" + url
        if "tiktok.com" in url and "/video/" not in url and "vm.tiktok.com" not in url:
            return None, "invalid_tiktok_url"  # Changed to use key instead of message
        return url, None  
    
    return None, "no_tiktok_url"  # Changed to use key instead of message

async def start_handler(client: pyrogram.Client, message: pyrogram.types.Message):
    # Log user data when they start the bot
    log_user_data(message.from_user)
    
    # Get user's language
    user_id = message.from_user.id
    user_lang = language.get_user_language(user_id)
    
    # Set the first user as admin if no admin exists
    if get_admin() is None:
        set_admin(user_id)
        await client.send_message(
            chat_id=message.chat.id, 
            text=language.get_text(user_lang, "admin_set")
        )

    first_name = message.chat.first_name
    userid = message.chat.id
    msgid = message.id
    
    # Get welcome message in user's language
    welcome_text = language.get_text(user_lang, "welcome_message", first_name=first_name)
    
    await client.send_message(chat_id=userid, text=welcome_text, reply_to_message_id=msgid)
    # Add welcome reaction
    await set_reaction(client, message, "👋")

async def list_users_handler(client: pyrogram.Client, message: pyrogram.types.Message):
    """Handler for the /users command - only accessible to admin"""
    user = message.from_user
    admin_id = get_admin()
    user_lang = language.get_user_language(user.id)

    if user.id != admin_id:
        await client.send_message(
            chat_id=message.chat.id, 
            text=language.get_text(user_lang, "no_permission")
        )
        return

    try:
        if os.path.exists(USERS_LOG_FILE):
            with open(USERS_LOG_FILE, "r") as file:
                users = json.load(file)

            if not users:
                await client.send_message(
                    chat_id=message.chat.id, 
                    text=language.get_text(user_lang, "no_users")
                )
                return

            # Get today's date in Kenya timezone for comparing with user timestamps
            today = datetime.now(KENYA_TZ).date()
            total_users = len(users)
            today_users = sum(
                1 for u in users if datetime.strptime(u['timestamp'], "%Y-%m-%d %H:%M:%S").date() == today
            )

            response = language.get_text(
                user_lang, "user_stats",
                total=total_users,
                today=today_users
            )
            
            for u in users:
                response += language.get_text(
                    user_lang, "user_entry",
                    user_id=u['user_id'],
                    username=u['username'] or 'N/A',
                    first_name=u['first_name'],
                    timestamp=u['timestamp']
                )
                
            await client.send_message(chat_id=message.chat.id, text=response)
        else:
            await client.send_message(
                chat_id=message.chat.id, 
                text=language.get_text(user_lang, "no_log_file")
            )
    except Exception as e:
        print(f"Error reading log: {e}")
        await client.send_message(
            chat_id=message.chat.id, 
            text=language.get_text(user_lang, "user_data_error")
        )

async def callback_handler(client: pyrogram.Client, callback_query: pyrogram.types.CallbackQuery):
    # First, check if this is a broadcast callback - if so, let the broadcaster handle it
    if callback_query.data.startswith("broadcast_"):
        # The broadcast callback handler will take care of this
        return
    
    # Check if this is a language selection callback
    if callback_query.data.startswith("lang_"):
        await handle_language_callback(client, callback_query)
        return
    
    # For other callbacks, proceed with regular handling
    # Log user data when they interact with inline buttons
    log_user_data(callback_query.from_user)
    user_lang = language.get_user_language(callback_query.from_user.id)
    
    print(f"General callback handler received: {callback_query.data}")
    
    if callback_query.data == "ReelsDownloader":
        await callback_query.answer()
        await client.send_message(
            chat_id=callback_query.from_user.id, 
            text=language.get_text(user_lang, "reels_coming_soon")
        )

async def handle_language_callback(client, callback_query):
    """Handle language selection callbacks"""
    # Extract language code from callback data (format: "lang_CODE")
    lang_code = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    
    # Update user's language preference
    success = language.set_user_language(user_id, lang_code)
    
    if success:
        # Get language name
        language_name = language.AVAILABLE_LANGUAGES[lang_code]
        
        # Send confirmation message
        await callback_query.answer()
        await client.send_message(
            chat_id=user_id,
            text=language.get_text(lang_code, "language_changed", language_name=language_name)
        )
        
        # Save language preferences
        language.save_user_languages()
    else:
        # Language code not valid
        await callback_query.answer("Invalid language selection")

async def language_handler(client: pyrogram.Client, message: pyrogram.types.Message):
    """Handler for the /language command"""
    user_id = message.from_user.id
    log_user_data(message.from_user)
    user_lang = language.get_user_language(user_id)
    
    # Create inline keyboard with language options
    keyboard = pyrogram.types.InlineKeyboardMarkup(
        inline_keyboard=[
            [pyrogram.types.InlineKeyboardButton(
                text=name, 
                callback_data=f"lang_{code}"
            ) for code, name in list(language.AVAILABLE_LANGUAGES.items())[i:i+2]]
            for i in range(0, len(language.AVAILABLE_LANGUAGES), 2)
        ]
    )
    
    # Send language selection message
    await client.send_message(
        chat_id=user_id,
        text=language.get_text(user_lang, "language_selection"),
        reply_markup=keyboard
    )

async def tiktok_handler(client: pyrogram.Client, message: pyrogram.types.Message):
    # Log user data when they use the TikTok download feature
    log_user_data(message.from_user)
    
    userid = message.chat.id
    text = message.text
    msgid = message.id
    user_lang = language.get_user_language(userid)
    
    print(f"{userid} - {text}")
    
    # First set a "received" reaction
    await set_reaction(client, message, "👀")
    
    # Check cooldown
    current_time = time.time()
    if userid in user_cooldowns and (current_time - user_cooldowns[userid]) < COOLDOWN_TIME:
        remaining_time = int(COOLDOWN_TIME - (current_time - user_cooldowns[userid]))
        await client.send_message(
            chat_id=userid, 
            text=language.get_text(user_lang, "cooldown_message", seconds=remaining_time), 
            reply_to_message_id=msgid
        )
        # Update reaction to timer for cooldown
        await set_reaction(client, message, "😎")
        return
    user_cooldowns[userid] = current_time

    tiktok_url, error_key = extract_tiktok_url(text)
    if error_key:
        await client.send_message(
            chat_id=userid, 
            text=language.get_text(user_lang, error_key), 
            reply_to_message_id=msgid
        )
        await set_reaction(client, message, "👎")
        return

    # Update reaction to processing
    await set_reaction(client, message, "⚡")

    try:
        details = await utils.get_video_detail(tiktok_url)
        if len(details) < 6:
            raise ValueError("Unexpected response format from get_video_detail")

        video_id, author_id, author_username, video_url, images, cookies = details[:6]
    except Exception as e:
        await client.send_message(
            chat_id=userid, 
            text=language.get_text(user_lang, "video_details_error"), 
            reply_to_message_id=msgid
        )
        await set_reaction(client, message, "👎")
        print(f"Error fetching video details: {e}")
        return

    output = cwd.joinpath(f"{video_id}.mp4")
    progress_message = await client.send_message(
        chat_id=userid, 
        text=language.get_text(user_lang, "downloading_message")
    )

    try:
        if video_url:
            result = await tiktok_downloader.get_content(url=video_url, output=output, cookies=cookies)
        else:
            result = await tiktok_downloader.musicaldown(url=tiktok_url, output=output)

        retext = language.get_text(user_lang, "download_complete")
        
        # Create keyboard with translated button text
        rekey = pyrogram.types.InlineKeyboardMarkup(
            inline_keyboard=[
                [pyrogram.types.InlineKeyboardButton(
                    text=language.get_text(user_lang, "source_video_button"), 
                    url=tiktok_url
                )],
                [
                    pyrogram.types.InlineKeyboardButton(
                        text=language.get_text(user_lang, "check_channel_button"), 
                        url="https://t.me/qubit_bots"
                    ),
                    pyrogram.types.InlineKeyboardButton(
                        text=language.get_text(user_lang, "all_in_1_button"), 
                        callback_data="ReelsDownloader"
                    ),
                ],
            ]
        )

        await client.send_video(
            chat_id=userid, 
            video=output, 
            caption=retext, 
            reply_to_message_id=msgid, 
            reply_markup=rekey
        )
        await progress_message.delete()
        output.unlink(missing_ok=True)
        # If download successful, update reaction to check mark
        await set_reaction(client, message, "🤝")
    except Exception as e:
        await client.send_message(
            chat_id=userid, 
            text=language.get_text(user_lang, "download_error"), 
            reply_to_message_id=msgid
        )
        await set_reaction(client, message, "👎")
        print(f"Error during download: {e}")

async def help_handler(client: pyrogram.Client, message: pyrogram.types.Message):
    """Handler for the /help command"""
    user_id = message.chat.id
    log_user_data(message.from_user)
    user_lang = language.get_user_language(user_id)
    
    # Get help text in user's language
    help_text = language.get_text(user_lang, "help_text")
    
    await client.send_message(
        chat_id=user_id,
        text=help_text,
        parse_mode="markdown"
    )

async def main():
    print("Starting bot!")
    await bot.start()
    
    # Add the regular handlers
    bot.add_handler(pyrogram.handlers.MessageHandler(start_handler, pyrogram.filters.command(["start"])))
    bot.add_handler(pyrogram.handlers.MessageHandler(help_handler, pyrogram.filters.command(["help"])))
    bot.add_handler(pyrogram.handlers.MessageHandler(language_handler, pyrogram.filters.command(["language"])))
    bot.add_handler(pyrogram.handlers.MessageHandler(tiktok_handler, pyrogram.filters.regex(r"tiktok")))
    bot.add_handler(pyrogram.handlers.MessageHandler(list_users_handler, pyrogram.filters.command(["users"])))
    
    # Add broadcast handlers from the broadcast module
    broadcast_handlers = get_broadcast_handlers(broadcaster)
    for handler in broadcast_handlers:
        bot.add_handler(handler)
    
    # Add the general callback handler LAST, so broadcast callbacks are handled first
    bot.add_handler(pyrogram.handlers.CallbackQueryHandler(callback_handler))
    
    await pyrogram.idle()
    await bot.stop()

if __name__ == "__main__":
    bot.run(main())