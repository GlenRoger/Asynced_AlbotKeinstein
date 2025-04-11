import asyncio
import config
import websockets
import os
import utils.send_message as sm
import commands.command_handler as ch
import requests

class TwitchConnection:

    def __init__(self, logger):
        self.logger_prefix = "utils/TwitchConnection=>"
        self.logger = logger
        self.websocket = ""

        self.run_loop = True

        self.send_messsage  = sm.Message_sending_central(self.logger)
        self.commands       = ch.Command_central(self.logger)

        self.alternative_respond = ""

        #Analyse commands in a different thread
        self.commands_to_check = []
        self.normal_priority_queue = []
        self.high_priority_queue = []

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
        


        self.check_oauth_token()
        self.check_oauth_token_br()
        # await self.check_token_scopes()




        # self.check_oauth_token()
        # await self.check_token_scopes()

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

            # await self.sending_msg_to_chat("AlbotKeinstein up and running! <3")
            await self.albot_msg_to_chat("AlbotKeinstein up and running! <3")


            print("\n\n\n\nLISTS!!\n\n\n")
            await self.get_MODs_list()
            await self.get_VIPs_list()
            await self.get_subscribers_list()
            await self.get_followers_list()
            self.get_xfirst_follower(10)

            self.logger.info(f"{current_log_prefix}Found MODs: {self.MODs_list}")
            self.logger.info(f"{current_log_prefix}Found VIPs: {self.VIPs_list}")
            self.logger.info(f"{current_log_prefix}Found subscribers: {self.subscribers_list}")




            try:
                while self.run_loop:
                    print("While in while....")

                    # self.logger.info(f"{current_log_prefix}Inside while loop.. active.")

                    message = await self.websocket.recv()

                    self.logger.info(f"{current_log_prefix}Catch-all-messages:{message}")

                    # Respond to PING with PONG to keep the connection alive
                    if message.startswith("PING"):
                        await self.websocket.send("PONG :tmi.twitch.tv")
                        self.logger.info("Responded to PING")

                    #Check for raid messages
                    if await self.raid_starting(message):
                        break

                    if await self.channel_went_offline(message):
                        break

                    message = message.rstrip(" \n")

                    self.logger.info(f"{current_log_prefix}Received: {message}")

                    #Checking if message is a command and if it what it's response should be
                    [sender, safe_command] = self.send_messsage.analyse_message_and_check_if_okay(message)

                    #Returns empty if we're going to ignore this message
                    if not safe_command:
                        self.logger.info(f"{sender} SENT NOT SAFE COMMAND?? See earlier in log!")
                        continue

                    #Sjekkes i annen asyncio.task
                    self.commands_to_check.append(f"{sender}:{safe_command}")




                    # #Check if it really is a command
                    # command_reponse = self.commands.check_valid_commands(sender, safe_command)

                    # if command_reponse[0] and command_reponse[0] == 'cmd':
                    #     if self.commanded_change(command_reponse[1]):
                    #         # [can_be_sent, message_to_send] = self.send_messsage.check_if_can_be_sent(command_reponse[2])
                    #         await self.sending_msg_to_chat(command_reponse[2])
                    #     else:
                    #         # [can_be_sent, message_to_send] = self.send_messsage.check_if_can_be_sent(self.alternative_respond)
                    #         await self.sending_msg_to_chat(self.alternative_respond)

                    # elif self.isNotSilenced:
                    #     if command_reponse[0] == 'RE':
                    #         # [can_be_sent, message_to_send] = self.send_messsage.check_if_can_be_sent(command_reponse[1])
                    #         await self.sending_msg_to_chat(command_reponse[1])



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

              
    async def continues_messsage_piles_check(self):
        current_log_prefix = self.logger_prefix + "continues_messsage_piles_check:"

        while self.run_loop:
            if not self.send_messsage.is_message_piles_empty():
                self.logger.info(f"{current_log_prefix} trying to empty message pile by one message - sleep 1 sec")
                await self.empty_message_piles()
                await asyncio.sleep(1)
            else:
                self.logger.info(f"{current_log_prefix} No messages in message piles - sleep 5 sec")
                await asyncio.sleep(5)


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
            self.logger.info(f"{current_log_prefix}Couldn't send the message(s) (Reason->can_be_sent:{can_be_sent})")


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





    #DISSE GJELDER FRA NÅ AV!
    async def commands_to_check_list_divide_into_queues(self):

        current_log_prefix = self.logger_prefix + "commands_to_check_list_divide_into_queues:"

        while self.run_loop:


            #If the commands_to_check list is not empty
            if self.commands_to_check:

                cmd_entry = self.commands_to_check.pop(0)

                self.logger.info(f"{current_log_prefix}Processing command: {cmd_entry}")

                sender, cmd = cmd_entry.split(':', 1)
                self.logger.info(f"{current_log_prefix}Divided cmd_entry into sender:{sender} and cmd:{cmd}")


                cmd_rated = self.commands.rate_priority_commands(cmd)

                self.logger.info(f"{current_log_prefix}Cmd:{cmd} got rated {cmd_rated}")

                if cmd_rated == 'high':
                    self.high_priority_queue.append(cmd_entry)
                elif cmd_rated == 'normal':
                    self.normal_priority_queue.append(cmd_entry)
                else:
                    self.logger.error(f"{current_log_prefix}What Am I going to to with this? Couldn't rate it!")

            await asyncio.sleep(1)
               



    def get_cmd_object(self, pri_list):

        current_log_prefix = self.logger_prefix + "run_commands_according_to_priority:"

        cur_cmd = pri_list.pop(0)

        self.logger.info(f"{current_log_prefix}There are commands to deal with:{cur_cmd}")

        sender, cmd = cur_cmd.split(':')

        self.logger.info(f"{current_log_prefix}Divided cmd_entry into sender:{sender} and cmd:{cmd}")

        #IKKE ALLE ADVANCED COMMANDS ER HIGH PRI...
        cmd_obj = self.commands.get_command_instructions(sender, cmd)

        return cmd_obj


    async def run_commands_according_to_priority(self):

        current_log_prefix = self.logger_prefix + "run_commands_according_to_priority:"

        while self.run_loop:


            #FØRSTE SJEKK BURDE VÆRE OM VI FAKTISK KAN SENDE EN  MELDING PER FØR VI PRØVER Å HÅNDTERE EN!

            #ANDRE SJEKK HAR VI EN COMMAND Å VURDERE?
            if self.high_priority_queue:


                cmd_obj = self.get_cmd_object(self.high_priority_queue)

                # cur_high_cmd = self.high_priority_queue.pop(0)

                # self.logger.info(f"{current_log_prefix}There are high priority commands to deal with:{cur_high_cmd}")

                # high_sender, high_cmd = cur_high_cmd.split(':')

                # self.logger.info(f"{current_log_prefix}Divided cmd_entry into sender:{high_sender} and cmd:{high_cmd}")

                # #IKKE ALLE ADVANCED COMMANDS ER HIGH PRI...
                # cmd_obj = self.commands.get_command_instructions(high_sender, high_cmd)

                #If we actually got something back
                if cmd_obj:

                    #Do something! Hard coded action
                    if cmd_obj.cmd_type == 'cmd':
                        pass


                    self.logger.info(f"{current_log_prefix}Going to send:{cmd_obj.response}")
                    await self.albot_msg_to_chat(cmd_obj.response)

                    


            elif self.normal_priority_queue:
                print(f"Normal pri: {self.normal_priority_queue}")

            else:
                print("No commands to execute!")


            await asyncio.sleep(1)


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



    # async def check_token_scopes(self):
    #     current_log_prefix = self.logger_prefix + "check_token_scopes:"

    #     print(self.access_token)

    #     try:
    #         # Get the token if you haven't already
    #         if not self.access_token:
    #             self.access_token = await self.get_oauth_token()
            
    #         # Make request to validation endpoint
    #         headers = {"Authorization": f"OAuth {self.access_token.replace('oauth:', '')}"}
    #         response = requests.get("https://id.twitch.tv/oauth2/validate", headers=headers)
            
    #         if response.status_code == 200:
    #             data = response.json()
    #             self.logger.info(f"{current_log_prefix}Client ID: {data.get('client_id')}")
    #             self.logger.info(f"{current_log_prefix}User ID: {data.get('user_id')}")
    #             self.logger.info(f"{current_log_prefix}Username: {data.get('login')}")
                
    #             # Log the scopes
    #             scopes = data.get('scopes', [])
    #             self.logger.info(f"{current_log_prefix}Token has {len(scopes)} scopes:")
    #             for scope in scopes:
    #                 self.logger.info(f"{current_log_prefix}- {scope}")
                    
    #             # Check if the needed scope is present
    #             if 'channel:read:subscriptions' in scopes:
    #                 self.logger.info(f"{current_log_prefix}✓ Token has the required 'channel:read:subscriptions' scope")
    #             else:
    #                 self.logger.error(f"{current_log_prefix}✗ Token DOES NOT have the required 'channel:read:subscriptions' scope")
                    
    #             return scopes
    #         else:
    #             self.logger.error(f"{current_log_prefix}Failed to validate token: {response.status_code}, {response.text}")
    #             return []
                
    #     except Exception as e:
    #         self.logger.error(f"{current_log_prefix}Error checking token scopes: {e}")
    #         return []
        
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
            self.logger.info(f"{current_log_prefix}User {follower_name} following since {followed_at}")
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