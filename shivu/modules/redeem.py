@app.on_message(filters.command("redeem") & filters.private)
async def redeem_code(client, message: Message):
    try:
        # Extract the redeem code
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Please provide the redeem code.")
            return
        
        redeem_code = args[1].upper()

        # Check if the redeem code exists
        redeem_info = await db.redeem_codes.find_one({"code": redeem_code})

        if not redeem_info:
            await message.reply_text("Invalid redeem code. Please check the code and try again.")
            return
        
        if redeem_info["used"]:
            await message.reply_text("This redeem code has already been used.")
            return
        
        # Mark the code as used
        await db.redeem_codes.update_one({"code": redeem_code}, {"$set": {"used": True}})

        # Reward the user based on the reward type
        reward_type = redeem_info["reward_type"]
        
        if reward_type == "balance":
            # Add balance to the user's account (example: 100 balance)
            await user_collection.update_one(
                {"id": message.from_user.id},
                {"$inc": {"balance": 100}}  # Add 100 balance
            )
            await message.reply_text("You have redeemed a balance of 100!")
        
        elif reward_type == "character":
            # Give a random character to the user (for simplicity, using a fixed character ID)
            character = await collection.find_one({"id": "12345"})  # Example character ID
            
            if character:
                await user_collection.update_one(
                    {"id": message.from_user.id},
                    {"$push": {"characters": character}}
                )
                await message.reply_photo(photo=character["img_url"], caption=f"You have redeemed a character: {character['name']}")
            else:
                await message.reply_text("Character not found for redemption.")

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")