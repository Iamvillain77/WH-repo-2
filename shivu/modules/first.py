import random
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import user_collection

# Rarities and their probabilities
def assign_rarity():
    rarities = ["Common", "Rare", "Epic", "Legendary"]
    weights = [50, 30, 15, 5]
    return random.choices(rarities, weights=weights, k=1)[0]

async def first_character(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    # Check if the user already got their first character
    user = await user_collection.find_one({'id': user_id})
    if user and 'first_character' in user:
        await update.message.reply_text('You have already received your first character! ❌️')
        return

    # Select a random character and assign rarity
    characters = await collection.find({}).to_list(length=None)  # Your character collection
    character = random.choice(characters)
    rarity = assign_rarity()

    # Update user data with the first character and rarity
    await user_collection.update_one(
        {'id': user_id},
        {'$set': {'first_character': character, 'rarity': rarity}},
        upsert=True
    )

    # Add the character to their harem
    await user_collection.update_one(
        {'id': user_id},
        {'$push': {'characters': character}},
        upsert=True
    )

    await update.message.reply_text(
        f'You have received your first character! 🎉\n\n'
        f'Character: {character["name"]}\n'
        f'Rarity: {rarity}\n'
        f'It has been added to your harem! Use /harem to see your collection.'
    )

# Add command handler to the bot
def main():
    application.add_handler(CommandHandler("first", first_character, block=False))
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
