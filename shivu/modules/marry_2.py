import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from time import time
import shivu  # Import configuration from shivu.py

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variable to track the time of the command
user_times = {}

# Define the command handler for /marry
def marry_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id

    if user_id not in user_times:
        user_times[user_id] = time()  # Track when the user issued the command
        message = "💍 Congratulations! You've proposed to the bot! 🎉 You have 60 seconds to confirm your proposal."
        update.message.reply_text(message)
    else:
        # Check if 60 seconds have passed
        if time() - user_times[user_id] <= 60:
            update.message.reply_text(f"You already proposed to the bot, {user.first_name}. Please wait before proposing again.")
        else:
            user_times[user_id] = time()  # Reset the timer
            update.message.reply_text(f"💍 Congratulations! You've proposed to the bot again! 🎉 You have 60 seconds to confirm your proposal.")

    # Give the user another chance after 60 seconds
    context.job_queue.run_once(retry_proposal, 60, context=user_id)

# Function to handle retrying the proposal after 60 seconds
def retry_proposal(context: CallbackContext):
    user_id = context.job.context
    user_times.pop(user_id, None)  # Remove the user from the timer dictionary
    context.bot.send_message(chat_id=user_id, text="You didn't confirm in time. Please try again later!")

# Define the help command
def help_command(update: Update, context: CallbackContext):
    help_text = (
        "/marry - Propose to the bot!\n"
        "/hello - Greet the bot.\n"
        "/help - Get a list of available commands."
    )
    update.message.reply_text(help_text)

# Define the hello command
def hello_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text(f"Hello, {user.first_name}! How can I help you today?")

# Main function to set up the bot
def main():
    # Create the Updater and pass it your bot's token from shivu.py
    bot_token = shivu.BOT_TOKEN  # Use the bot token from shivu.py

    updater = Updater(bot_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the /marry, /help, and /hello commands
    dispatcher.add_handler(CommandHandler("marry", marry_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))

    # Register the job queue for timing purposes
    job_queue = updater.job_queue

    # Start the bot
    updater.start_polling()
    logger.info("Bot started and listening for commands.")
    updater.idle()

if __name__ == "__main__":
    main()