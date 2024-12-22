from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from datetime import datetime, timedelta
from shivu import application, collection, user_collection

OWNER_IDS = [8019277081, 5909658683]  # Owner IDs list
SUPPORT_GROUP_CHAT_ID = -1001234567890  # Your support group chat ID
request_cooldown = {}  # Dictionary to store request cooldowns

# Command: /request <character_id>
async def request_character(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    # Check if the command is used in private chat or support group chat
    if update.message.chat.id != update.effective_user.id and update.message.chat.id != SUPPORT_GROUP_CHAT_ID:
        await update.message.reply_text("This command can only be used in the support group or in private messages.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Please provide the character ID you want to request. Example: /request 12345")
        return

    character_id = context.args[0]
    character = await collection.find_one({'id': character_id})

    if not character:
        await update.message.reply_text("Character not found.")
        return

    # Check for cooldown
    if user_id in request_cooldown:
        last_request_time = request_cooldown[user_id]
        cooldown_remaining = last_request_time + timedelta(hours=24) - datetime.utcnow()

        if cooldown_remaining > timedelta(seconds=0):
            # Send remaining time before the user can request again
            hours, remainder = divmod(cooldown_remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            await update.message.reply_text(f"You can request a character again in {hours}h {minutes}m {seconds}s.")
            return

    # Notify the owners about the request
    request_message = f"User {update.effective_user.first_name} (@{update.effective_user.username}) has requested character {character['name']} (ID: {character['id']}).\n\n"
    request_message += f"To approve: /approve {user_id} {character_id}\nTo deny: /deny {user_id} {character_id}"

    for owner_id in OWNER_IDS:
        try:
            await application.bot.send_message(owner_id, request_message)
        except Exception as e:
            print(f"Failed to send request to owner {owner_id}: {e}")

    # Update the user's last request time to enforce cooldown
    request_cooldown[user_id] = datetime.utcnow()

    await update.message.reply_text(f"Your request for {character['name']} has been sent to the owner for approval.")

# Command: /approve <user_id> <character_id>
async def approve_request(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    # Ensure that the command is used in the support group chat
    if update.message.chat.id != SUPPORT_GROUP_CHAT_ID:
        await update.message.reply_text("This command can only be used in the support group.")
        return

    if user_id not in OWNER_IDS:
        await update.message.reply_text("You are not authorized to approve requests.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Please provide both the user ID and character ID. Example: /approve 12345 67890")
        return

    requested_user_id = int(context.args[0])
    character_id = context.args[1]
    character = await collection.find_one({'id': character_id})

    if not character:
        await update.message.reply_text("Character not found.")
        return

    # Add the character to the user's collection
    await user_collection.update_one(
        {'id': requested_user_id},
        {'$push': {'characters': character}}
    )

    await update.message.reply_text(f"Character {character['name']} has been successfully added to user {requested_user_id}'s collection.")

    # Notify the user
    try:
        await application.bot.send_message(requested_user_id, f"Congratulations! Your request for {character['name']} has been approved and added to your collection.")
    except Exception as e:
        print(f"Failed to notify user {requested_user_id}: {e}")

# Command: /deny <user_id> <character_id>
async def deny_request(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    # Ensure that the command is used in the support group chat
    if update.message.chat.id != SUPPORT_GROUP_CHAT_ID:
        await update.message.reply_text("This command can only be used in the support group.")
        return

    if user_id not in OWNER_IDS:
        await update.message.reply_text("You are not authorized to deny requests.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Please provide both the user ID and character ID. Example: /deny 12345 67890")
        return

    requested_user_id = int(context.args[0])
    character_id = context.args[1]

    # Notify the user
    try:
        await application.bot.send_message(requested_user_id, f"Sorry, your request for character {character_id} has been denied.")
    except Exception as e:
        print(f"Failed to notify user {requested_user_id}: {e}")

    await update.message.reply_text(f"Request for character {character_id} has been denied for user {requested_user_id}.")

# Add command handlers to the bot
application.add_handler(CommandHandler("request", request_character))
application.add_handler(CommandHandler("approve", approve_request))
application.add_handler(CommandHandler("deny", deny_request))