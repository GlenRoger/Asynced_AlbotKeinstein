import utils.logger as logger
import utils.TwitchConnection as TC
from utils.overlay_system import OverlaySystem
import asyncio

class AlbotBrain:

    def __init__(self):

        self.logger_prefix = "AlbotBrain:"

        #This logger is going to be passed on to other objects to be used for logging the full bot's life cycle
        self.logger = logger.LogThis().get_logger()
        self.logger.info("ALBOTKEINSTEIN INITIALIZING ANEW!\n###############################################################################")

        #Connect to Twitch chat
        self.TwitchConnector = TC.TwitchConnection(self.logger)

        #Make overlay
        self.overlay = OverlaySystem(self.logger)

        self.TwitchConnector.add_overlay_connection(self.overlay)

    async def start(self):
        current_log_prefix = self.logger_prefix + "start:"
        print("There's work to be done!")

        #The analysing of Twich chat is going on in the background
        try:

            self.message_task                   = asyncio.create_task(self.TwitchConnector.start_messsage_loop())
            self.message_pile_queue_organizer   = asyncio.create_task(self.TwitchConnector.commands_to_check_list_divide_into_queues())
            self.message_pile_queue_handler     = asyncio.create_task(self.TwitchConnector.run_commands_according_to_priority())
            self.overlay_task                   = asyncio.create_task(self.overlay.start_server())

            tasks = [self.message_task, self.message_pile_queue_organizer, self.message_pile_queue_handler, self.overlay_task]
            self.logger.info(f"{current_log_prefix}Created {len(tasks)} tasks")
            
            return tasks

        except Exception as e:
            self.logger.error(f"{current_log_prefix}Bot stopped due to an unexpected error -> /{e}/")

        #Other things needed to be done?