class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "5909658683"
    sudo_users = "5909658683", "8019277081", "5608779258", "6961368696", "1881562083", "8035449599", "7430528632"
    GROUP_ID = -1002311769574
    TOKEN = "7655351916:AAH_Sen1msMhGk8lNHyQTC1RWzMJfbjV77g"
    mongo_url = "mongodb+srv://waifubot1:<deathnote0p>@cluster0.km5g4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    PHOTO_URL = ["https://files.catbox.moe/wy70cl.jpg", "https://files.catbox.moe/wy70cl.jpg"]
    SUPPORT_CHAT = "WH_SUPPORT_GC"
    UPDATE_CHAT = "iamvillain77"
    BOT_USERNAME = "@Waifu_World_Robot"
    CHARA_CHANNEL_ID = "-1002311769574"
    api_id = "24061032"
    api_hash = "5ad029547f2eeb5a0b68b05d0db713be"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
