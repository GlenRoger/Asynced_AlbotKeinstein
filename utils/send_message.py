import asyncio
import logging


class Message_sending_central:


#NOTHING HERE IS TESTED!
#Message pile must also be checked!


    def __init__(self, websocket_out, channel_visited, max_messages_per_minute=100, cooldown_duration=60):
        self.websocket = websocket_out
        self.channel = channel_visited
        self.running = False
        self.message_count = 0
        self.max_messages = max_messages_per_minute  # Maximum messages before cooldown
        self.cooldown_time = cooldown_duration  # Cooldown time in seconds
        self.in_cooldown = False
        self.logger = self._setup_logger()

        self.message_counter = 0
        self.message_pile = [] #If on cooldown, save messages to be inpreted for later


    def _setup_logger(self):
        # Basic logger setup
        logger = logging.getLogger("MessageSender")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger


    def can_send_message(self):
        """Check if a message can be sent based on rate limits"""
        # First check if we're in cooldown
        if self.in_cooldown:
            self.logger.info(f"Currently the bot is in cooldown. {self.message_counter} messages has been sent.")
            print(f"Currently the bot is in cooldown. {self.message_counter} messages has been sent.")
            return False
        
        self.logger.info("Bot not in cooldown!")
        print("Bot not in cooldown!")
        return True


    async def keep_track_of_how_many_message_sent(self):
        """Increment counter, wait one minute, then decrement counter"""
        self.message_counter += 1

        self.logger.info(f"New messages sent: {self.message_counter}")

        print(f"New messages sent:{self.message_counter}")

        asyncio.create_task(self._decrement_counter_after_delay())


    async def _decrement_counter_after_delay(self):
        await asyncio.sleep(60)
        self.message_counter -= 1
        self.logger.info(f"Message counter decremented. Remaining: {self.message_counter}")
        print(f"Another is done for sleep counting. Message sent left in quaranteen:{self.message_counter}")

    def split_large_message(self, large_message):
        print("\n\n\nThis is not implemented yet - UTILS/SEND_MESSAGE.PY -> DEF SPLIT_LARGE_MESSAGE\n\n\n")

    #We got a cooldown, let's cool down before more messages is sent to chat, to avoid Twitch
    #starts to ignore the bot.
    async def cooldown(self):
        self.logger.info("Entering cool-down mode for one minute!")
        print("Entering cool-down mode for one minute!")
        self.in_cooldown = True
        await asyncio.sleep(self.cooldown_time)
        self.in_cooldown = False
        self.logger.info("Cooldown mode ended.")
        
        # Process any messages in the pile
        await self.process_message_pile()


    async def process_message_pile(self):
        """Process messages that accumulated during cooldown"""
        if not self.message_pile:
            return
            
        self.logger.info(f"Processing {len(self.message_pile)} messages from the pile")
        # Take a copy of the message pile and clear the original
        messages_to_process = self.message_pile.copy()
        self.message_pile.clear()
        
        # Process each message
        for message in messages_to_process:
            # Check if we can send without going into cooldown again
            if self.message_counter < self.max_messages:
                await self.send_message(message)
            else:
                # Put back in pile and exit - we'll try again after next cooldown
                self.message_pile.append(message)
                self.logger.info("Hit message limit while processing pile. Remaining messages saved.")
                break



    async def send_message(self, message: str):
        if self.in_cooldown:
            self.logger.info(f"Not sending message during cooldown: {message}. Saving it for later!")
            self.message_pile.append(message)
            return

        # Check if this message would put us over the limit
        if self.message_counter >= self.max_messages - 1:
            self.logger.info(f"Message limit nearly reached ({self.message_counter}/{self.max_messages}). Entering cooldown.")
            self.message_pile.append(message)
            await self.cooldown()
            return


        self.logger.info(f"Messsage being sent: {message}.")
        await self.websocket.send(f"PRIVMSG #{self.channel} :{message}")
        await self.keep_track_of_how_many_message_sent()



    def empty_pile(self):
        pass