import config
import asyncio

class Message_sending_central:


#NOTHING HERE IS TESTED!
#Message pile must also be checked!


    def __init__(self, logger, max_messages_per_minute=60, cooldown_duration=60):
        self.logger_prefix = "utils/send_message.Message_sending_central=>"

        # self.running = False
        self.message_id = 0 #incremental per new message sent
        self.count_messages = 58
        self.max_messages = max_messages_per_minute  # Maximum messages before cooldown
        self.cooldown_time = cooldown_duration  # Cooldown time in seconds
        self.inCooldownMode = False

        #For every message we create an asyncio-task on cooldown. Need to clean up when bot shuts down.
        self.message_sent_tasks_list = []

        self.logger = logger

        # self.message_counter -= 1
        self.message_pile = [] #If on cooldown, save messages to be inpreted for later



    #######################################################################
    #################### CHECKING IF MESSAGE CAN BE SENT ##################
    #######################################################################

    #Check if we're not spamming/in cooldown chat already 
    #Check if the message is more than 500 characters, if so then split it. 
    #Returning [True/False, [a list]].
    def check_if_can_be_sent(self, outgoing_chat_msg):

        #Checking if message is larger than 480 characters, if it is, then split it.
        #After this changed outgoing_chat_msg into a list.
        if len(outgoing_chat_msg) < 485:
            outgoing_chat_msg = self.split_large_message(outgoing_chat_msg)

        #We are already in quarantine for sending too many messages
        #put message in the message pile and send it later.
        if self.inCooldownMode:
            for msgs in outgoing_chat_msg:
                self.message_pile.append(msgs)
            return [False, []]

        #We're not in cooldown for sending too many messages -
        #so check we should be or not, if we should be we start the cooldown task.
        elif self.count_messages >= self.max_messages:
            asyncio.create_task(self.startCooldownMode())

        #We're not in cooldown, so we can send the messsage, now the message
        #is a list of message chunks. Biggest size 485.
        else:
            return [True, outgoing_chat_msg]

    #Splitting large messages:
    def split_large_message(self, large_message):
        current_log_prefix = self.logger_prefix + "split_large_message:"
        self.logger.info(f"{current_log_prefix}Splitting message of {len(large_message)} characters")
        
        chunk_size = 485
        message_chunks = []
        
        # Split the message into chunks of 485 characters
        for i in range(0, len(large_message), chunk_size):
            chunk = large_message[i:i + chunk_size]
            message_chunks.append(chunk)
        
        self.logger.info(f"{current_log_prefix}Split into {len(message_chunks)} chunks")
        return message_chunks

    #Call this one when a new message has been sent
    async def message_sent(self):
        self.message_sent_tasks_list.append(asyncio.create_task(self.track_messages_sent()))

    async def track_messages_sent(self):
        current_log_prefix = self.logger_prefix + "track_messages_sent:"
        self.count_messages += 1
        self.message_id     += 1
        cur_message_id = self.message_id
        self.logger.info(f"{current_log_prefix}Tracking another message, this is number #{cur_message_id}")

        await asyncio.sleep(60)  # Need to await here

        self.logger.info(f"{current_log_prefix}Tracking on message removed for message number #{cur_message_id}")
        self.logger.info(f"{current_log_prefix}Popping: {self.message_sent_tasks_list[0]}")
        self.message_sent_tasks_list.pop(0)  #Task done pop it out from list! Always the first element, fifo-queue.
        self.count_messages -= 1


    async def clean_up_message_sent_tasks_list(self):
        current_log_prefix = self.logger_prefix + "clean_up_message_sent_tasks_list:"

        cancelled_msgs_counter = 0

        for task in self.message_sent_tasks_list:
            if not task.done():
                cancelled_msgs_counter += 1
                task.cancel()

        self.logger.info(f"{current_log_prefix}Cleaning up messages-tasks-list. Number of tasks cancelled: {cancelled_msgs_counter}")


    async def startCooldownMode(self):
        self.inCooldownMode = True
        await asyncio.sleep(60)  # Need to await here

        #Time to catch up on the message-pile, when it's empty we can go on as normal.
        if len(self.message_pile) == 0:
            self.inCooldownMode = False

    #Put priorities on the message pile before getting back to normal.
    def check_message_pile(self):
        current_log_prefix = self.logger_prefix + "check_message_pile:"

        self.logger.info(f"{current_log_prefix}Messages left in message-pile: {len(self.message_pile)}.")

        if len(self.message_pile) == 0 and self.count_messages <= self.max_messages and not self.inCooldownMode:
            self.logger.info(f"{current_log_prefix}Message-pile empty => #{len(self.message_pile)} messages left.")
            self.inCooldownMode = True
            return []

        if len(self.message_pile) != 0 and self.count_messages <= self.max_messages and not self.inCooldownMode:
            self.logger.info(f"{current_log_prefix}Emptying another message from the message-pile.")
            return self.message_pile.pop(0)


    ########################################################################
    ############### CHECKING IF INCOMMING CHAT MESSAGE IS OKAY #############
    ########################################################################    

    def analyse_message_and_check_if_okay(self, chat_msg):
        """Checks amessage step by step if is a command or something to reply to and if the sender
        is allowed to use this command. Returns a list of messages for response. Has to be a list,
        because a response can be more then 500 characters long and therefor needed to be split ut.
        Most of the time it will be a list with only one message to be sent. If it is empty, there
        will be no response due to not received a message, message has invalid characters, sendt by a
        unkown user or a user who can not use this command."""

        current_log_prefix = self.logger_prefix + "analyse_message_and_check_if_okay:"
        

        #Checking for messages starting with %
        [sender, chat_msg_sent] = self.find_msg_and_sender(chat_msg)

        if sender == config.BOT_USERNAME:
            self.logger.info(f"{current_log_prefix}AlbotKeinstein wrote this itself (ignoring it): {chat_msg}") #chat_msg_sent is empty if check fails, use chat_msg
            return ["", ""]

        if not chat_msg_sent:
            self.logger.info(f"{current_log_prefix}Not a command: {chat_msg}") #chat_msg_sent is empty if check fails, use chat_msg
            return ["", ""]

        self.logger.info(f"{current_log_prefix}Passed start with '%' and not empty-check:{chat_msg}")

        #Checking for illegal characters that can be used for code injections
        if not self.is_safe_command(chat_msg_sent):
            self.logger.info(f"{current_log_prefix}Not a analysed any further:/{chat_msg_sent}/")
            return ["", ""]

        self.logger.info(f"{current_log_prefix}Passed safety - legal characters-check:{chat_msg}")

        #MORE TO CHECK?

        self.logger.info(f"{current_log_prefix}So far so good on this one:{chat_msg}")

        return[sender, chat_msg_sent]


    #STEP 1 - Splitting the message into sender and message
    def find_msg_and_sender(self, chat_msg):

        current_log_prefix = self.logger_prefix + "find_msg_and_sender:"
        # :coolingenwastaken!coolingenwastaken@coolingenwastaken.tmi.twitch.tv PRIVMSG #coolingenwastaken :%hei

        split_chat = chat_msg.split(' ')

        is_PRIVMSG = split_chat[1] == "PRIVMSG"

        if not is_PRIVMSG:
            self.logger.info(f"{current_log_prefix}Not a PRIVMSG-message - not for us:{chat_msg}")
            return["",""]


        is_command = split_chat[3].startswith(f":{config.PREFIX_FOR_BOT_TO_READ}")

        if is_command:
            split_chat[3] = split_chat[3][2:]
            split_chat[-1] = split_chat[-1].rstrip()
            command_rebuild = (' ').join(split_chat[3:])
            username_sending_message = split_chat[2][1:]
            return([username_sending_message, command_rebuild])
        else:
            self.logger.info(f"{current_log_prefix}Doesn't start with:/{config.PREFIX_FOR_BOT_TO_READ}/:{chat_msg}")
            return["",""]

    #STEP 2 - Checking if the sent message contains any characters not allowed?
    #Don't want code-injections!
    def is_safe_command(self, chat_msg_sent):
        current_log_prefix = self.logger_prefix + "is_safe_command:"

        # Define explicitly what characters are allowed
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_+- øæåÆØÅ')
        
        # Check each character in the command
        disallowed_found = []
        for char in chat_msg_sent:
            if char not in allowed_chars:
                disallowed_found.append(char)
        
        # If we found any disallowed characters
        if disallowed_found:
            disallowed_str = ', '.join([f"'{c}'" for c in set(disallowed_found)])
            self.logger.info(f"{current_log_prefix}Command rejected. Disallowed characters found: {disallowed_str} in: {chat_msg_sent}")
            return False
        
        return True  


    # def can_send_message(self):
    #     """Check if a message can be sent based on rate limits"""
    #     # First check if we're in cooldown
    #     if self.in_cooldown:
    #         return False
        
    #     # Check if we're at the message limit
    #     if self.message_counter >= self.max_messages_per_minute:
    #         self.start_cooldown()
    #         return False
        
    #     return True


    # async def start_message_cooldown(self):
    #     """Increment counter, wait one minute, then decrement counter"""
    #     self.message_counter += 1
    #     await asyncio.sleep(60)  # Sleep for 1 minute
    #     self.message_counter -= 1


    # def split_large_message(self, large_message):
    #     print("\n\n\nThis is not implemented yet - UTILS/SEND_MESSAGE.PY -> DEF SPLIT_LARGE_MESSAGE\n\n\n")

    # #We got a cooldown, let's cool down before more messages is sent to chat, to avoid Twitch
    # #starts to ignore the bot.
    # async def end_cooldown(self):
    #     await asyncio.sleep(self.cooldown_time)
    #     self.in_cooldown = False
    #     self.logger.info("Cooldown ended.")


    # async def send_message(self, message: str):
    #     if self.in_cooldown:
    #         self.logger.info(f"Not sending message during cooldown: {message}. Saving it for later!"))
    #         self.message_pile.append(message)
    #         return


    # # async def send_message(self, irc_connection, channel, message):
    # #     """Send a message if rate limits allow"""
    # #     if self.can_send_message():
    # #         try:
    # #             irc_connection.PRIVMSG(channel, message)
    # #             # Start the cooldown task for this message
    # #             asyncio.create_task(self.start_message_cooldown())
    # #             return True
    # #         except Exception as e:
    # #             print(f"Error sending message: {e}")
    # #             return False
    # #     else:
    # #         print("Cannot send message: rate limit reached or in cooldown")
    # #         return False




    # def empty_pile(self):
    #     pass