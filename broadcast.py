import os
import json
import time
import asyncio
from typing import Dict, List, Optional, Union, Any
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

class Broadcaster:
    """Class to handle all broadcasting functionality in the bot"""
    
    def __init__(self, users_log_file: str, admin_file: str):
        """Initialize the broadcaster with file paths for user tracking and admin management"""
        self.USERS_LOG_FILE = users_log_file
        self.ADMIN_FILE = admin_file
        self.pending_broadcast: Optional[Dict[str, Any]] = None
        
    def get_admin(self) -> Optional[int]:
        """Get the admin user ID from the admin file"""
        if os.path.exists(self.ADMIN_FILE):
            try:
                with open(self.ADMIN_FILE, "r") as file:
                    return json.load(file).get("admin_id")
            except json.JSONDecodeError:
                print(f"Error: Admin file is not valid JSON")
            except Exception as e:
                print(f"Error reading admin file: {e}")
        return None
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users from the users log file"""
        if os.path.exists(self.USERS_LOG_FILE):
            try:
                with open(self.USERS_LOG_FILE, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print(f"Error: Users log file is not valid JSON")
                return []
            except Exception as e:
                print(f"Error reading users log file: {e}")
                return []
        return []
    
    async def handle_broadcast_command(self, client: Client, message: Message) -> None:
        """Handle the /broadcast command - only accessible to admin"""
        user = message.from_user
        admin_id = self.get_admin()

        if user.id != admin_id:
            await client.send_message(chat_id=message.chat.id, text="❌ You don't have permission to use this command.")
            return

        # Check if there's a message to broadcast
        command_parts = message.text.split(' ', 1)
        if len(command_parts) < 2 and not message.reply_to_message:
            await client.send_message(
                chat_id=message.chat.id, 
                text=(
                    "To broadcast a message, either:\n\n"
                    "1. Use: /broadcast [your message]\n"
                    "2. Reply to any message with /broadcast\n\n"
                    "For media broadcasts, reply to a photo or video with /broadcast\n"
                    "For broadcasts with buttons, use the format:\n"
                    "/broadcast Text\n--btn--Button Text|http://example.com\n--btn--Button 2|http://example2.com"
                )
            )
            return
        
        # Get message content based on whether it's a reply or direct command
        broadcast_info = {}
        
        if message.reply_to_message:
            # Handle different types of replied content
            replied_msg = message.reply_to_message
            
            # Extract any caption from the replied message
            caption = replied_msg.caption or ""
            if len(command_parts) > 1:
                # If there's additional text with the command, use it instead of caption
                caption = command_parts[1]
            
            if replied_msg.photo:
                broadcast_info["type"] = "photo"
                broadcast_info["photo_id"] = replied_msg.photo.file_id
                broadcast_info["caption"] = caption
            elif replied_msg.video:
                broadcast_info["type"] = "video"
                broadcast_info["video_id"] = replied_msg.video.file_id
                broadcast_info["caption"] = caption
            else:
                # Text message reply
                broadcast_info["type"] = "text"
                broadcast_info["text"] = replied_msg.text or caption or "No text content found"
        else:
            # Direct command - parse text and check for button markup
            broadcast_text = command_parts[1]
            broadcast_info["type"] = "text"
            
            # Check for button syntax and parse if exists
            lines = broadcast_text.split('\n')
            message_text = []
            buttons = []
            
            for line in lines:
                if line.startswith("--btn--"):
                    # This line contains a button
                    try:
                        # Remove the --btn-- prefix and split into button text and URL
                        button_parts = line[7:].split('|', 1)
                        if len(button_parts) == 2:
                            text, url = button_parts
                            buttons.append({"text": text.strip(), "url": url.strip()})
                    except Exception as e:
                        print(f"Error parsing button: {e}")
                else:
                    message_text.append(line)
            
            broadcast_info["text"] = '\n'.join(message_text)
            if buttons:
                broadcast_info["buttons"] = buttons
        
        # Get users to broadcast to
        users = self.get_users()
        if not users:
            await client.send_message(chat_id=message.chat.id, text="No users to broadcast to.")
            return
        
        # Prepare confirmation message text
        if broadcast_info["type"] == "text":
            preview_text = broadcast_info["text"]
            if len(preview_text) > 200:
                preview_text = preview_text[:197] + "..."
                
            confirm_text = f"⚠️ You are about to send this message to {len(users)} users:\n\n{preview_text}"
            
            # Add info about buttons if present
            if "buttons" in broadcast_info and broadcast_info["buttons"]:
                button_text = "\n\n📝 With the following buttons:"
                for idx, btn in enumerate(broadcast_info["buttons"], 1):
                    button_text += f"\n{idx}. {btn['text']} -> {btn['url']}"
                confirm_text += button_text
        else:
            # Media broadcast
            media_type = broadcast_info["type"].capitalize()
            caption = broadcast_info["caption"] if broadcast_info["caption"] else "No caption"
            if len(caption) > 100:
                caption = caption[:97] + "..."
                
            confirm_text = f"⚠️ You are about to send a {media_type} with caption:\n\n{caption}\n\nTo {len(users)} users."
        
        # Create confirmation buttons
        confirm_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data="broadcast_confirm"),
                InlineKeyboardButton("❌ No", callback_data="broadcast_cancel")
            ]
        ])
        
        # Send confirmation message (with media preview for media broadcasts)
        try:
            if broadcast_info["type"] == "photo":
                confirm_msg = await client.send_photo(
                    chat_id=message.chat.id,
                    photo=broadcast_info["photo_id"],
                    caption=confirm_text,
                    reply_markup=confirm_markup
                )
            elif broadcast_info["type"] == "video":
                confirm_msg = await client.send_video(
                    chat_id=message.chat.id,
                    video=broadcast_info["video_id"],
                    caption=confirm_text,
                    reply_markup=confirm_markup
                )
            else:
                confirm_msg = await client.send_message(
                    chat_id=message.chat.id,
                    text=confirm_text,
                    reply_markup=confirm_markup
                )
            
            # Save broadcast info
            broadcast_info["users"] = users
            broadcast_info["confirm_msg_id"] = confirm_msg.id
            broadcast_info["chat_id"] = message.chat.id  # Store chat_id for updates
            
            self.pending_broadcast = broadcast_info
            print(f"Created broadcast confirmation with message ID: {confirm_msg.id}")
            
        except Exception as e:
            print(f"Error preparing broadcast: {e}")
            await client.send_message(
                chat_id=message.chat.id, 
                text=f"⚠️ Error preparing broadcast message: {str(e)}"
            )
    
    async def handle_broadcast_callback(self, client: Client, callback_query: CallbackQuery) -> bool:
        """
        Handle broadcast confirmation callbacks
        Returns True if the callback was handled, False otherwise
        """
        # Only handle broadcast callbacks
        if not callback_query.data.startswith("broadcast_"):
            return False
            
        print(f"Received broadcast callback: {callback_query.data}")
        
        user = callback_query.from_user
        admin_id = self.get_admin()

        if user.id != admin_id:
            await callback_query.answer("You don't have permission to use this feature.", show_alert=True)
            return True

        # Get the action from the callback data
        action = callback_query.data.split('_')[1]
        
        # Check if there is a pending broadcast
        if not self.pending_broadcast:
            await callback_query.answer("No pending broadcast found.", show_alert=True)
            return True
            
        # Validate we're interacting with the correct confirmation message
        if self.pending_broadcast["confirm_msg_id"] != callback_query.message.id:
            await callback_query.answer("This broadcast request is no longer valid.", show_alert=True)
            return True
        
        if action == "confirm":
            await self._execute_broadcast(client, callback_query)
        elif action == "cancel":
            await self._cancel_broadcast(client, callback_query)
            
        return True
        
    async def _execute_broadcast(self, client: Client, callback_query: CallbackQuery) -> None:
        """Execute the broadcast after confirmation"""
        try:
            # Start broadcasting
            await callback_query.answer("Broadcasting started...")
            
            # Edit the confirmation message to show progress
            progress_text = "🚀 Broadcasting message to all users...\nThis may take some time."
            try:
                if callback_query.message.photo:
                    await client.edit_message_caption(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.id,
                        caption=progress_text
                    )
                elif callback_query.message.video:
                    await client.edit_message_caption(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.id,
                        caption=progress_text
                    )
                else:
                    await client.edit_message_text(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.id,
                        text=progress_text
                    )
            except Exception as e:
                print(f"Error updating progress message: {e}")
            
            # Counter for successful and failed sends
            success_count = 0
            fail_count = 0
            
            # Prepare buttons if any
            reply_markup = None
            if "buttons" in self.pending_broadcast and self.pending_broadcast["buttons"]:
                keyboard = []
                row = []
                for btn in self.pending_broadcast["buttons"]:
                    # Create rows of 2 buttons each
                    if len(row) >= 2:
                        keyboard.append(row)
                        row = []
                    row.append(InlineKeyboardButton(btn["text"], url=btn["url"]))
                
                # Add any remaining buttons
                if row:
                    keyboard.append(row)
                
                reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Start sending messages to all users
            for user in self.pending_broadcast["users"]:
                try:
                    user_id = user["user_id"]
                    
                    if self.pending_broadcast["type"] == "text":
                        await client.send_message(
                            chat_id=user_id,
                            text=f"📢 BROADCAST MESSAGE\n\n{self.pending_broadcast['text']}",
                            reply_markup=reply_markup
                        )
                    elif self.pending_broadcast["type"] == "photo":
                        await client.send_photo(
                            chat_id=user_id,
                            photo=self.pending_broadcast["photo_id"],
                            caption=f"📢 BROADCAST\n\n{self.pending_broadcast['caption']}",
                            reply_markup=reply_markup
                        )
                    elif self.pending_broadcast["type"] == "video":
                        await client.send_video(
                            chat_id=user_id,
                            video=self.pending_broadcast["video_id"],
                            caption=f"📢 BROADCAST\n\n{self.pending_broadcast['caption']}",
                            reply_markup=reply_markup
                        )
                    
                    success_count += 1
                    # Add a small delay to avoid hitting rate limits
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Failed to send broadcast to user {user['user_id']}: {e}")
                    fail_count += 1
            
            # Update the confirmation message with results
            result_text = (
                f"✅ Broadcast completed!\n\n"
                f"📊 Statistics:\n"
                f"- Sent successfully: {success_count}\n"
                f"- Failed: {fail_count}\n"
                f"- Total users: {len(self.pending_broadcast['users'])}"
            )
            
            try:
                if callback_query.message.photo:
                    await client.edit_message_caption(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.id,
                        caption=result_text
                    )
                elif callback_query.message.video:
                    await client.edit_message_caption(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.id,
                        caption=result_text
                    )
                else:
                    await client.edit_message_text(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.id,
                        text=result_text
                    )
            except Exception as e:
                print(f"Error updating result message: {e}")
                # Fallback to sending a new message
                await client.send_message(
                    chat_id=callback_query.message.chat.id,
                    text=result_text
                )
        except Exception as e:
            print(f"Error during broadcast execution: {e}")
            try:
                await client.send_message(
                    chat_id=callback_query.message.chat.id,
                    text=f"⚠️ Error during broadcast: {str(e)}"
                )
            except:
                pass
        finally:
            # Clear the pending broadcast
            self.pending_broadcast = None
    
    async def _cancel_broadcast(self, client: Client, callback_query: CallbackQuery) -> None:
        """Cancel the broadcast"""
        await callback_query.answer("Broadcast cancelled.")
        
        # Edit the confirmation message
        cancel_text = "❌ Broadcast cancelled."
        try:
            if callback_query.message.photo:
                await client.edit_message_caption(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.id,
                    caption=cancel_text
                )
            elif callback_query.message.video:
                await client.edit_message_caption(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.id,
                    caption=cancel_text
                )
            else:
                await client.edit_message_text(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.id,
                    text=cancel_text
                )
        except Exception as e:
            print(f"Error updating cancel message: {e}")
        
        # Clear the pending broadcast
        self.pending_broadcast = None

# Create handler functions that can be registered with the bot

def get_broadcast_handlers(broadcaster: Broadcaster):
    """Return handlers that can be added to the bot"""
    
    broadcast_command = pyrogram.handlers.MessageHandler(
        broadcaster.handle_broadcast_command, 
        filters=filters.command(["broadcast"])
    )
    
    # The callback handler requires special handling since it needs to check
    # if the callback is for broadcast before processing
    async def callback_wrapper(client: Client, callback_query: CallbackQuery):
        if callback_query.data and callback_query.data.startswith("broadcast_"):
            await broadcaster.handle_broadcast_callback(client, callback_query)
    
    broadcast_callback = pyrogram.handlers.CallbackQueryHandler(
        callback_wrapper,
        filters=filters.regex(r"^broadcast_")
    )
    
    return [broadcast_command, broadcast_callback]