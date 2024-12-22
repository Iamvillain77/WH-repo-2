from datetime import datetime, timedelta
from telegram.ext import CommandHandler
from shivu import application, user_collection, collection
import random

# Function to check if the user has claimed today
async def has_claimed_today(user_id):
    user_data = await user_collection.find_one({'id': user_id})
    if user_data:
        last_claim = user_data.get('last_claim', None)
        if last_claim:
            # Check if the last claim was today
            if datetime.utcnow() - last_claim < timedelta(days=1):
                return True
    return False

# Function to handle the claim command
async def claim(update, context):
    user_id = update.effective_user.id

    # Check if the user has claimed today
    if await has_claimed_today(user_id):
        await update.message.reply_text("You have already claimed your character today! Come back tomorrow.")
        return

    # Get a random character from the collection
    character = await collection.aggregate([{"$sample": {"size": 1}}]).next()
    if character:
        # Add the character to the user's profile
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
    else:
        await update.message.reply_text("Oops! Something went wrong. Try again later.")

# Add the handler for the /claim command
application.add_handler(CommandHandler("claim", claim, block=False))