import random
import string
from pyrogram import Client, filters
from pyrogram.types import Message
from shivu import user_collection, collection, db

# Add your dev user IDs
DEV_LIST = [8019277081, 5909658683]

# Function to generate a redeem code
def generate_redeem_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))  # 8-character code
    return code

@app.on_message(filters.command("gen") & filters.user(DEV_LIST))
async def generate_redeem_code_command(client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Please specify the reward type: balance or character.")
            return
        
        reward_type = args[1].lower()
        
        if reward_type not in ["balance", "character"]:
            await message.reply_text("Invalid reward type. Please specify either 'balance' or 'character'.")
            return

        redeem_code = generate_redeem_code()

        redeem_info = {
            "code": redeem_code,
            "reward_type": reward_type,
            "used": False
        }
        await db.redeem_codes.insert_one(redeem_info)

        await message.reply_text(f"Redeem code generated: {redeem_code}\nType: {reward_type}")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")


@app.on_message(filters.command("genredeem") & filters.user(DEV_LIST))
async def genredeem_code(client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Please provide the redeem code.")
            return

        redeem_code = args[1]
        code_info = await db.redeem_codes.find_one({"code": redeem_code})

        if not code_info:
            await message.reply_text("Invalid code!")
            return

        if code_info['used']:
            await message.reply_text("This code has already been used!")
            return

        if code_info["reward_type"] == "balance":
            await message.reply_text(f"You've received balance!")
        elif code_info["reward_type"] == "character":
            await message.reply_text(f"You've received a character!")

        await db.redeem_codes.update_one({"code": redeem_code}, {"$set": {"used": True}})
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
