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

        

        #If true respond to all commands, if not just repsond to advanced ones!
        self.isNotSilenced = True
        
        self.subscribers = ""

        

    async def get_subscribers_list(self):

        access_token = await self.get_oauth_token()
        client_id = await self.get_client_id()

       
        headers = {"Authorization": f"Bearer {access_token}", "Client-ID": client_id}
        response = requests.get(f"https://api.twitch.tv/helix/users?login=streamername", headers=headers)
        channel_id = response.json()["data"][0]["id"]


        headers = {"Authorization": f"Bearer {access_token}", "Client-ID": client_id}
        response = requests.get(f"https://api.twitch.tv/helix/subscriptions?broadcaster_id={channel_id}", headers=headers)
        rep = response.json()
        print(rep)
        self.subscribers = response.json()["data"]

        print(f"Here: {self.subscribers}")


    async def get_client_id(self):
        """Read get_client_id from file or prompt user if not found"""

        current_log_prefix = self.logger_prefix + "get_client_id:"

        if os.path.exists(config.CLIENT_ID_FILE):
            with open(config.CLIENT_ID_FILE, 'r') as f:
                clientid = f.read().strip()
                self.logger.info(f"{current_log_prefix}ClientID loaded from file.")
                return clientid
        else:
            # Exit gracefully
            self.logger.error(f"{current_log_prefix}ClientID file not found: {config.OAUTH_TOKEN_FILE}")
            raise SystemExit(1)



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

            # await self.sending_msg_to_chat("AlbotKeinstein up and running! <3")
            await self.albot_msg_to_chat("AlbotKeinstein up and running! <3")


            # await self.get_subscribers_list()
            # print("Here we go!!")
            # print(f"{self.subscribers}")




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
            self.logger.info(f"{current_log_prefix}Tried to send to Twitch chat:{msg_to_send}, but failed due to /{e}/")
