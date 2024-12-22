class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "5909658683"
    sudo_users = "5909658683", "8019277081", "5608779258", "6961368696", "1881562083", "8035449599", "7430528632"
    GROUP_ID = -1002311769574
    TOKEN = ""
    mongo_url = ""
    PHOTO_URL = ["https://files.catbox.moe/wy70cl.jpg", "https://files.catbox.moe/wy70cl.jpg"]
    SUPPORT_CHAT = "WH_SUPPORT_GC"
    UPDATE_CHAT = "iamvillain77"
    BOT_USERNAME = "@Waifu_World_Robot"
    CHARA_CHANNEL_ID = "-1002311769574"
    api_id = "26062263"
    api_hash = "f22fee8f0b782fbdf3a91a342763f56d"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
