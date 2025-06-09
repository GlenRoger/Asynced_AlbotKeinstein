import asyncio
import config
import websockets
import os
import requests



class TwitchConnection:

    def __init__(self, logger):
        self.logger_prefix = "utils/TwitchConnection=>"
        self.logger = logger
        self.websocket = ""

        self.run_loop = True

        self.msg_central  = ""  #het self.send_messsage før

        #Analyse commands in a different thread
        self.commands_to_check = []

        self.high_priority_queue    = []
        self.normal_priority_queue  = []
        self.shout_out_queue        = []
        self.overlay_queue          = []

        self.shout_out_cooldown_in_sec          = 60
        self.last_shout_out_given_timestamp     = ""

        self.client_id          = ""
        self.access_token       = ""

        self.client_id_br       = ""
        self.access_token_br    = ""

        #If true respond to all commands, if not just repsond to advanced ones!
        self.isNotSilenced = True

        self.shout_out_given    = []

        self.usermanagement = ""

        # Reference to the overlay bridge - to be set by AlbotBrain
        self.overlay_runner = None

         # Reference to the Albotbrain - to be set by AlbotBrain, to be able
         # to shut down the program completely
        self.albot_brain = None


    #To be able to shut down the program completely
    def set_albot_brain(self, albot_brain):
        """Set reference to AlbotBrain for shutdown purposes"""
        self.albot_brain = albot_brain

    #TwitchConnection gir tokens og diverse Oauth til usermanager
    def set_user_manager(self, um):
        self.usermanagement = um       

    def set_msg_central(self, mc):
        self.msg_central = mc

    def set_overlay_runner(self, ob):
        self.overlay_runner = ob

    #Shutting down the bot all the way from Twitch chat to albotbrain
    async def shutdown(self):
        """Shutdown the Twitch connection cleanly"""
        current_log_prefix = self.logger_prefix + "shutdown:"
        self.logger.info(f"{current_log_prefix}Shutting down TwitchConnection...")
        
        self.run_loop = False
        
        # Send goodbye message if we're still connected
        try:
            if hasattr(self, 'websocket') and self.websocket:
                await self.albot_msg_to_chat("TwitchConnection.shutdown", "See you later everybody! Bye-bye! <3")
                # Give a moment for the message to send
                await asyncio.sleep(1)
        except Exception as e:
            self.logger.warning(f"{current_log_prefix}Could not send goodbye message: {e}")
            
        await self.disconnect()


    async def get_client_id(self):
        """Read get_client_id from file or prompt user if not found"""

        current_log_prefix = self.logger_prefix + "get_client_id:"

        self.logger.info(f"{current_log_prefix}Getting the ClientID...")

        if os.path.exists(config.CLIENT_ID_FILE):

            self.logger.info(f"{current_log_prefix}File found...")

            with open(config.CLIENT_ID_FILE, 'r') as f:
                self.logger.info(f"{current_log_prefix}File opened...")

                self.client_id = f.read().strip()

                if len(self.client_id) > 10:
                    self.logger.info(f"{current_log_prefix}ClientID loaded from file. Ok!")
                else:
                    self.logger.info(f"{current_log_prefix}ClientID loaded from file.. seems short though?")
        else:
            # Exit gracefully
            self.logger.error(f"{current_log_prefix}ClientID file not found: {config.CLIENT_ID_FILE}")
            raise SystemExit(1)


    async def get_client_id_br(self):
        """Read get_client_id from file or prompt user if not found"""

        current_log_prefix = self.logger_prefix + "get_client_id_br:"

        self.logger.info(f"{current_log_prefix}Getting the ClientID_br...")

        if os.path.exists(config.CLIENT_ID_FILE_2):

            self.logger.info(f"{current_log_prefix}File found...")

            with open(config.CLIENT_ID_FILE_2, 'r') as f:
                self.logger.info(f"{current_log_prefix}File opened...")

                self.client_id_br = f.read().strip()

                if len(self.client_id_br) > 10:
                    self.logger.info(f"{current_log_prefix}ClientID loaded from file. Ok!")
                else:
                    self.logger.info(f"{current_log_prefix}ClientID loaded from file.. seems short though?")
        else:
            # Exit gracefully
            self.logger.error(f"{current_log_prefix}ClientID file not found: {config.CLIENT_ID_FILE_2}")
            raise SystemExit(1)


    async def get_oauth_token(self):
        """Read OAuth token from file or prompt user if not found"""
        current_log_prefix = self.logger_prefix + "get_oauth_token:"

        if os.path.exists(config.OAUTH_TOKEN_FILE):
            with open(config.OAUTH_TOKEN_FILE, 'r') as f:
                token = f.read().strip()
                # token = token.replace("oauth:", "")
                # self.logger.info(f"{current_log_prefix}OAuth token loaded from file: /{token}/")
                self.logger.info(f"{current_log_prefix}OAuth token loaded successfully!")
                self.access_token =  token
        else:
            # Exit gracefully
            self.logger.error(f"{current_log_prefix}OAuth token file not found: {config.OAUTH_TOKEN_FILE}")
            self.logger.info(f"{current_log_prefix}Please create this file with your Twitch OAuth token")
            self.logger.info(f"{current_log_prefix}You can get a token from https://twitchapps.com/tmi/")
            raise SystemExit(1)
        

    async def get_oauth_token_br(self):
        """Read OAuth token from file or prompt user if not found"""
        current_log_prefix = self.logger_prefix + "get_oauth_token:"

        if os.path.exists(config.OAUTH_TOKEN_FILE_2):
            with open(config.OAUTH_TOKEN_FILE_2, 'r') as f:
                token_br = f.read().strip()
                # token = token.replace("oauth:", "")
                # self.logger.info(f"{current_log_prefix}OAuth token loaded from file: /{token_br}/")
                self.logger.info(f"{current_log_prefix}OAuth token loaded successfully!")
                self.access_token_br =  token_br
        else:
            # Exit gracefully
            self.logger.error(f"{current_log_prefix}OAuth token file not found: {config.OAUTH_TOKEN_FILE_2}")
            self.logger.info(f"{current_log_prefix}Please create this file with your Twitch OAuth token")
            self.logger.info(f"{current_log_prefix}You can get a token from https://twitchapps.com/tmi/")
            raise SystemExit(1)
        


        #Sjekker tokens for Albot og kanal
        self.check_oauth_token()
        self.check_oauth_token_br()


    # Main loop checking Twitch chat for commands and changes in chat status and keeping ping to look alive.
    async def start_messsage_loop(self):
        """Connect to Twitch IRC via WebSocket and analysing the Twitch chat"""

        current_log_prefix = self.logger_prefix +"start_messsage_loop:"

        self.logger.info(f"{current_log_prefix}OAuth check complete!")


        uri = f"{config.TWITCH_IRC_SERVER}:{config.TWITCH_IRC_PORT}"

        self.logger.info(f"{current_log_prefix}Connecting to Twitch IRC: {uri}")

        await self.get_oauth_token()
        await self.get_client_id()

        await self.get_oauth_token_br()
        await self.get_client_id_br()

        self.usermanagement.setOauthTokens(self.access_token, self.access_token_br)
        self.usermanagement.setCliend_ids(self.client_id, self.client_id_br)

        await self.usermanagement.buildlists()

        async with websockets.connect(uri) as self.websocket:

            # Send authentication commands
            await self.websocket.send(f"PASS {self.access_token}")
            await self.websocket.send(f"NICK {config.BOT_USERNAME}")
            
            # Join the channel
            await self.websocket.send(f"JOIN #{config.CHANNEL}")
            
            self.logger.info(f"{current_log_prefix}Joined channel: #{config.CHANNEL}")

            await self.albot_msg_to_chat("TwitchConnection.start_message_loop", "AlbotKeinstein up and running! <3")
            self.overlay_runner.set_in_queue(f"Albot up and running!:AlbotStartup")

            try:
                while self.run_loop:
                    print("\nWhile in while....")

                    #Venter på at noe skal skje i chatten
                    message = await self.websocket.recv()

                    message = message.rstrip(" \n")

                    self.logger.info(f"{current_log_prefix}Catch-all-messages:/{message}/")


                    #First precheck of messages if they ar from Twich
                    if not await self.check_for_Twitch_messages(message):

                        #Check if this is for the bot
                        if config.PREFIX_FOR_BOT_TO_READ in message:
                            await self.msg_central.check_chat_message(message)
                        else:
                            await self.msg_central.check_for_automatic_shout_out(message)
                            self.logger.info(f"{current_log_prefix} - Ignoring message, not a command, missing {config.PREFIX_FOR_BOT_TO_READ}!")

                self.logger.info(f"{current_log_prefix}WHILE-LOOP STOPPED! (self.run_loop={self.run_loop})")

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


    #Håndterer Twitch-meldinger, ping/raid/dc
    async def check_for_Twitch_messages(self, message):
        
        # Respond to PING with PONG to keep the connection alive
        if message.startswith("PING"):
            await self.websocket.send("PONG :tmi.twitch.tv")
            self.logger.info("Responded to PING")
            return True

        #Check for raid messages
        if await self.raid_starting(message):
            self.run_loop = False

        if await self.channel_went_offline(message):
            self.run_loop = False

        return False

    #Sjekke om kanalen er offline.... at least I tried...
    async def channel_went_offline(self, message):
        """Check if the message indicates that the channel went offline"""
        current_log_prefix = self.logger_prefix + "channel_went_offline:"
        
        # Look for Twitch notices about the channel going offline
        if "NOTICE" in message and "Channel is currently offline" in message:
            self.logger.info(f"{current_log_prefix}Channel {config.CHANNEL} is OFFLINE. Shutting down bot...")
            return True
            
        # Alternatively, you can look for the channel's stream status in the roomstate
        if "ROOMSTATE" in message and ":offline=1" in message:
            self.logger.info(f"{current_log_prefix}Channel {config.CHANNEL} detected as OFFLINE. Shutting down bot...")
            return True
            
        return False

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
        self.run_loop = False


        try:
            self.logger.info(f"{current_log_prefix}Disconnecting from Twitch chat..")
            self.logger.info(f"{current_log_prefix}Cleaning up message-tasks-lists")

            # await self.send_messsage.clean_up_message_sent_tasks_list()

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


