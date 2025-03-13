#!/usr/bin/env python3
# main.py - Main entry point for the AlbertKeinstein Twitch bot
import asyncio
import logging
import signal
import sys
from typing import Dict, List, Optional, Set

import config
from utils.twitch_connection import TwitchConnection
from utils.command_handler import CommandHandler
from utils.event_sub import EventSubHandler
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

class AlbertKeinsteinBot:
    """Main bot class that handles the core functionality and delegation."""
    
    def __init__(self):
        self.twitch_connection = TwitchConnection(
            username=config.BOT_USERNAME,
            oauth_token=config.OAUTH_TOKEN,
            channel=config.CHANNEL
        )
        self.command_handler = CommandHandler(self.twitch_connection)
        self.event_sub = EventSubHandler(self.twitch_connection)
        
        # Track bot state
        self.is_running = False
        self.moderators: Set[str] = set()
        self.vips: Set[str] = set()
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Handle termination signals for graceful shutdown."""
        logger.info(f"Received signal {sig}, shutting down...")
        self.stop()
    
    async def start(self):
        """Start the bot and connect to Twitch."""
        if self.is_running:
            logger.warning("Bot is already running")
            return
        
        logger.info(f"Starting AlbertKeinstein bot in channel #{config.CHANNEL}")
        self.is_running = True
        
        # Connect to Twitch and start listening
        await self.twitch_connection.connect()
        
        # Initialize commands
        await self.command_handler.load_commands()
        
        # Start processing messages
        await self._message_loop()
    
    def stop(self):
        """Stop the bot and close connections."""
        if not self.is_running:
            return
        
        logger.info("Shutting down bot...")
        self.is_running = False
        
        # Event loop will detect is_running=False and exit cleanly
    
    async def _message_loop(self):
        """Main message processing loop."""
        logger.info("Starting message processing loop")
        
        try:
            while self.is_running:
                # Get next message from the connection
                raw_message = await self.twitch_connection.read_message()
                
                if not raw_message:
                    # Empty message, probably connection closed
                    if self.is_running:
                        logger.warning("Connection lost, attempting to reconnect...")
                        await self.twitch_connection.reconnect()
                    continue
                
                # Handle different message types
                if "PING" in raw_message:
                    await self.twitch_connection.send_pong()
                elif "PRIVMSG" in raw_message:
                    await self._handle_privmsg(raw_message)
                elif "NOTICE" in raw_message:
                    logger.info(f"Twitch notice: {raw_message}")
                elif "USERSTATE" in raw_message or "ROOMSTATE" in raw_message:
                    # Track channel state
                    pass
                elif "353" in raw_message:  # NAMES list (chatters in channel)
                    # Could parse for initial user list, but Twitch doesn't send full list here
                    pass
                elif "JOIN" in raw_message or "PART" in raw_message:
                    # Track users joining/leaving, if needed
                    pass
                elif "CLEARCHAT" in raw_message:
                    # Handle timeouts/bans
                    pass
                
                # Special cases for raid or stream end (from your current progress notes)
                if ":tmi.twitch.tv NOTICE" in raw_message and ("hosting" in raw_message.lower() or "raid" in raw_message.lower()):
                    logger.info("Stream is hosting or raiding, shutting down bot")
                    self.stop()
                    break
        
        except asyncio.CancelledError:
            logger.info("Message loop was cancelled")
        except Exception as e:
            logger.error(f"Error in message loop: {e}", exc_info=True)
        finally:
            # Ensure connection is closed
            await self.twitch_connection.disconnect()
            logger.info("Bot has been shut down")
    
    async def _handle_privmsg(self, raw_message: str):
        """Handle chat messages from users."""
        try:
            # Parse the message 
            username, message_content = self.twitch_connection.parse_privmsg(raw_message)
            
            if not username or not message_content:
                return
            
            # Check for bot command
            if message_content.startswith(config.COMMAND_PREFIX):
                await self._handle_command(username, message_content)
            else:
                # Regular message, could process for custom features
                pass
                
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def _handle_command(self, username: str, message_content: str):
        """Process bot commands."""
        # Special case - bot rest command (from your current progress notes)
        if message_content.lower() == f"{config.COMMAND_PREFIX}albotrest":
            is_moderator = username.lower() in self.moderators or username.lower() == config.CHANNEL.lower()
            if is_moderator:
                await self.twitch_connection.send_chat_message("Going to sleep now. Good night!")
                logger.info(f"Bot shutdown requested by moderator {username}")
                self.stop()
                return
        
        # Handle other commands
        await self.command_handler.process_command(username, message_content)

async def main():
    """Entry point for the bot."""
    bot = AlbertKeinsteinBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
    finally:
        # Ensure the bot is stopped
        bot.stop()

if __name__ == "__main__":
    asyncio.run(main())