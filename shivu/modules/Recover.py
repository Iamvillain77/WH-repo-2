import random
from datetime import datetime, timedelta
from telegram.ext import CommandHandler
from shivu import application, user_collection

COOLDOWN_PERIOD = timedelta(days=1)  # 24 hours cooldown
OWNER_IDS = [8019277081, 5909658683]  # Replace with actual owner IDs

# This function will handle the /dailycode command
async def daily_code(update, context):
    user_id = update.effective_user.id

    # Retrieve the user's data from the database
    user_data = await user_collection.find_one({'id': user_id})

    if user_data:
        last_claim = user_data.get('last_claim', None)
        balance_amount = user_data.get('balance', 0)

        # If the user has claimed before, check if the cooldown period has passed
        if last_claim:
            last_claim_time = datetime.fromisoformat(last_claim)
            if (datetime.utcnow() - last_claim_time) < COOLDOWN_PERIOD:
                remaining_time = COOLDOWN_PERIOD - (datetime.utcnow() - last_claim_time)
                remaining_time_str = await format_time_delta(remaining_time)
                await update.message.reply_text(f"You have already claimed your daily balance. Please wait {remaining_time_str} before claiming again.")
                return

        # Generate a random amount for the daily balance between 1000 and 5000
        daily_balance = random.randint(1000, 5000)

        # Update the user's balance and last claim time
        new_balance = balance_amount + daily_balance
        await user_collection.update_one(
            {'id': user_id},
            {'$set': {'last_claim': datetime.utcnow().isoformat()}, '$inc': {'balance': daily_balance}}
        )

        await update.message.reply_text(f"Congratulations! You have claimed your daily balance of {daily_balance} Gold coins. Your new balance is {new_balance} Gold coins.")
    else:
        await update.message.reply_text("You are not eligible to claim a daily balance. Please register first.")

# Format the remaining time into a readable format (e.g., 12h 34m 56s)
async def format_time_delta(delta):
    seconds = delta.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

# /recover command for owners to reset the cooldown
async def recover(update, context):
    user_id = update.effective_user.id

    # Check if the user is the owner
    if user_id not in OWNER_IDS:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    # Check if the user is replying to a message
    if not update.message.reply_to_message:
        await update.message.reply_text("You must reply to a user's message to recover their daily claim.")
        return

    # Get the user who is being recovered
    recipient_id = update.message.reply_to_message.from_user.id

    # Reset the recipient's last claim time to allow immediate daily claim
    await user_collection.update_one(
        {'id': recipient_id},
        {'$set': {'last_claim': None}}  # This resets the cooldown
    )

    await update.message.reply_text(f"Successfully reset the daily cooldown for user {recipient_id}. They can now claim their daily balance immediately.")

# Add the handlers for the /dailycode and /recover commands
application.add_handler(CommandHandler("dailycode", daily_code, block=False))
application.add_handler(CommandHandler("recover", recover, block=False))