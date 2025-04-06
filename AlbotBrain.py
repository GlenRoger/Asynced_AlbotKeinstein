import utils.logger as logger
import utils.TwitchConnection as TC
import asyncio

class AlbotBrain:

    def __init__(self):

        self.logger_prefix = "AlbotBrain:"

        #This logger is going to be passed on to other objects to be used for logging the full bot's life cycle
        self.logger = logger.LogThis().get_logger()
        self.logger.info("ALBOTKEINSTEIN INITIALIZING ANEW!\n###############################################################################")

        #Connect to Twitch chat
        self.TwitchConnector = TC.TwitchConnection(self.logger)


    async def start(self):
        print("There's work to be done!")

        #The analysing of Twich chat is going on in the background
        try:
            self.message_task = asyncio.create_task(self.TwitchConnector.start_messsage_loop())
            return self.message_task
            #await self.TwitchConnector.start_messsage_loop()
        except Exception as e:
            self.logger.error(f"{self.current_log_prefix}Bot stopped due to an unexpected error -> /{e}/")

        #Other things needed to be done?