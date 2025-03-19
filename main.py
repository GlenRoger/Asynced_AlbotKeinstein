#####   IMPORTANT IMPORTS #####
#!/usr/bin/env python3
# main.py - Main entry point for the AlbertKeinstein Twitch bot


#Importing libraries
import asyncio
import logging
import websockets
import os



# import signal
# import sys
# from typing import Dict, List, Optional, Set

#Importing files made for AlbotKeinstein
import config
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
    logger.info(f"Connecting to Twitch IRC: {uri}")
    
    async with websockets.connect(uri) as websocket:
        # Send authentication commands
        await websocket.send(f"PASS {token}")
        await websocket.send(f"NICK {config.BOT_USERNAME}")
        
        # Join the channel
        await websocket.send(f"JOIN #{config.CHANNEL}")
        
        logger.info(f"Joined channel: #{config.CHANNEL}")
        
        # Main message loop
        try:
            while True:
                message = await websocket.recv()
                logger.info(f"Received: {message}")
                
                # Respond to PING with PONG to keep the connection alive
                if message.startswith("PING"):
                    await websocket.send("PONG :tmi.twitch.tv")
                    logger.info("Responded to PING")
        
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