#MOVE! Eller ok er her?
    # async def create_custom_shoutout(self, sender):
    #     """Send a custom shoutout message"""
    #     current_log_prefix = self.logger_prefix + "create_custom_shoutout:"
        
    #     try:

    #         messsage = ""

    #         # Get what the streamer was last playing
    #         game_name = await self.get_streamer_last_game(sender)
            
    #         # Craft message based on available info
    #         if game_name:
    #             message = f"Check out {sender} at https://twitch.tv/{sender} - they were last playing {game_name}!"
    #         else:
    #             message = f"Check out {sender} at https://twitch.tv/{sender} - they're an awesome streamer!"
            
    #         self.shout_out_queue.append(message)

    #         self.logger.info(f"{current_log_prefix}Adding shoutout for {sender} to so-queue")
            
    #     except Exception as e:
    #         self.logger.error(f"{current_log_prefix}Failed to send enhanced shoutout: {e}")

#MOVE! command
    #Sender is the person who wrote the command
    # def handle_overlay_commands(self, sender, overview_cmd):

    #     current_log_prefix = self.logger_prefix + "handle_overlay_commands:"

    #     self.logger.info(f"{current_log_prefix}Received sender:{sender} and overview_cmd:{overview_cmd}")
    #     self.logger.info(f"{current_log_prefix}Commando read:/{overview_cmd.upper()}/")


    #     if not self.isNotSilenced:
    #         self.logger.info(f"{current_log_prefix}Couldn't complete.. Albot is sleeping! (status not silenced?:{self.isNotSilenced})/")
    #         return ""



    #     if overview_cmd.upper().startswith('OVERLAY '):

    #         self.logger.info(f"{current_log_prefix}It's an overlay!")

    #         parts = overview_cmd.split(' ', 2)  # Split into 3 parts: 'OVERLAY', action, [params]

    #         if len(parts) >= 2:
    #             action = parts[1].upper()

    #             self.logger.info(f"{current_log_prefix}-len >= 2: True and action understood as:/{action}/")



    #             if action.upper() == 'MESSAGE' and len(parts) >= 3:
    #                 self.overlay_bridge.show_message(' '.join(parts[2:]))
    #             elif action.upper() == 'SOUND':
    #                 self.overlay_bridge.play_sound("./overlay_media/sounds/Alarm01.wav")
    #             elif action.upper() == 'GIF':
    #                 self.overlay_bridge.show_gif("./overlay_media/gifs/MOON_CAKE_CHAOS.gif")
    #             elif action.upper() == 'GREETINGS':
    #                 self.overlay_bridge.show_full_greeting(streamer_name=sender, 
    #                                                        greeting_text=f'Howdy,{sender}', 
    #                                                        gif_path="./overlay_media/gifs/MOON_CAKE_CHAOS.gif", 
    #                                                        sound_path="./overlay_media/sounds/Alarm01.wav")
    #             elif action.upper() == 'HIDE':
    #                 self.overlay_bridge.hide_overlay()
            
    #             # Animation commands
    #             elif action.upper() == 'ANIMATE' and len(parts) >= 3:
    #                 anim_parts = parts[2].split(' ', 1)
    #                 anim_type = anim_parts[0].lower()
                    
    #                 # Get message if provided, otherwise use default
    #                 message = anim_parts[1] if len(anim_parts) > 1 else f"Animation by {sender}!"
                    
    #                 # Show message with the specified animation
    #                 self.overlay_bridge.show_message(message, run_alone=True)
    #                 self.overlay_bridge.animate_message(anim_type)

    #             # Combined fade-in/fade-out animation - show a message that fades in, stays visible, then fades out
    #             elif action == 'FADE' and len(parts) >= 3:
    #                 message = parts[2]
    #                 self.logger.info(f"{current_log_prefix}Combined fade animation with message: {message}")
                    
    #                 # Show message with initially zero opacity
    #                 self.overlay_bridge.show_message(message, run_alone=True)
                    
    #                 # Start the combined fade animation - default 6000ms total (2000ms fade-in, 2000ms display, 2000ms fade-out)
    #                 self.overlay_bridge.animate_message("fade")



    #             # Specific animation shortcuts
    #             elif action.upper() in ['BOUNCE', 'SPIN', 'ROLL', 'SHAKE', 'WAVE', 'PULSE'] and len(parts) >= 3:
    #                 self.logger.info(f"{current_log_prefix}Action recognized as animation action:{action.upper()}")
    #                 # First show the message
    #                 self.overlay_bridge.show_message(parts[2], run_alone=True)
    #                 # Then animate it
    #                 self.overlay_bridge.animate_message(action.lower())

    #         # Specific animation shortcuts - Claude changed its mind? :S
    #         # elif action == 'BOUNCE' and len(parts) >= 3:
    #         #     self.overlay_bridge.show_message(' '.join(parts[2:]), "bounce")
    #         # elif action == 'SPIN' and len(parts) >= 3:
    #         #     self.overlay_bridge.show_message(' '.join(parts[2:]), "spin")
    #         # elif action == 'ROLL' and len(parts) >= 3:
    #         #     self.overlay_bridge.show_message(' '.join(parts[2:]), "roll")
    #         # elif action == 'SHAKE' and len(parts) >= 3:
    #         #     self.overlay_bridge.show_message(' '.join(parts[2:]), "shake")
    #         # elif action == 'WAVE' and len(parts) >= 3:
    #         #     self.overlay_bridge.show_message(' '.join(parts[2:]), "wave")
    #         # elif action == 'PULSE' and len(parts) >= 3:
    #         #     self.overlay_bridge.show_message(' '.join(parts[2:]), "pulse")
    #         # elif action == 'FADE' and len(parts) >= 3:
    #         #     self.overlay_bridge.show_message(' '.join(parts[2:]), "fade")


