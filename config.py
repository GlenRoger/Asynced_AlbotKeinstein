# config.py

OVERLAY_TEXT_HEIGHT = 80
OVERLAY_GIF_HEIGHT  = 270

OVERLAY_WIDTH       = 480
OVERLAY_HEIGHT      = OVERLAY_TEXT_HEIGHT + OVERLAY_GIF_HEIGHT


#Set who can do some certain commands to Albert Keinstein
TSTWTMEMBERS_ONLY = True
TSTWTMEMBERS = ["thestreamteamwastaken", "coolingenwastaken", "kyllingpews", "nurseiplier", "dad__76", "themonkeytea", "krishli", "raivdaiv"]
AUTOMATIC_SHOUTOUT_LIST = ["phextheflex", "jarlspock", "verstoppel", "pnkyfisk", "muffin_no", "ectovibs", "hi_kalaan", "uvq3tsa", "queenvegan", "raeasakura", "taterthotplays"]   #Use lower case!!

PREFIX_FOR_BOT_TO_READ = '%'


# Twitch IRC server
TWITCH_IRC_SERVER   =   "wss://irc-ws.chat.twitch.tv"
TWITCH_IRC_PORT     =   443


# Twitch channel to connect to
CHANNEL = "TheStreamTeamWasTaken"
# CHANNEL = "TheStreamTeamWasTesting"
# CHANNEL = "CoolingenWasTaken"
# CHANNEL = "AlBotKeinStein"

# Bot's Twitch username
BOT_USERNAME = "AlBotKeinStein"

# Path to the file containing the OAuth token
OAUTH_TOKEN_FILE = "../ToAblertK.txt"
CLIENT_ID_FILE   = "../ToAlbotC.txt"

OAUTH_TOKEN_FILE_2 = "../toTSTWT.txt"
CLIENT_ID_FILE_2   = "../toTSTWTC.txt"

#Media storage
MEDIA_FOLDER        = "overlay_media/"
MEDIA_FOLDER_GIF    = "overlay_media/gifs/"
MEDIA_FOLDER_SOUNDS = "overlay_media/SOUNDS/"

#Tenor gif
TENOR_API_KEY       = "../TenorApiKey.txt"
TENOR_CLIENT_NAME   = "AlBotKeinStein"