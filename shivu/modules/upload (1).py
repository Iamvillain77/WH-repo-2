import urllib.request
from pymongo import ReturnDocument
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, sudo_users, collection, db, CHARA_CHANNEL_ID, SUPPORT_CHAT
import logging

logging.basicConfig(level=logging.INFO)

WRONG_FORMAT_TEXT = """Wrong ❌ format... eg. /upload Img_url muzan-kibutsuji Demon-slayer 3

img_url character-name anime-name rarity-number

Rarity Map:
1: ⚪ COMMON
2: 🟢 MEDIUM
3: 🟣 RARE
4: 🟡 LEGENDARY
5: 🏖️ HOT
6: ❄ COLD
7: 💞 LOVE
8: 🎃 SCARY
9: 🎄 CHRISTMAS
10: ✨ SPECIAL EDITION
11: 💫 SHINING
12: 🪽 ANGELIC
13: 🧬 MIX WORLD
14: 🔮 DELUXE EDITION
15: 🥵 MYSTIC
16: 👑 ROYAL
17: 👗 COSPLAY
18: 🌍 UNIVERSAL
19: 🎁 GIVEAWAY
20: 🎨 CUSTOM
"""

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
    20: "🎨 CUSTOM",
}

# Function to get the next sequence number
async def get_next_sequence_number(sequence_name):
    try:
        sequence_collection = db.sequences
        sequence_document = await sequence_collection.find_one_and_update(
            {'_id': sequence_name},
            {'$inc': {'sequence_value': 1}},
            return_document=ReturnDocument.AFTER
        )
        if not sequence_document:
            await sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
            return 0
        return sequence_document['sequence_value']
    except Exception as e:
        logging.error(f"Error in get_next_sequence_number: {str(e)}")
        return None

# Function to upload a character
async def upload(update: Update, context: CallbackContext):
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('Ask Pro Otaku...')
        return

    try:
        args = context.args
        if len(args) != 4:
            await update.message.reply_text(WRONG_FORMAT_TEXT)
            return

        img_url, character_name, anime_name, rarity_num = args
        character_name = character_name.replace('-', ' ').title()
        anime_name = anime_name.replace('-', ' ').title()

        # Validate URL
        try:
            urllib.request.urlopen(img_url)
        except:
            await update.message.reply_text('Invalid URL.')
            return

        # Validate rarity
        try:
            rarity = RARITY_MAP[int(rarity_num)]
        except KeyError:
            await update.message.reply_text('Invalid rarity. Use numbers between 1 to 20.')
            return

        # Generate new ID
        char_id = str(await get_next_sequence_number('character_id')).zfill(2)

        character_data = {
            'img_url': img_url,
            'name': character_name,
            'anime': anime_name,
            'rarity': rarity,
            'id': char_id,
        }

        try:
            message = await context.bot.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=img_url,
                caption=f"<b>Character Name:</b> {character_name}\n"
                        f"<b>Anime Name:</b> {anime_name}\n"
                        f"<b>Rarity:</b> {rarity}\n"
                        f"<b>ID:</b> {char_id}\n"
                        f"Added by <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>",
                parse_mode='HTML'
            )
            character_data['message_id'] = message.message_id
            await collection.insert_one(character_data)
            await update.message.reply_text('CHARACTER ADDED....')
        except Exception as e:
            logging.error(f"Error in upload: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
    except Exception as e:
        logging.error(f"Error in upload: {str(e)}")
        await update.message.reply_text(f"Error: {str(e)}")

# Function to delete a character
async def delete(update: Update, context: CallbackContext):
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('Ask Pro Otaku...')
        return

    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text('Incorrect format. Use: /delete ID')
            return

        char_id = args[0]
        character = await collection.find_one_and_delete({'id': char_id})

        if character:
            await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character['message_id'])
            await update.message.reply_text('Deleted successfully.')
        else:
            await update.message.reply_text('Character not found.')
    except Exception as e:
        logging.error(f"Error in delete: {str(e)}")
        await update.message.reply_text(f"Error: {str(e)}")

# Function to update a character
async def update(update: Update, context: CallbackContext):
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('Ask Pro Otaku...')
        return

    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text('Incorrect format. Use: /update ID field new_value')
            return

        char_id, field, new_value = args
        character = await collection.find_one({'id': char_id})

        if not character:
            await update.message.reply_text('Character not found.')
            return

        if field not in ['img_url', 'name', 'anime', 'rarity']:
            await update.message.reply_text(f'Invalid field. Valid fields are: img_url, name, anime, rarity.')
            return

        if field == 'rarity':
            try:
                new_value = RARITY_MAP[int(new_value)]
            except KeyError:
                await update.message.reply_text('Invalid rarity number.')
                return

        await collection.find_one_and_update({'id': char_id}, {'$set': {field: new_value}})
        await update.message.reply_text('Character updated successfully.')
    except Exception as e:
        logging.error(f"Error in update: {str(e)}")
        await update.message.reply_text(f"Error: {str(e)}")

# Add handlers for commands
application.add_handler(CommandHandler("upload", upload))
application.add_handler(CommandHandler("delete", delete))
application.add_handler(CommandHandler("update", update))

# Start the bot
application.run_polling()