#MOVE? comand
    def get_cmd_obj_and_sender(self, cur_cmd):

        current_log_prefix = self.logger_prefix + "get_cmd_obj_and_sender:"
        self.logger.info(f"{current_log_prefix}There are commands to deal with:{cur_cmd}")

        sender, cmd = cur_cmd.split(':')

        self.logger.info(f"{current_log_prefix}Divided cmd_entry into sender:{sender} and cmd:{cmd}")

        #IKKE ALLE ADVANCED COMMANDS ER HIGH PRI...
        cmd_obj = self.commands.get_command_object(cmd)

        return sender, cmd_obj

    #Meldinger som alle i chat kan se
    async def albot_msg_to_chat(self, called_by_function, msg_to_chat):
        # await websocket.send(f"PRIVMSG #{channel_name} :{message}")
        current_log_prefix = self.logger_prefix + "albot_msg_to_chat:"


        self.logger.info(f"{current_log_prefix}Going to send {msg_to_chat}, on behalf or (called_by_function)")

        self.logger.info(f"{current_log_prefix}Going to send {len(msg_to_chat)} characters.")
        self.logger.info(f"{current_log_prefix}Received {msg_to_chat} characters.")

        try:
            # for msg_to_send in msg_to_chat_list:
            self.logger.info(f"{current_log_prefix}AlbotKeinstein sending chat message:{msg_to_chat}")
            await self.websocket.send(f"PRIVMSG #{config.CHANNEL} :{msg_to_chat}")
            # await self.send_messsage.message_sent()
        except Exception as e:
            self.logger.info(f"{current_log_prefix}Tried to send to Twitch chat:{msg_to_chat}, but failed due to /{e}/")


    #Meldinger kun synlig for mods
    async def albot_msg_to_mod_only(self, message):
        """Send a message in main chat that only mods and broadcaster can see"""
        current_log_prefix = self.logger_prefix + "send_mod_only_message:"
        
        try:
            self.logger.info(f"{current_log_prefix}Sending mod-only message: {message}")
            await self.websocket.send(f"PRIVMSG #{config.CHANNEL} :/mods {message}")
        except Exception as e:
            self.logger.error(f"{current_log_prefix}Failed to send mod-only message: {e}")



