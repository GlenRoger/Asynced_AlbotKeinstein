import utils.logger as logger
import utils.TwitchConnection as TC
from utils.overlay_system import OverlaySystem
import asyncio

import sys
from utils.overlay import OverlayWindow
from utils.overlay_bridge import OverlayBridge
from PySide6.QtWidgets import QApplication

class AlbotBrain:

    def __init__(self):

        self.logger_prefix = "AlbotBrain:"

        #This logger is going to be passed on to other objects to be used for logging the full bot's life cycle
        self.logger = logger.LogThis().get_logger()
        self.logger.info("ALBOTKEINSTEIN INITIALIZING ANEW!\n###############################################################################")

        # Initialize Qt Application
        self.app = QApplication.instance() or QApplication(sys.argv)

        # Create overlay bridge
        self.overlay_bridge = OverlayBridge(self.logger)
        self.logger.info(f"{self.logger_prefix}Overlay bridge created")

        # Initialize overlay window with bridge
        self.overlay = OverlayWindow(self.logger)
        self.overlay.connect_bridge(self.overlay_bridge)
        self.logger.info(f"{self.logger_prefix}Overlay window created and connected to bridge")


        #Connect to Twitch chat
        self.TwitchConnector = TC.TwitchConnection(self.logger)

        # Add bridge reference to TwitchConnection
        self.TwitchConnector.overlay_bridge = self.overlay_bridge

        #Make overlay - FastAPI-style delete later??
        # self.overlay = OverlaySystem(self.logger)

        # self.TwitchConnector.add_overlay_connection(self.overlay)

    async def start(self):
        current_log_prefix = self.logger_prefix + "start:"
        print("There's work to be done!")

        # Try sending a message through the bridge AFTER delay
        asyncio.create_task(self.delayed_test_message())

        # Show the overlay with initial message via the bridge
        # self.overlay_bridge.show_message("Hi there!")
        # self.logger.info(f"{current_log_prefix}Overlay window shown via bridge")

        #The analysing of Twich chat is going on in the background
        try:

            self.message_task                   = asyncio.create_task(self.TwitchConnector.start_messsage_loop())
            self.message_pile_queue_organizer   = asyncio.create_task(self.TwitchConnector.commands_to_check_list_divide_into_queues())
            self.message_pile_queue_handler     = asyncio.create_task(self.TwitchConnector.run_commands_according_to_priority())
            # self.overlay_task                   = asyncio.create_task(self.overlay.start_server())

            # Add overlay processing task - PySide6
            self.overlay_task = asyncio.create_task(self.process_qt_events())


            tasks = [self.message_task, self.message_pile_queue_organizer, self.message_pile_queue_handler, self.overlay_task]


            # tasks = [self.message_task, self.message_pile_queue_organizer, self.message_pile_queue_handler, self.overlay_task]
            self.logger.info(f"{current_log_prefix}Created {len(tasks)} tasks")
            
            return tasks

        except Exception as e:
            self.logger.error(f"{current_log_prefix}Bot stopped due to an unexpected error -> /{e}/")

        #Other things needed to be done?

    async def delayed_test_message(self):
        """Send a test message after a delay to ensure everything is initialized"""
        await asyncio.sleep(3)  # Wait 3 seconds
        self.logger.info(f"{self.logger_prefix}Sending delayed test message via bridge")
        self.overlay_bridge.show_message("Visuals active!")

    #PySide6 stuff
    async def process_qt_events(self):
        """Process Qt events in an asyncio-friendly way"""
        current_log_prefix = self.logger_prefix + "process_qt_events:"
        self.logger.info(f"{current_log_prefix}Starting Qt event processing")
        
        while True:
            # Process Qt events
            self.app.processEvents()
            # Yield to other tasks
            await asyncio.sleep(0.1)  # 10ms is usually a good balance