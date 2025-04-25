import asyncio
import config
import websockets
import os
import utils.send_message as sm
import commands.command_handler as ch
import requests
import time

class TwitchConnection:

    def __init__(self, logger):
        self.logger_prefix = "utils/TwitchConnection=>"
        self.logger = logger
        self.websocket = ""

        self.run_loop = True

        self.send_messsage  = sm.Message_sending_central(self.logger)
        self.commands       = ch.Command_central(self.logger)

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
        
        self.subscribers = ""

        self.MODs_list          = []
        self.VIPs_list          = []
        self.subscribers_list   = []
        self.followers_list     = []
        self.followers_dict     = {}


        self.shout_out_given    = []

        # Reference to the overlay bridge - to be set by AlbotBrain
        self.overlay_bridge = None



    #Henter ut alle VIPs
    async def get_VIPs_list(self):

        current_log_prefix = self.logger_prefix + "get_VIPs_list:"

        self.logger.info(f"{current_log_prefix}Contacting server for logging in")
      
        token = self.access_token_br.replace("oauth:", "")
        

        headers = {"Authorization": f"Bearer {token}", "Client-ID": self.client_id_br}
        response = requests.get(f"https://api.twitch.tv/helix/users?login={config.CHANNEL}", headers=headers)
        channel_id = response.json()["data"][0]["id"]

        if response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get channel ID: {response.text}")
            return

        channel_id = response.json()["data"][0]["id"]
        self.logger.info(f"{current_log_prefix}Got channel ID: {channel_id} for {config.CHANNEL}")
    
        # Now get the VIPs
        vip_response = requests.get(
            f"https://api.twitch.tv/helix/channels/vips?broadcaster_id={channel_id}", 
            headers=headers
        )
        
        if vip_response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get VIPs: {vip_response.text}")
            return
        
        vips_data = vip_response.json()["data"]
        vip_usernames = [vip["user_name"] for vip in vips_data]
        
        self.logger.info(f"{current_log_prefix}Found {len(vip_usernames)} VIPs")
        self.VIPs_list =  vip_usernames

    #Henter ut alle mods
    async def get_MODs_list(self):

        current_log_prefix = self.logger_prefix + "get_MODs_list:"

        self.logger.info(f"{current_log_prefix}Contacting server for logging in")
      
        token = self.access_token_br.replace("oauth:", "")

        headers = {"Authorization": f"Bearer {token}", "Client-ID": self.client_id_br}
        response = requests.get(f"https://api.twitch.tv/helix/users?login={config.CHANNEL}", headers=headers)
        channel_id = response.json()["data"][0]["id"]

        if response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get channel ID: {response.text}")
            return

        channel_id = response.json()["data"][0]["id"]
        self.logger.info(f"{current_log_prefix}Got channel ID: {channel_id} for {config.CHANNEL}")
    
        # Now get the MODs
        mods_response = requests.get(
            f"https://api.twitch.tv/helix/moderation/moderators?broadcaster_id={channel_id}", 
            headers=headers
        )
        
        if mods_response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get MODs: {mods_response.text}")
            return
        
        mods_data = mods_response.json()["data"]
        mods_usernames = [mod["user_name"] for mod in mods_data]
        
        self.logger.info(f"{current_log_prefix}Found {len(mods_usernames)} MODs")
        self.MODs_list =  mods_usernames


    #Henter ut alle subscribers
    async def get_subscribers_list(self):

        current_log_prefix = self.logger_prefix + "get_subscribers_list:"

        self.logger.info(f"{current_log_prefix}Contacting server for logging in")
      
        token = self.access_token_br.replace("oauth:", "")

        headers = {"Authorization": f"Bearer {token}", "Client-ID": self.client_id_br}
        response = requests.get(f"https://api.twitch.tv/helix/users?login={config.CHANNEL}", headers=headers)
        channel_id = response.json()["data"][0]["id"]

        self.logger.info(f"{current_log_prefix}Gotten the {channel_id} for {config.CHANNEL}")

        headers = {"Authorization": f"Bearer {token}", "Client-ID": self.client_id_br}
        sub_response = requests.get(f"https://api.twitch.tv/helix/subscriptions?broadcaster_id={channel_id}", headers=headers)

        if sub_response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get subscribers: {sub_response.text}")
            return
        
        subs_data = sub_response.json()["data"]
        subs_usernames = [sub["user_name"] for sub in subs_data]
        
        self.logger.info(f"{current_log_prefix}Found {len(subs_usernames)} subscribers")
        self.subscribers_list =  subs_usernames

