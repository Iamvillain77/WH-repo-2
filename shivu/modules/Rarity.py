from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, sudo_users, collection  # Assuming 'collection' is the MongoDB collection where characters are stored

RARITY_MAP = {
    1: "⚪ COMMON",
    2: "🟢 MEDIUM",
    3: "🟣 RARE",
    4: "🟡 LEGENDARY",
    5: "🏖️ HOT",
    6: "❄ COLD",
    7: "💞 LOVE",
    8: "🎃 SCARY",
    9: "🎄 CHRISTMAS",
    10: "✨ SPECIAL EDITION",
    11: "💫 SHINING",
    12: "🪽 ANGELIC",
    13: "🧬 MIX WORLD",
    14: "🔮 DELUXE EDITION",
    15: "🥵 MYSTIC",
    16: "👑 ROYAL",
    17: "👗 COSPLAY",
    18: "🌍 UNIVERSAL",
    19: "🎁 GIVEAWAY",
    20: "🎨 CUSTOM"
}

# /rarity command function
async def rarity(update: Update, context: CallbackContext):
    try:
        rarity_message = "Here are the available rarities and how many characters have been uploaded for each:\n\n"

        # Loop through each rarity and count the number of characters for each
        for rarity_id, rarity_name in RARITY_MAP.items():
            # Query the database to count how many characters have this rarity
            rarity_count = await collection.count_documents({'rarity': rarity_name})
            rarity_message += f"{rarity_id}: {rarity_name} - {rarity_count} characters uploaded\n"

        await update.message.reply_text(rarity_message)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Add /rarity command to the application
application.add_handler(CommandHandler("rarity", rarity))
