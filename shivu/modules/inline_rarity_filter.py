import re
import time
from html import escape
from cachetools import TTLCache
from pymongo import MongoClient, ASCENDING
from telegram import Update, InlineQueryResultPhoto
from telegram.ext import InlineQueryHandler, CallbackContext, CommandHandler 
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from shivu import user_collection, collection, application, db


# MongoDB Indexes
db.characters.create_index([('id', ASCENDING)])
db.characters.create_index([('anime', ASCENDING)])
db.characters.create_index([('img_url', ASCENDING)])

# User collection indexes
db.user_collection.create_index([('characters.id', ASCENDING)])
db.user_collection.create_index([('characters.name', ASCENDING)])
db.user_collection.create_index([('characters.img_url', ASCENDING)])

# Caching
all_characters_cache = TTLCache(maxsize=10000, ttl=36000)
user_collection_cache = TTLCache(maxsize=10000, ttl=60)

# Rarity map
rarity_map = {
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
    16: "👑 ROYAL"
}

async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    # Extract rarity filter if it exists (e.g., "legendary", "hot")
    rarity_filter = None
    rarity_keyword = None
    for rarity in rarity_map.values():
        if query.lower().startswith(rarity.lower()):
            rarity_filter = [key for key, value in rarity_map.items() if value.lower() == rarity.lower()][0]
            rarity_keyword = rarity
            query = query[len(rarity):].strip()
            break

    # If it's a collection search
    if query.startswith('collection.'):
        user_id, *search_terms = query.split(' ')[0].split('.')[1], ' '.join(query.split(' ')[1:])
        if user_id.isdigit():
            if user_id in user_collection_cache:
                user = user_collection_cache[user_id]
            else:
                user = await user_collection.find_one({'id': int(user_id)})
                user_collection_cache[user_id] = user

            if user:
                all_characters = list({v['id']:v for v in user['characters']}.values())
                if search_terms:
                    regex = re.compile(' '.join(search_terms), re.IGNORECASE)
                    all_characters = [character for character in all_characters if regex.search(character['name']) or regex.search(character['anime'])]
                
                # Apply rarity filter if set
                if rarity_filter:
                    all_characters = [char for char in all_characters if char.get('rarity') == rarity_filter]

            else:
                all_characters = []
        else:
            all_characters = []
    else:
        # Generic search for all characters with rarity filter
        if query:
            regex = re.compile(query, re.IGNORECASE)
            all_characters = list(await collection.find({"$or": [{"name": regex}, {"anime": regex}]}).to_list(length=None))
        else:
            if 'all_characters' in all_characters_cache:
                all_characters = all_characters_cache['all_characters']
            else:
                all_characters = list(await collection.find({}).to_list(length=None))
                all_characters_cache['all_characters'] = all_characters

        # Apply rarity filter if provided
        if rarity_filter:
            all_characters = [char for char in all_characters if char.get('rarity') == rarity_filter]

    # Paginate characters
    characters = all_characters[offset:offset+50]
    if len(characters) > 50:
        characters = characters[:50]
        next_offset = str(offset + 50)
    else:
        next_offset = str(offset + len(characters))

    results = []
    for character in characters:
        global_count = await user_collection.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})

        # Set caption based on rarity and collection context
        if query.startswith('collection.'):
            user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])
            caption = f"<b> Look At <a href='tg://user?id={user['id']}'>{(escape(user.get('first_name', user['id'])))}</a>'s Character</b>\n\n🌸: <b>{character['name']} (x{user_character_count})</b>\n🏖️: <b>{character['anime']} ({user_anime_characters}/{anime_characters})</b>\n<b>{rarity_map.get(character['rarity'], 'Unknown')}</b>\n\n<b>🆔️:</b> {character['id']}"
        else:
            caption = f"<b>Look At This Character !!</b>\n\n🌸:<b> {character['name']}</b>\n🏖️: <b>{character['anime']}</b>\n<b>{rarity_map.get(character['rarity'], 'Unknown')}</b>\n🆔️: <b>{character['id']}</b>\n\n<b>Globally Guessed {global_count} Times...</b>"
        
        results.append(
            InlineQueryResultPhoto(
                thumbnail_url=character['img_url'],
                id=f"{character['id']}_{time.time()}",
                photo_url=character['img_url'],
                caption=caption,
                parse_mode='HTML'
            )
        )

    await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

application.add_handler(InlineQueryHandler(inlinequery, block=False))