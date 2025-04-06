import asyncio
import config
import websockets
import os
import utils.send_message as sm
import commands.command_handler as ch

class TwitchConnection:

    def __init__(self, logger):
        self.logger_prefix = "utils/TwitchConnection=>"
        self.logger = logger
        self.websocket = ""

        self.run_loop = True

        self.send_messsage  = sm.Message_sending_central(self.logger)
        self.commands       = ch.Command_central(self.logger)

        self.alternative_respond = ""

        #If true respond to all commands, if not just repsond to advanced ones!
        self.isNotSilenced = True
        
    async def get_oauth_token(self):
        """Read OAuth token from file or prompt user if not found"""

        current_log_prefix = self.logger_prefix + "get_oauth_token:"

        if os.path.exists(config.OAUTH_TOKEN_FILE):
            with open(config.OAUTH_TOKEN_FILE, 'r') as f:
                token = f.read().strip()
                self.logger.info(f"{current_log_prefix}OAuth token loaded from file")
                return token
        else:
            # Exit gracefully
            self.logger.error(f"{current_log_prefix}OAuth token file not found: {config.OAUTH_TOKEN_FILE}")
            self.logger.info(f"{current_log_prefix}Please create this file with your Twitch OAuth token")
            self.logger.info(f"{current_log_prefix}You can get a token from https://twitchapps.com/tmi/")
            raise SystemExit(1)

    def commanded_change(self, change_this):
        current_log_prefix = self.logger_prefix + "commanded_change:"

        if (change_this.upper() == 'SLEEP' or change_this.upper() == 'SILENCE'):
            if self.isNotSilenced:
                self.logger.info(f"{current_log_prefix}SLEEP MODE ACTIVATED!")
                self.isNotSilenced = False
                return True
            else:
                self.logger.info(f"{current_log_prefix}SLEEP MODE -ALREADY- ACTIVATED!")
                self.alternative_respond = "AlbotKeinstein is already sleeping.. shhhh! ;)"
                return False

        if change_this.upper() == 'WAKEUP':
            if not self.isNotSilenced:
                self.isNotSilenced = True
                self.logger.info(f"{current_log_prefix}SLEEP MODE DE-ACTIVATED!")
                return True
            else:
                self.alternative_respond = "I'm not sleeping, you're sleeping! :P"
                self.logger.info(f"{current_log_prefix}SLEEP MODE -ALREADY- DE-ACTIVATED!")
                return False

        
        if change_this.upper() == 'REPEAT':
            self.logger.info(f"{current_log_prefix}WILLL REPEAT!")
            #ADD SOMETHING HERE!
            return True

        if change_this.upper() == 'ALBOTREST' or change_this.upper() == 'SHUTDOWN' or change_this.upper() == 'QUIT':
            self.logger.info(f"{current_log_prefix}SHUTTING DOWN!")
            self.run_loop = False
            return True


    #THIS FUNCTION SHOULD PROBABLY BEEN IN ALBOTBRAIN.PY???
    async def start_messsage_loop(self):
        """Connect to Twitch IRC via WebSocket and analysing the Twitch chat"""

        current_log_prefix = self.logger_prefix +"start_messsage_loop:"

        uri = f"{config.TWITCH_IRC_SERVER}:{config.TWITCH_IRC_PORT}"

        self.logger.info(f"{current_log_prefix}Connecting to Twitch IRC: {uri}")

        token = await self.get_oauth_token()

        async with websockets.connect(uri) as self.websocket:
            # Send authentication commands
            await self.websocket.send(f"PASS {token}")
            await self.websocket.send(f"NICK {config.BOT_USERNAME}")
            
            # Join the channel
            await self.websocket.send(f"JOIN #{config.CHANNEL}")
            
            self.logger.info(f"{current_log_prefix}Joined channel: #{config.CHANNEL}")

            await self.sending_msg_to_chat("AlbotKeinstein up and running! <3")

            try:
                while self.run_loop:
                    # self.logger.info(f"{current_log_prefix}Inside while loop.. active.")

                    message = await self.websocket.recv()

                    # Respond to PING with PONG to keep the connection alive
                    if message.startswith("PING"):
                        await self.websocket.send("PONG :tmi.twitch.tv")
                        self.logger.info("Responded to PING")

                    #Check for raid messages
                    if await self.raid_starting(message):
                        break

                    message = message.rstrip(" \n")

                    self.logger.info(f"{current_log_prefix}Received: {message}")

                    #Checking if message is a command and if it what it's response should be
                    [sender, safe_command] = self.send_messsage.analyse_message_and_check_if_okay(message)

                    #Returns empty if we're going to ignore this message
                    if not safe_command:
                        continue

                    #Check if it really is a command
                    command_reponse = self.commands.check_valid_commands(sender, safe_command)

                    if command_reponse[0] and command_reponse[0] == 'cmd':
                        if self.commanded_change(command_reponse[1]):
                            # [can_be_sent, message_to_send] = self.send_messsage.check_if_can_be_sent(command_reponse[2])
                            await self.sending_msg_to_chat(command_reponse[2])
                        else:
                            # [can_be_sent, message_to_send] = self.send_messsage.check_if_can_be_sent(self.alternative_respond)
                            await self.sending_msg_to_chat(self.alternative_respond)

                            
                    elif self.isNotSilenced:
                        if command_reponse[0] == 'RE':
                            # [can_be_sent, message_to_send] = self.send_messsage.check_if_can_be_sent(command_reponse[1])
                            await self.sending_msg_to_chat(command_reponse[1])

                            if can_be_sent:
                                await self.sending_msg_to_chat(message_to_send)

            except websockets.exceptions.ConnectionClosed:
                self.logger.error(f"{current_log_prefix}Connection closed")
            except KeyboardInterrupt:
                self.logger.info(f"{current_log_prefix}Bot stopped by user - KEYBOARDINTERUPT! CTRL+C ?")
            except Exception as e:
                self.logger.error(f"{current_log_prefix}Bot stopped due to an unexpected error -> /{e}/")
            finally:
                #Cleanup code and exit gracfully
                self.logger.info(f"{current_log_prefix}Twitch-chat-loop terminated.")
                await self.disconnect()


    async def sending_msg_to_chat(self, msg_to_chat):
        # await websocket.send(f"PRIVMSG #{channel_name} :{message}")
        current_log_prefix = self.logger_prefix + "sending_msg_to_chat:"
        self.logger.info(f"{current_log_prefix}Going to send {len(msg_to_chat)} characters.")
        self.logger.info(f"{current_log_prefix}Received {msg_to_chat} characters.")

        [can_be_sent, msg_to_chat_list] = self.send_messsage.check_if_can_be_sent(msg_to_chat)

        if can_be_sent:
            self.logger.info(f"{current_log_prefix}Going to send {len(msg_to_chat_list)} message(s).")

            try:
                for msg_to_send in msg_to_chat_list:
                    self.logger.info(f"{current_log_prefix}AlbotKeinstein sending chat message:{msg_to_send}")
                    await self.websocket.send(f"PRIVMSG #{config.CHANNEL} :{msg_to_send}")
                    await self.send_messsage.message_sent()
            except Exception as e:
                self.logger.info(f"{current_log_prefix}Tried to send to Twitch chat:{msg_to_send}, but failed due to /{e}/")
        else:
            self.logger.info(f"{current_log_prefix}Couldn't send the message(s).")



    # Check for raid messages
    async def raid_starting(self, message):

        current_log_prefix = self.logger_prefix + "raid_starting:"

        if "USERNOTICE" in message and "msg-id=raid" in message:
            self.logger.info(f"{current_log_prefix}RAID DETECTED! Shutting down bot...")
            await self.disconnect()
            return True

        # Alternative way: check for the chat message that shows when a raid begins
        if "PRIVMSG" in message and ":Username is raiding with a party of" in message:
            self.logger.info(f"{current_log_prefix}RAID DETECTED through chat message! Shutting down bot...")
            await self.disconnect()
            return True

        return False

    #A work in progress....
    async def disconnect(self):

        current_log_prefix = self.logger_prefix + "disconnect:"

        self.logger.info(f"{current_log_prefix}Shutting down Twitch-chat-loop")
        self.run_loop = True


        try:
            self.logger.info(f"{current_log_prefix}Disconnecting from Twitch chat..")

            self.logger.info(f"{current_log_prefix}Cleaning up message-tasks-lists")
            await self.send_messsage.clean_up_message_sent_tasks_list()

            #Dette må sjekkes opp nærmere..
            # # Close the websocket/socket connection
            # if hasattr(self, 'connection') and self.connection:
            #     await self.connection.close()
                
            # # Cancel any pending tasks
            # for task in self.pending_tasks:
            #     task.cancel()
                
            # # Send logout message if needed
            # if self.is_connected:
            #     await self.send_raw("QUIT :Disconnecting")
                
            self.logger.info(f"{current_log_prefix}Successfully disconnected from Twitch")
        except Exception as e:
            self.logger.error(f"{current_log_prefix}Error during disconnect: {e}")
        finally:
            # Reset connection state variables
            self.is_connected = False
            self.connection = None