import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, user_collection, collection, PHOTO_URL

# Dictionary to store the last used time of the command for each user
propose_cooldown = {}

async def propose(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    # Check cooldown
    if user_id in propose_cooldown:
        last_used = propose_cooldown[user_id]
        time_diff = datetime.utcnow() - last_used
        if time_diff < timedelta(minutes=5):  # 5-minute cooldown
            remaining_time = timedelta(minutes=5) - time_diff
            await update.message.reply_text(f"Please wait {remaining_time} before proposing again.")
            return

    # Choose a random character from the database or predefined list of characters
    cursor = collection.aggregate([
        {"$sample": {"size": 1}}  # Randomly pick one character
    ])
    character_data = await cursor.to_list(length=1)

    if not character_data:
        await update.message.reply_text("No characters available for proposal right now!")
        return

    character = character_data[0]
    character_name = character['name']
    character_img = character.get('img_url', PHOTO_URL[0])  # Fallback to default photo if no image URL found
    
    # Generate a random outcome: either rejection or acceptance
    outcome = random.choice([1, 2])

    if outcome == 1:
        # Rejected
        message = f"He/She rejected your proposal and ran away 😂"
        # You can customize this message to match the character's name or any extra details if needed
        message = f"<b>{character_name}</b> {message}"

    elif outcome == 2:
        # Accepted
        message = f"Congratulations! {character_name} has accepted your proposal! 💍🎉"
    
    # Send the response with character's image and message
    await update.message.reply_photo(photo=character_img, caption=message, parse_mode='HTML')

    # Update the last used time for the user to implement the cooldown
    propose_cooldown[user_id] = datetime.utcnow()

# Add /propose handler
application.add_handler(CommandHandler("propose", propose, block=False))