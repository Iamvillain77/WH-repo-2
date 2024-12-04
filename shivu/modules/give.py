from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shivu import db, collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection
import asyncio
from shivu import shivuu as app
from shivu import sudo_users

DEV_LIST = [5909658683,8019277081]

async def give_character(receiver_id, character_id):
    character = await collection.find_one({'id': character_id})

    if character:
        try:
            await user_collection.update_one(
                {'id': receiver_id},
                {'$push': {'characters': character}}
            )

            img_url = character['img_url']
            caption = (
                f" Slave Added {receiver_id}\n"
                f"\n"
                f" Name : {character['name']}\n"
                f" Rarity : {character['rarity']}\n"
                f" ID : {character['id']}"
            )

            return img_url, caption
        except Exception as e:
            print(f"Error updating user: {e}")
            raise
    else:
        raise ValueError("Character not found.")

@app.on_message(filters.command(["give"]) & filters.reply & filters.user(DEV_LIST))
async def give_character_command(client, message):
    if not message.reply_to_message:
        await message.reply_text("You need to reply to a user's message to give a character!")
        return
    try:
        character_id = str(message.text.split()[1])
        receiver_id = message.reply_to_message.from_user.id

        result = await give_character(receiver_id, character_id)

        if result:
            img_url, caption = result
            await message.reply_photo(photo=img_url, caption=caption)
    except (IndexError, ValueError) as e:
        await message.reply_text(str(e))
    except Exception as e:
        print(f"Error in give_character_command: {e}")
        await message.reply_text("An error occurred while processing the command.")
