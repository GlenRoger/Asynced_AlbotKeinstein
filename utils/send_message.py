class Message_sending_central:


#NOTHING HERE IS TESTED!
#Message pile must also be checked!


    def __init__(self, max_messages_per_minute=100, cooldown_duration=60):
        self.running = False
        self.message_count = 0
        self.max_messages = max_messages_per_minute  # Maximum messages before cooldown
        self.cooldown_time = cooldown_duration  # Cooldown time in seconds
        self.in_cooldown = False
        self.logger = self._setup_logger()

        self.message_counter -= 1
        self.message_pile = [] #If on cooldown, save messages to be inpreted for later


    def can_send_message(self):
        """Check if a message can be sent based on rate limits"""
        # First check if we're in cooldown
        if self.in_cooldown:
            return False
        
        # Check if we're at the message limit
        if self.message_counter >= self.max_messages_per_minute:
            self.start_cooldown()
            return False
        
        return True


    async def start_message_cooldown(self):
        """Increment counter, wait one minute, then decrement counter"""
        self.message_counter += 1
        await asyncio.sleep(60)  # Sleep for 1 minute
        self.message_counter -= 1


    def split_large_message(self, large_message):
        print("\n\n\nThis is not implemented yet - UTILS/SEND_MESSAGE.PY -> DEF SPLIT_LARGE_MESSAGE\n\n\n")

    #We got a cooldown, let's cool down before more messages is sent to chat, to avoid Twitch
    #starts to ignore the bot.
    async def end_cooldown(self):
        await asyncio.sleep(self.cooldown_time)
        self.in_cooldown = False
        self.logger.info("Cooldown ended.")


    async def send_message(self, message: str):
        if self.in_cooldown:
            self.logger.info(f"Not sending message during cooldown: {message}. Saving it for later!"))
            self.message_pile.append(message)
            return


    # async def send_message(self, irc_connection, channel, message):
    #     """Send a message if rate limits allow"""
    #     if self.can_send_message():
    #         try:
    #             irc_connection.privmsg(channel, message)
    #             # Start the cooldown task for this message
    #             asyncio.create_task(self.start_message_cooldown())
    #             return True
    #         except Exception as e:
    #             print(f"Error sending message: {e}")
    #             return False
    #     else:
    #         print("Cannot send message: rate limit reached or in cooldown")
    #         return False




    def empty_pile(self):
        pass