#TEST OM TOKEN ER av rett type og om den fortsatt kan brukes (ikke utgått)!
    def check_oauth_token(self):
        # Remove 'oauth:' prefix if present

        print("CHECKING Albot's TOKEN VALIDATION, time left and scopes:")

        token = self.access_token
        if token.startswith('oauth:'):
            token = token[6:]
        
        # Make request to validation endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://id.twitch.tv/oauth2/validate", headers=headers)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Token is valid!")
            print(f"Client ID: {data.get('client_id')}")
            print(f"User ID: {data.get('user_id')}")
            print(f"Username: {data.get('login')}")
            
            # Show the scopes
            scopes = data.get('scopes', [])
            print(f"Token has {len(scopes)} scopes:")
            for scope in scopes:
                print(f"- {scope}")
            
            # Check for expiration
            if 'expires_in' in data:
                print(f"Token expires in {data['expires_in']} seconds")
                
            return True
        else:
            print("Token is invalid or expired")
            print(f"Response: {response.text}")
            return False



    def check_oauth_token_br(self):
        # Remove 'oauth:' prefix if present

        print("CHECKING BR-TOKEN VALIDATION, time left and scopes:")

        token = self.access_token_br
        if token.startswith('oauth:'):
            token = token[6:]
        
        # Make request to validation endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://id.twitch.tv/oauth2/validate", headers=headers)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Token is valid!")
            print(f"Client ID: {data.get('client_id')}")
            print(f"User ID: {data.get('user_id')}")
            print(f"Username: {data.get('login')}")
            
            # Show the scopes
            scopes = data.get('scopes', [])
            print(f"Token has {len(scopes)} scopes:")
            for scope in scopes:
                print(f"- {scope}")
            
            # Check for expiration
            if 'expires_in' in data:
                print(f"Token expires in {data['expires_in']} seconds")
                
            return True
        else:
            print("Token is invalid or expired")
            print(f"Response: {response.text}")
            return False

