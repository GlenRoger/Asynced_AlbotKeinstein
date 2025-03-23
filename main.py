#####   IMPORTANT IMPORTS #####
#!/usr/bin/env python3
# main.py - Main entry point for the AlbertKeinstein Twitch bot


#Importing libraries
import asyncio
import logging
import websockets
import os
import re



# import signal
# import sys
# from typing import Dict, List, Optional, Set

#Importing files made for AlbotKeinstein
import config
import commands.command_handler as ch
# from utils.twitch_connection import TwitchConnection
# from utils.command_handler import CommandHandler
# from utils.event_sub import EventSubHandler
# from utils.logger import setup_logger

# # Setup logging
# logger = setup_logger(__name__)

### FROM HERE ON THERE WILLB E PROGRAMMING ##




# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("twitch_bot")



async def get_oauth_token():
    """Read OAuth token from file or prompt user if not found"""
    if os.path.exists(config.OAUTH_TOKEN_FILE):
        with open(config.OAUTH_TOKEN_FILE, 'r') as f:
            token = f.read().strip()
            logger.info("OAuth token loaded from file")
            return token
    else:
        logger.error(f"OAuth token file not found: {config.OAUTH_TOKEN_FILE}")
        logger.info("Please create this file with your Twitch OAuth token")
        logger.info("You can get a token from https://twitchapps.com/tmi/")
        # Exit gracefully
        print(f"Error: OAuth token file not found at {config.OAUTH_TOKEN_FILE}")
        print("Please create this file with your Twitch OAuth token (including 'oauth:' prefix)")
        print("You can get a token from https://twitchapps.com/tmi/")
        # Using SystemExit is a clean way to exit from inside a function
        raise SystemExit(1)



async def connect_to_twitch(token):
    """Connect to Twitch IRC via WebSocket"""
    # uri = f"wss://irc-ws.chat.twitch.tv:443"
    uri = f"{config.TWITCH_IRC_SERVER}:{config.TWITCH_IRC_PORT}"
    logger.info(f"######################## STARTING BOT ####################")
    logger.info(f"Connecting to Twitch IRC: {uri}")
    
    async with websockets.connect(uri) as websocket:
        # Send authentication commands
        await websocket.send(f"PASS {token}")
        await websocket.send(f"NICK {config.BOT_USERNAME}")
        
        # Join the channel
        await websocket.send(f"JOIN #{config.CHANNEL}")
        
        logger.info(f"Joined channel: #{config.CHANNEL}")
        
        # Main message loop #LOOOOOOOOOP
        try:
            while True:
                message = await websocket.recv()
                logger.info(f"Received: {message}")


            #For an overview over messages to deal with -> see file Twitch-Messages_to_deal_with.txt



                # Respond to PING with PONG to keep the connection alive
                if message.startswith("PING"):
                    await websocket.send("PONG :tmi.twitch.tv")
                    logger.info("Responded to PING")
                #Not important messages or info about albotkeinstein's log on
                elif message.startswith(":tmi.twitch.tv") or message.startswith(":albotkeinstein"):
                    logger.info(f"Ignoring/Not treating this message: {message}")
                else:


                    #Split gir oss: #[':coolingenwastaken!coolingenwastaken@coolingenwastaken.tmi.twitch.tv', 'PRIVMSG', '#coolingenwastaken', ':%hei\r\n']
                    split_chat = message.split(' ')


                    is_PRIVMSG = split_chat[1] == "PRIVMSG"
                    is_command = split_chat[3].startswith(':%')

                    if is_PRIVMSG and is_command:
                        split_chat[3] = split_chat[3][2:]
                        split_chat[-1] = split_chat[-1].rstrip()
                        command_rebuild = (' ').join(split_chat[3:])

                        username_sending_message = split_chat[2][1:]
                        print(username_sending_message)
                        # ptrn = r"^[a-zA-Z_+-øæåÆØÅ ]+$"

                        if ch.is_safe_message(command_rebuild, username_sending_message) and ch.is_safe_command(command_rebuild):
                            logger.info(f"Considered safe to check if it is a valid command: {message}")
                            ch.command_handler(command_rebuild)
                        else:
                            logger.info(f"I don't dare run this command: {message}")

                    elif is_PRIVMSG:
                        logger.info(f"Just a chat message: {message}")
                    else:
                        logger.info(f"In 'else' in main loop. This message came through.. why? {message}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.error("Connection closed")






async def main():
    """Main entry point for the bot"""
    try:
        token = await get_oauth_token()
        await connect_to_twitch(token)
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise

# Run the bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")