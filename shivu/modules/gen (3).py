import random
import string
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shivu import db, collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection
import asyncio
from shivu import shivuu as app
from shivu import sudo_users

DEV_LIST = [8019277081, 5909658683]

# Function to generate redeem code
def generate_redeem_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# Function to handle balance addition
async def add_balance(user_id, amount):
    user = await user_collection.find_one({'id': user_id})

    if user:
        new_balance = user.get('balance', 0) + amount
        await user_collection.update_one(
            {'id': user_id},
            {'$set': {'balance': new_balance}},
            upsert=True
        )
        return new_balance
    else:
        raise ValueError("User not found.")

# Function to handle character generation
async def gen_character(user_id, character_id):
    character = await collection.find_one({'id': character_id})

    if character:
        # Adding character to user collection
        await user_collection.update_one(
            {'id': user_id},
            {'$push': {'characters': character}},
            upsert=True
        )

        img_url = character['img_url']
        caption = (
            f"Character Generated for {user_id}!\n"
            f"\n"
            f"Name: {character['name']}\n"
            f"Rarity: {character['rarity']}\n"
            f"ID: {character['id']}"
        )

        return img_url, caption
    else:
        raise ValueError("Character not found.")

@app.on_message(filters.command(["gen"]) & filters.user(DEV_LIST))
async def gen_command(client, message):
    try:
        args = message.text.split()[1:]

        if not args:
            await message.reply_text("Invalid command format.")
            return

        if args[0] == "balance":
            if len(args) != 3:
                await message.reply_text("Usage: /gen balance <amount> <quantity>")
                return

            amount = float(args[1])
            quantity = int(args[2])
            user_id = message.from_user.id

            # Generate redeem code
            redeem_code = generate_redeem_code()

            # Store redeem code in the database with amount and quantity
            await db.redeem_codes.insert_one({
                'code': redeem_code,
                'amount': amount,
                'quantity': quantity,
                'used': False
            })

            # Send balance info and redeem code to the admin
            await message.reply_text(f"Generated code: {redeem_code}\n"
                                     f"Amount: {amount}\n"
                                     f"Quantity: {quantity}\n"
                                     f"Use this code to redeem: /redeem {redeem_code}")

        elif args[0] == "character":
            if len(args) != 3:
                await message.reply_text("Usage: /gen character <id> <quantity>")
                return

            character_id = str(args[1])
            quantity = int(args[2])
            user_id = message.from_user.id

            # Generate the character for the user
            img_url, caption = await gen_character(user_id, character_id)

            # Generate redeem code for character
            redeem_code = generate_redeem_code()

            # Store redeem code for character in the database
            await db.redeem_codes.insert_one({
                'code': redeem_code,
                'character_id': character_id,
                'quantity': quantity,
                'used': False
            })

            await message.reply_text(f"Character generated successfully! Use this code to redeem your character: /redeem {redeem_code}")
            await message.reply_photo(photo=img_url, caption=caption)

        else:
            await message.reply_text("Invalid argument. Use 'balance' or 'character'.")

    except ValueError as e:
        await message.reply_text(str(e))
    except Exception as e:
        print(f"Error in /gen command: {e}")
        await message.reply_text("An error occurred while processing the command.")

# Function to handle redeeming of the code
@app.on_message(filters.command(["redeem"]))
async def redeem_command(client, message):
    try:
        redeem_code = message.text.split()[1]
        user_id = message.from_user.id

        # Check if redeem code exists and has quantity > 0
        code_data = await db.redeem_codes.find_one({'code': redeem_code, 'quantity': {'$gt': 0}})

        if code_data:
            if 'amount' in code_data:
                # Process balance redeem
                amount = code_data['amount']
                new_balance = await add_balance(user_id, amount)

                # Decrement the quantity
                new_quantity = code_data['quantity'] - 1
                await db.redeem_codes.update_one(
                    {'code': redeem_code},
                    {'$set': {'quantity': new_quantity}}
                )

                await message.reply_text(f"Redeem successful! {amount} added to your balance. New balance: {new_balance}.\nRemaining Quantity: {new_quantity}")

            elif 'character_id' in code_data:
                # Process character redeem
                character_id = code_data['character_id']
                img_url, caption = await gen_character(user_id, character_id)

                # Decrement the quantity
                new_quantity = code_data['quantity'] - 1
                await db.redeem_codes.update_one(
                    {'code': redeem_code},
                    {'$set': {'quantity': new_quantity}}
                )

                await message.reply_photo(photo=img_url, caption=caption)
                await message.reply_text(f"Character redeemed successfully!\nRemaining Quantity: {new_quantity}")

        else:
            await message.reply_text("Invalid or exhausted redeem code.")
    except IndexError:
        await message.reply_text("Please provide a redeem code.")
    except Exception as e:
        print(f"Error in redeem command: {e}")
        await message.reply_text("An error occurred while processing the redeem.")
