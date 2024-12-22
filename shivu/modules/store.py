import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler
from shivu import application, user_collection, db

# Predefined rarity price ranges
RARITY_PRICE_RANGES = {
    1: (2000, 10000),  # COMMON
    2: (2000, 10000),  # MEDIUM
    3: (2000, 10000),  # RARE
    4: (2000, 10000),  # LEGENDARY
    5: (1000000, 1500000),  # HOT
    6: (1000000, 1500000),  # COLD
    7: (1000000, 1500000),  # LOVE
    8: (1000000, 1500000),  # SCARY
    9: (1000000, 1500000),  # CHRISTMAS
    10: (20000, 40000),  # SPECIAL EDITION
    11: (22000, 44000),  # SHINING
    12: (24000, 48000),  # ANGELIC
    13: (26000, 52000),  # MIX WORLD
    14: (28000, 56000),  # DELUXE EDITION
    15: (30000, 60000),  # MYSTIC
    16: (32000, 64000)   # ROYAL
}

# Refresh cooldown period (24 hours)
REFRESH_COOLDOWN = timedelta(days=1)

async def store(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    # Retrieve the user's last store visit time and refresh time
    user_data = await user_collection.find_one({"id": user_id})
    last_store_visit = user_data.get('last_store_visit', None)
    last_refresh = user_data.get('last_refresh', None)
    
    if last_store_visit:
        # Check if the user can use the store based on the cooldown period
        if datetime.now() - last_store_visit < timedelta(days=1):
            time_left = timedelta(days=1) - (datetime.now() - last_store_visit)
            await update.message.reply_text(f"You can use the store again in {time_left}.")
            return

    # Get the characters (excluding Hot, Love, Cold, Scary, and Christmas rarities)
    characters = await db.characters.find({
        "rarity": {"$nin": [5, 6, 7, 8, 9]}  # Exclude these rarities from store
    }).to_list(length=3)

    # Prepare the keyboard for the user to choose which character they want to buy
    keyboard = []
    for character in characters:
        rarity = character['rarity']
        min_price, max_price = RARITY_PRICE_RANGES.get(rarity, (2000, 10000))
        price = random.randint(min_price, max_price)
        
        button_text = f"{character['name']} - {price} coins"
        callback_data = f"buy_{character['id']}_{price}"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Update the user's last store visit time
    await user_collection.update_one(
        {"id": user_id},
        {"$set": {"last_store_visit": datetime.now()}},
        upsert=True
    )
    
    await update.message.reply_text("Welcome to the store! Choose a character to purchase:", reply_markup=reply_markup)

async def refresh(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    # Retrieve the user's last refresh time
    user_data = await user_collection.find_one({"id": user_id})
    last_refresh = user_data.get('last_refresh', None)
    
    if last_refresh and datetime.now() - last_refresh < REFRESH_COOLDOWN:
        time_left = REFRESH_COOLDOWN - (datetime.now() - last_refresh)
        await update.message.reply_text(f"You can refresh the store again in {time_left}.")
        return

    # Get 3 random characters including Hot, Love, Cold, Scary, and Christmas rarities
    characters = await db.characters.find({
        "rarity": {"$in": [5, 6, 7, 8, 9]}  # Include these rarities for refresh
    }).to_list(length=3)

    # Prepare the keyboard for the user to choose which character they want to buy
    keyboard = []
    for character in characters:
        rarity = character['rarity']
        min_price, max_price = RARITY_PRICE_RANGES.get(rarity, (2000, 10000))
        price = random.randint(min_price, max_price)
        
        button_text = f"{character['name']} - {price} coins"
        callback_data = f"buy_{character['id']}_{price}"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Update the user's last refresh time
    await user_collection.update_one(
        {"id": user_id},
        {"$set": {"last_refresh": datetime.now()}},
        upsert=True
    )
    
    await update.message.reply_text("Store refreshed! Choose a new character to purchase:", reply_markup=reply_markup)

# Handle purchase selection
async def buy_character(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split("_")
    
    # Extract character info
    character_id = int(data[1])
    price = int(data[2])
    
    # Check the user's balance (this assumes a 'coins' field in the user collection)
    user_data = await user_collection.find_one({"id": user_id})
    if user_data and user_data.get("coins", 0) >= price:
        # Deduct the coins and add the character to the user's collection
        await user_collection.update_one(
            {"id": user_id},
            {"$inc": {"coins": -price}, "$push": {"characters": {"id": character_id}}}
        )
        await query.answer(f"Congrats! You have purchased {character_id} for {price} coins.")
    else:
        await query.answer("You do not have enough coins to purchase this character.")

# Add the store and refresh command handlers
application.add_handler(CommandHandler("store", store, block=False))
application.add_handler(CommandHandler("refresh", refresh, block=False))
application.add_handler(CallbackQueryHandler(buy_character, pattern=r"^buy_", block=False))