#         # rep = response.json()

#         # self.logger.info(f"{current_log_prefix}Accepted!?")

# #        print(f"Response => {rep}")
#         # self.subscribers_list = response.json()["data"]


#         mods_data = mod_response.json()["data"]
#         self.subscribers_list = [mod["user_name"] for mod in mods_data]


#         print(f"Here: {self.subscribers_list}")



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
                self.logger.info(f"{current_log_prefix}OAuth token loaded from file: /{token}/")
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
                self.logger.info(f"{current_log_prefix}OAuth token loaded from file: /{token_br}/")
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


    #Gets a command object
    async def commanded_change(self, cmd_obj):
        current_log_prefix = self.logger_prefix + "commanded_change:"

        change_this = cmd_obj.get_cmd_calling()
        response = cmd_obj.get_response()

        self.logger.info(f"{current_log_prefix}Commanding change:/{change_this}/")

        alternative_respond = ""
        is_task_completed = True


        if (change_this.upper() == 'SLEEP' or change_this.upper() == 'SILENCE'):
            if self.isNotSilenced:
                self.logger.info(f"{current_log_prefix}SLEEP MODE ACTIVATED!")
                self.isNotSilenced = False
                is_task_completed = True
            else:
                self.logger.info(f"{current_log_prefix}SLEEP MODE -ALREADY- ACTIVATED!")
                alternative_respond = "AlbotKeinstein is already sleeping.. shhhh! ;)"
                is_task_completed = False

        elif change_this.upper() == 'WAKEUP':
            if not self.isNotSilenced:
                self.isNotSilenced = True
                self.logger.info(f"{current_log_prefix}SLEEP MODE DE-ACTIVATED!")
                is_task_completed = True
            else:
                alternative_respond = "I'm not sleeping, you're sleeping! :P"
                self.logger.info(f"{current_log_prefix}SLEEP MODE -ALREADY- DE-ACTIVATED!")
                is_task_completed = False

        
        elif change_this.upper() == 'REPEAT':
            self.logger.info(f"{current_log_prefix}WILLL REPEAT!")
            #ADD SOMETHING HERE!
            is_task_completed = True

        elif change_this.upper() == 'ALBOTREST' or change_this.upper() == 'SHUTDOWN' or change_this.upper() == 'QUIT':
            self.logger.info(f"{current_log_prefix}SHUTTING DOWN!")
            self.run_loop = False
            is_task_completed = True

        #Alternative repsond should be more accurate... hopefully!
        if alternative_respond:
            self.logger.info(f"{current_log_prefix}Using alternativ repsons {alternative_respond} rather than {response}")
            response = alternative_respond


        await self.albot_msg_to_chat(response)

        return is_task_completed

    #THIS FUNCTION SHOULD PROBABLY BEEN IN ALBOTBRAIN.PY???
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


        async with websockets.connect(uri) as self.websocket:

            # Send authentication commands
            await self.websocket.send(f"PASS {self.access_token}")
            await self.websocket.send(f"NICK {config.BOT_USERNAME}")
            
            # Join the channel
            await self.websocket.send(f"JOIN #{config.CHANNEL}")
            
            self.logger.info(f"{current_log_prefix}Joined channel: #{config.CHANNEL}")

            await self.albot_msg_to_chat("AlbotKeinstein up and running! <3")


            print("\n\n\n\nLISTS!! (Move listmaking outside this function? Maybe not possible because of with websocket)\n\n\n")
            await self.get_MODs_list()
            await self.get_VIPs_list()
            await self.get_subscribers_list()
            # await self.get_followers_list()
            self.get_xfirst_follower(10)

            self.logger.info(f"{current_log_prefix}Found MODs: {self.MODs_list}")
            self.logger.info(f"{current_log_prefix}Found VIPs: {self.VIPs_list}")
            self.logger.info(f"{current_log_prefix}Found subscribers: {self.subscribers_list}")


            try:
                while self.run_loop:
                    print("While in while....")

                    # self.logger.info(f"{current_log_prefix}Inside while loop.. active.")


                    #Venter på at noe skal skje i chatten
                    message = await self.websocket.recv()

                    self.logger.info(f"{current_log_prefix}Catch-all-messages:/{message}/")

                    # Respond to PING with PONG to keep the connection alive
                    if message.startswith("PING"):
                        await self.websocket.send("PONG :tmi.twitch.tv")
                        self.logger.info("Responded to PING")
                        continue

                    #Check for raid messages
                    if await self.raid_starting(message):
                        self.run_loop = False
                        break

                    if await self.channel_went_offline(message):
                        self.run_loop = False
                        break

                    message = message.rstrip(" \n")

                    self.logger.info(f"{current_log_prefix}Received: {message}")


                    sender = ""
                    chat_msg_sent = ""
                    safe_command = ""

                    #Checking if message is a command and if it what it's response should be
                    [sender, chat_msg_sent] = self.send_messsage.find_msg_and_sender(message)

                    self.logger.info(f"Getting back sender: {sender} and /{chat_msg_sent}/ from find_msg_and_sender")

                    if chat_msg_sent != "":
                        safe_command = self.send_messsage.analyse_message_and_check_if_okay(sender, chat_msg_sent)

                    await self.check_sender_privileges(sender)

                    #Returns empty if we're going to ignore this message
                    if not safe_command:
                        self.logger.info(f"{sender} SENT NOT SAFE COMMAND?? See earlier in log!")
                        continue

                    #Sjekkes i annen asyncio.task om
                    self.commands_to_check.append(f"{sender}:{safe_command}")

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


    def check_message_piles(self):
        return self.send_messsage.get_item_from_message_pile()

    async def empty_message_piles(self):
        current_log_prefix = self.logger_prefix + "empty_message_piles:"
        message_pile_item = self.send_messsage.get_item_from_message_pile()
        await self.sending_priority_from_message_pile(message_pile_item)

              
    async def sending_priority_from_message_pile(self, msg_to_chat):

        current_log_prefix = self.logger_prefix + "sending_priority_from_message_pile:"
        self.logger.info(f"{current_log_prefix}PRIORITY to send {len(msg_to_chat)} characters.")
        self.logger.info(f"{current_log_prefix}Amount of characters to be sent {msg_to_chat}.")

        msg_to_chat_list = ""

        #Checking if message is larger than 480 characters, if it is, then split it.
        #After this changed outgoing_chat_msg into a list.
        if len(msg_to_chat) < 485:
            msg_to_chat_list = self.send_messsage.split_large_message(msg_to_chat)
        else:
            msg_to_chat_list = [msg_to_chat]


        try:
            for msg_to_send in msg_to_chat_list:
                self.logger.info(f"{current_log_prefix}AlbotKeinstein sending PRIORITY chat message:{msg_to_send}")
                await self.websocket.send(f"PRIVMSG #{config.CHANNEL} :{msg_to_send}")
        except Exception as e:
            self.logger.info(f"{current_log_prefix}Tried to send to Twitch chat:{msg_to_send}, but failed due to /{e}/")


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


    #DISSE GJELDER FRA NÅ AV!

    #Hente ut siste spill av streamer, som skal få shoutout
    async def get_streamer_last_game(self, username):
        """Get the last game played by a streamer from Twitch API"""
        current_log_prefix = self.logger_prefix + "get_streamer_last_game:"
        
        try:
            # Prepare API request
            token = self.access_token_br.replace("oauth:", "")
            headers = {
                "Authorization": f"Bearer {token}", 
                "Client-ID": self.client_id_br
            }
            
            # First get the user ID from username
            response = requests.get(
                f"https://api.twitch.tv/helix/users?login={username}", 
                headers=headers
            )
            
            if response.status_code != 200:
                self.logger.error(f"{current_log_prefix}Failed to get user ID: {response.text}")
                return None
                
            user_id = response.json()["data"][0]["id"]
            
            # Then get the channel information including game
            channel_response = requests.get(
                f"https://api.twitch.tv/helix/channels?broadcaster_id={user_id}", 
                headers=headers
            )
            
            if channel_response.status_code != 200:
                self.logger.error(f"{current_log_prefix}Failed to get channel info: {channel_response.text}")
                return None
                
            channel_data = channel_response.json()["data"][0]
            game_name = channel_data.get("game_name", "")
            
            self.logger.info(f"{current_log_prefix}Found game for {username}: {game_name}")
            return game_name
            
        except Exception as e:
            self.logger.error(f"{current_log_prefix}Error getting game info: {e}")
            return None

    async def create_custom_shoutout(self, sender):
        """Send a custom shoutout message"""
        current_log_prefix = self.logger_prefix + "create_custom_shoutout:"
        
        try:

            messsage = ""

            # Get what the streamer was last playing
            game_name = await self.get_streamer_last_game(sender)
            
            # Craft message based on available info
            if game_name:
                message = f"Check out {sender} at https://twitch.tv/{sender} - they were last playing {game_name}!"
            else:
                message = f"Check out {sender} at https://twitch.tv/{sender} - they're an awesome streamer!"
            
            self.shout_out_queue.append(message)

            self.logger.info(f"{current_log_prefix}Adding shoutout for {sender} to so-queue")
            
        except Exception as e:
            self.logger.error(f"{current_log_prefix}Failed to send enhanced shoutout: {e}")

    #Per nå er det kun for automatiske shout outs
    async def check_sender_privileges(self, sender):
        current_log_prefix = self.logger_prefix + "check_sender_privileges:"
        self.logger.info(f"{current_log_prefix}Checking privileges for {sender}..")

        check_sender_in_automatic_shoutout_list = sender in config.AUTOMATIC_SHOUTOUT_LIST
        check_shout_out_already_gotten_a_shoutout = sender in self.shout_out_given

        if  check_sender_in_automatic_shoutout_list and not check_shout_out_already_gotten_a_shoutout:
            self.shout_out_given.append(sender) #Mulig denne burde settes når !So faktisk er gitt ut?
            self.logger.info(f"{current_log_prefix}Fellow streamer detected: {sender} => give shout out!")

            #Creates and queues the shoutout
            await self.create_custom_shoutout(sender)
        else:
            self.logger.info(f"{current_log_prefix}Already gotten a shoutout {check_shout_out_already_gotten_a_shoutout} or {sender} is not in auto-shoutout-list of streamers ({check_sender_in_automatic_shoutout_list})")


    #Sjekker hvilken rolle denne brukeren har opp mot hva som trengs for å kjøre denne kommandoen hos AlbotKeinstein.
    def is_user_allowed_to_use_this_command(self, sender, check_role_list):
        current_log_prefix = self.logger_prefix + "is_user_allowed_to_use_this_command:"

        if 'EVERYONE' in check_role_list:
            self.logger.info(f"{current_log_prefix}Sender {sender} is one of EVERYONE and allowed to run command!")
            return True

        for role in check_role_list:
                
                if role.upper() == 'STREAMERS':
                    if sender in config.STREAMERS:
                        self.logger.info(f"{current_log_prefix}Sender {sender} is in STREAMERS-list and allowed to run command!")
                        return True
                    
                elif role.upper() == 'MODS':
                    if sender in self.MODs_list:
                        self.logger.info(f"{current_log_prefix}Sender {sender} is in MODs-list and allowed to run command!")
                        return True

                elif role.upper() == 'VIPS':
                    if sender in self.VIPs_list:
                        self.logger.info(f"{current_log_prefix}Sender {sender} is in VIPs-list and allowed to run command!")
                        return True

                elif role.upper() == 'SUBS':
                    if sender in self.subscribers_list:
                        self.logger.info(f"{current_log_prefix}Sender {sender} is in SUBs-list and allowed to run command!")
                        return True
                    

                elif role.upper() =='FOLLOWERS':
                    if sender in self.followers_dict.keys():
                        self.logger.info(f"{current_log_prefix}Sender {sender} is in FOLLOWERS-list and allowed to run command!")
                        return True


        self.logger.info(f"{current_log_prefix}Sender {sender} is NOT alllowd to run command!")
        return False


    #Sender is the person who wrote the command
    def handle_overlay_commands(self, sender, overview_cmd):
        current_log_prefix = self.logger_prefix + "handle_overlay_commands:"

        self.logger.info(f"{current_log_prefix}Received sender:{sender} and overview_cmd:{overview_cmd}")

        if overview_cmd.upper().startswith('OVERLAY '):
            parts = overview_cmd.split(' ', 2)  # Split into 3 parts: 'OVERLAY', action, [params]
            if len(parts) >= 2:
                action = parts[1].upper()
                
                if action == 'MESSAGE':
                    self.overlay_bridge.show_message(' '.join(parts[2:]))
                elif action == 'SOUND':
                    self.overlay_bridge.play_sound("./overlay_media/sounds/Alarm01.wav")
                elif action == 'GIF':
                    self.overlay_bridge.show_gif("./overlay_media/gifs/temp_gif.gif")
                elif action == 'GREETINGS':
                    self.overlay_bridge.show_full_greeting(streamer_name=sender, greeting_text=f'Howdy,{sender}', gif_path="./overlay_media/gifs/temp_gif.gif", sound_path="./overlay_media/sounds/Alarm01.wav")
                elif action == 'HIDE':
                    self.overlay_bridge.hide_overlay()

            
            # Animation commands
            elif action == 'ANIMATE' and len(parts) >= 3:
                anim_parts = parts[2].split(' ', 1)
                anim_type = anim_parts[0].lower()
                
                # Get message if provided, otherwise use default
                message = anim_parts[1] if len(anim_parts) > 1 else f"Animation by {sender}!"
                
                # Show message with the specified animation
                self.overlay_bridge.show_message(message, anim_type)
                
            # Specific animation shortcuts
            elif action == 'BOUNCE' and len(parts) >= 3:
                self.overlay_bridge.show_message(' '.join(parts[2:]), "bounce")
            elif action == 'SPIN' and len(parts) >= 3:
                self.overlay_bridge.show_message(' '.join(parts[2:]), "spin")
            elif action == 'ROLL' and len(parts) >= 3:
                self.overlay_bridge.show_message(' '.join(parts[2:]), "roll")
            elif action == 'SHAKE' and len(parts) >= 3:
                self.overlay_bridge.show_message(' '.join(parts[2:]), "shake")
            elif action == 'WAVE' and len(parts) >= 3:
                self.overlay_bridge.show_message(' '.join(parts[2:]), "wave")
            elif action == 'PULSE' and len(parts) >= 3:
                self.overlay_bridge.show_message(' '.join(parts[2:]), "pulse")
            elif action == 'FADE' and len(parts) >= 3:
                self.overlay_bridge.show_message(' '.join(parts[2:]), "fade")

    async def commands_to_check_list_divide_into_queues(self):

        current_log_prefix = self.logger_prefix + "commands_to_check_list_divide_into_queues:"

        while self.run_loop:


            #If the commands_to_check list is not empty
            if self.commands_to_check:

                cmd_entry = self.commands_to_check.pop(0)

                self.logger.info(f"{current_log_prefix}Processing command: {cmd_entry}")

                sender, cmd = cmd_entry.split(':', 1)
                self.logger.info(f"{current_log_prefix}Divided cmd_entry into sender:{sender} and cmd:{cmd}")


                #Sjekk om dette er en kommando først
                if self.commands.is_command(cmd):

                    #Må finne ut om denne kommandoen er av high eller normal prioritet
                    cmd_rated = self.commands.rate_priority_commands(cmd)

                    self.logger.info(f"{current_log_prefix}Cmd:{cmd} got rated {cmd_rated}")

                    if cmd_rated == 'high':
                        self.high_priority_queue.append(cmd_entry)
                    elif cmd_rated == 'normal':
                        self.normal_priority_queue.append(cmd_entry)
                    elif cmd_rated == 'shoutout':
                        await self.create_custom_shoutout(cmd.split(" ")[1])
                    elif cmd_rated == 'overlay':
                        self.overlay_queue.append(cmd_entry)
                    else:
                        #Logg it and "throw"/"trash" this command. Next..
                        self.logger.error(f"{current_log_prefix}What Am I going to to with this? Couldn't rate it!")
                
                else:
                    #If we want to have a response later on commands that doesn't exist, this is the place to do it!
                    pass


            await asyncio.sleep(1)
               
        self.logger.info(f"{current_log_prefix}WHILE-LOOP STOPPED! (self.run_loop={self.run_loop})")

    def get_cmd_obj_and_sender(self, cur_cmd):

        current_log_prefix = self.logger_prefix + "get_cmd_obj_and_sender:"
        self.logger.info(f"{current_log_prefix}There are commands to deal with:{cur_cmd}")

        sender, cmd = cur_cmd.split(':')

        self.logger.info(f"{current_log_prefix}Divided cmd_entry into sender:{sender} and cmd:{cmd}")

        #IKKE ALLE ADVANCED COMMANDS ER HIGH PRI...
        cmd_obj = self.commands.get_command_object(cmd)

        return sender, cmd_obj


    async def run_commands_according_to_priority(self):

        current_log_prefix = self.logger_prefix + "run_commands_according_to_priority:"

        while self.run_loop:


            #Overlay har egentlig ingen minimum gifs, lyd og slik den kan kjøre, men vi må hindre at de ikke spilles av for fort og
            #over hverandre.
            if self.overlay_queue:
                cur_ovrl_cmd = self.overlay_queue.pop(0)

                sender, cmd = cur_ovrl_cmd.split(':')
                
                self.logger.info(f"{current_log_prefix}This command has Overlay priority: /{cur_ovrl_cmd}/.")
                self.handle_overlay_commands(sender, cmd)



            #FØRSTE SJEKK BURDE VÆRE OM VI FAKTISK KAN SENDE EN  MELDING PER FØR VI PRØVER Å HÅNDTERE EN!

            cur_cmd = ""

            #ANDRE SJEKK HAR VI EN COMMAND Å VURDERE?
            if self.high_priority_queue:
                cur_cmd = self.high_priority_queue.pop(0)
                self.logger.info(f"{current_log_prefix}This command has high priority: /{cur_cmd}/.")
            elif self.normal_priority_queue:
                cur_cmd = self.normal_priority_queue.pop(0)
                self.logger.info(f"{current_log_prefix}This command has normal priority: /{cur_cmd}/.")
            elif self.shout_out_queue:

                cur_time = time.time()

                #If we have set a timestamp, then check if the cooldown is over
                if self.last_shout_out_given_timestamp:
                    cooldown_diff = cur_time - self.last_shout_out_given_timestamp

                    if  cooldown_diff >= self.shout_out_cooldown_in_sec:

                        self.logger.info(f"{current_log_prefix}No cooldown!")

                        #if we're not on a coldown for shout out, do the same as above
                        self.last_shout_out_given_timestamp = cur_time

                        shout_out_message = self.shout_out_queue.pop(0)
                        await self.albot_msg_to_chat(shout_out_message)



                else:
                    #If timestamp not made, make one and send shout out (1st time)
                    self.last_shout_out_given_timestamp = cur_time
                    await self.albot_msg_to_chat(self.shout_out_queue.pop(0))



            if cur_cmd == "":
                await asyncio.sleep(1)
                continue

            sender, cmd_obj = self.get_cmd_obj_and_sender(cur_cmd)

            #If we didn't get a command-object back, start anew - command doesn't exist
            if not cmd_obj:
                self.logger.info(f"{current_log_prefix}Unknown command: /{cur_cmd}/ - Check next command in stead")
                await asyncio.sleep(1)
                continue

            #Check if user can use this command, then run it if ok
            if self.is_user_allowed_to_use_this_command(sender, cmd_obj.get_allowed_users_list()):

                self.logger.info(f"{current_log_prefix}{sender} is allowed to use /{cur_cmd}/")

                #Do something! Hard coded action
                if cmd_obj.cmd_type.upper() == 'CMD':
                    self.logger.info(f"{current_log_prefix}/{cur_cmd}/ is a command!/")
                    await self.commanded_change(cmd_obj)

                elif cmd_obj.cmd_type.upper() == 'RE':
                    self.logger.info(f"{current_log_prefix}/{cur_cmd}/ is a response!/")
                    await self.albot_msg_to_chat(cmd_obj.response)
                else:
                    self.logger.info(f"{current_log_prefix}Unknown command type: /{cmd_obj.cmd_type.upper()}/")
                    pass #Unknown command-type

            else:
                #If we want feedback on users/senders trying to use commands they're not allowed to, it can be put here
                self.logger.info(f"{current_log_prefix}{sender} is NOT allowed to use /{cur_cmd}/")
                pass


            #Hindrer at botten løper løpsk og sender mer enn 60 meldinger i minuttet.
            await asyncio.sleep(1)


        self.logger.info(f"{current_log_prefix}WHILE-LOOP STOPPED! (self.run_loop={self.run_loop})")


    #Meldinger som alle i chat kan se
    async def albot_msg_to_chat(self, msg_to_chat):
        # await websocket.send(f"PRIVMSG #{channel_name} :{message}")
        current_log_prefix = self.logger_prefix + "albot_msg_to_chat:"

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

        print("CHECKING TOKEN VALIDATION, time left and scopes:")

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

        print("CHECKING TOKEN VALIDATION, time left and scopes:")

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




    async def get_followers_list(self):
        current_log_prefix = self.logger_prefix + "get_followers_list:"
        
        self.logger.info(f"{current_log_prefix}Getting followers for channel {config.CHANNEL}")
        
        token = self.access_token_br.replace("oauth:", "")

        print(f"TOKEN:/{token}/")

        # First get the channel ID
        headers = {"Authorization": f"Bearer {token}", 
                "Client-ID": self.client_id_br}
        
        response = requests.get(f"https://api.twitch.tv/helix/users?login={config.CHANNEL}", 
                            headers=headers)
        
        if response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get channel ID: {response.text}")
            return
            
        channel_id = response.json()["data"][0]["id"]
        
        # Get followers
        followers = []
        pagination = ""
        
        # We need to paginate through results since Twitch limits to 100 per request
        while True:
            pagination_query = f"&after={pagination}" if pagination else ""
            followers_url = f"https://api.twitch.tv/helix/channels/followers?broadcaster_id={channel_id}&first=100{pagination_query}"
            
            followers_response = requests.get(followers_url, headers=headers)
            
            if followers_response.status_code != 200:
                self.logger.error(f"{current_log_prefix}Failed to get followers: {followers_response.text}")
                break
                
            result = followers_response.json()
            followers.extend(result["data"])
            
            # Check if we need to paginate more
            if "pagination" in result and "cursor" in result["pagination"]:
                pagination = result["pagination"]["cursor"]
                self.logger.info(f"{current_log_prefix}Getting next page of followers...")
            else:
                break
        
        self.logger.info(f"{current_log_prefix}Found {len(followers)} followers")
        
        # Each follower object contains follow date info
        for follower in followers:
            follower_name = follower["user_name"]
            followed_at = follower["followed_at"]  # ISO format date string
            # self.logger.info(f"{current_log_prefix}User {follower_name} following since {followed_at}")
            self.followers_dict[follower_name] = followed_at

        self.followers_list = followers


    def get_xfirst_follower(self, xfirst):
        # Sort by follow date descending (most recent first)
        sorted_followers = sorted(self.followers_dict.items(), key=lambda x: x[1], reverse=False)

        # Get the top X (e.g., top 5)
        top_x = xfirst
        top_followers = sorted_followers[:top_x]

        # Print or use the results
        for username, followed_at in top_followers:
            print(f"{username} followed on {followed_at}")