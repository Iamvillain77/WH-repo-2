import logging
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import random
from termcolor import colored

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define the command handler for /marry
def marry_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    bot_name = "Waifu_World_Robot"  # Replace with the actual bot name if needed

    # Check if the command is directed at the bot
    if context.args and context.args[0] == f"@{bot_name}":
        message = f"💍 Congratulations, {user.first_name}! You've proposed to {bot_name}. 🎉"
        update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"User {user.first_name} proposed to {bot_name}")
    else:
        update.message.reply_text(f"You need to tag me (@{bot_name}) to use this command properly!")

# Define the help command
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "*Help Menu*\n\n"
        "/marry @Waifu_World_Robot - Propose to the bot!\n"
        "/hello - Receive a greeting from the bot.\n"
        "/random - Get a random response!\n"
        "/color - See a color-themed response.\n",
        parse_mode=ParseMode.MARKDOWN
    )
    logger.info(f"Help command accessed by {update.message.from_user.first_name}")

# Define the hello command
def hello_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text(f"Hello, {user.first_name}! How can I help you today?", parse_mode=ParseMode.MARKDOWN)
    logger.info(f"Greeted {user.first_name}")

# Define the random command to give random responses
def random_command(update: Update, context: CallbackContext):
    responses = [
        "Here's a random fact: The Eiffel Tower can be 15 cm taller during the summer.",
        "Random quote: 'The only way to do great work is to love what you do.' – Steve Jobs",
        "Did you know? A group of flamingos is called a 'flamboyance'."
    ]
    response = random.choice(responses)
    update.message.reply_text(response)
    logger.info(f"Random response given to {update.message.from_user.first_name}")

# Define the color command that demonstrates color in terminal output
def color_command(update: Update, context: CallbackContext):
    message = colored("This is a colorful response!", "red", attrs=["bold"])
    update.message.reply_text(message)
    logger.info("Colorful response given.")

# Define error handler for debugging
def error(update: Update, context: CallbackContext):
    logger.warning(f"Update {update} caused error {context.error}")
    update.message.reply_text("An error occurred. Please try again later.")

# Define a function to handle unknown messages
def unknown_message(update: Update, context: CallbackContext):
    update.message.reply_text("I don't understand that. Try using /help to see available commands.")
    logger.info(f"Unknown message from {update.message.from_user.first_name}")

def main():
    # Create the Updater and pass it your bot's token
    bot_token = "7655351916:AAGp7V4n00frq--ZKZi10u-DKdTdT807Pac"  # Replace with your actual token

    updater = Updater(bot_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler("marry", marry_command, pass_args=True))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))
    dispatcher.add_handler(CommandHandler("random", random_command))
    dispatcher.add_handler(CommandHandler("color", color_command))

    # Register message handlers
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, unknown_message))

    # Register error handler
    dispatcher.add_error_handler(error)

    # Start the bot
    updater.start_polling()
    logger.info(colored("Bot started. Listening for commands...", "green"))
    updater.idle()

if __name__ == "__main__":
    main()