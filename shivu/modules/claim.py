from datetime import datetime, timedelta
from telegram.ext import CommandHandler
from shivu import application, user_collection, collection
import random
import logging

# Enable logging for errors and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to check if the user has claimed today
async def has_claimed_today(user_id):
    try:
        user_data = await user_collection.find_one({'id': user_id})
        if user_data:
            last_claim = user_data.get('last_claim', None)
            if last_claim:
                # Check if the last claim was today or within the cooldown period
                cooldown_period = timedelta(days=1)  # 24 hours cooldown
                if datetime.utcnow() - last_claim < cooldown_period:
                    time_left = cooldown_period - (datetime.utcnow() - last_claim)
                    return False, time_left  # User cannot claim yet, return the time left
            # If there's no last claim or the cooldown has passed, user can claim
        return True, None
    except Exception as e:
        logger.error(f"Error in checking claim: {e}")
        return False, None

# Function to handle the claim command
async def claim(update, context):
    user_id = update.effective_user.id

    # Check if the user has claimed today
    claimed, time_left = await has_claimed_today(user_id)
    if not claimed and time_left:
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        await update.message.reply_text(
            f"You have already claimed your character today! Please wait {hours} hours and {minutes} minutes to claim again."
        )
        return

    # Get a random character from the collection
    character = await collection.aggregate([{"$sample": {"size": 1}}]).next()
    if character:
        try:
            # Add the character to the user's profile and update the claim time
            await user_collection.update_one(
                {'id': user_id},
                {'$push': {'characters': character}, '$set': {'last_claim': datetime.utcnow()}}
            )

            img_url = character['img_url']
            caption = (
                f"🎉 Congratulations! You have claimed a new character!\n\n"
                f"Name: {character['name']}\n"
                f"Rarity: {character['rarity']}\n"
                f"ID: {character['id']}"
            )

            # Send the character image and info to the user
            await update.message.reply_photo(photo=img_url, caption=caption)
        except Exception as e:
            logger.error(f"Error in updating user data or sending message: {e}")
            await update.message.reply_text("Oops! Something went wrong. Please try again later.")
    else:
        await update.message.reply_text("Oops! Could not fetch a character. Try again later.")

# Add the handler for the /claim command
application.add_handler(CommandHandler("claim", claim, block=False))
