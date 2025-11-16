import utils.logger as logger
import utils.TwitchConnection as TC
import asyncio

import sys
from utils.overlay import OverlayWindow
from utils.overlay_bridge import OverlayBridge
from PySide6.QtWidgets import QApplication

from utils.UserRoleManager      import UserRoleManager
from utils.Message_central      import Message_central
from commands.command_handler   import Command_central
from commands.command_runner    import Command_runner
from utils.overlay_runner       import Overlay_runner
import utils.GifHandler as GH

from utils.databasecontroller import DatabaseController

import random

# from commands.overlay_runner import 

class AlbotBrain:

    def __init__(self):

        self.logger_prefix = "AlbotBrain:"

        #Adding database
        self.db = DatabaseController()


        #This logger is going to be passed on to other objects to be used for logging the full bot's life cycle
        self.logger = logger.LogThis(self.db).get_logger()
        self.logger.info("ALBOTKEINSTEIN INITIALIZING ANEW!\n###############################################################################")


        # Initialize Qt Application
        self.app = QApplication.instance() or QApplication(sys.argv)

        # Create overlay bridge
        self.overlay_bridge = OverlayBridge(self.logger)
        self.logger.info(f"{self.logger_prefix}Overlay bridge created")

        self.gif_handler    = GH.GifHandler(self.logger)

        # Initialize overlay window with bridge
        self.overlay = OverlayWindow(self.logger)
        self.overlay.connect_bridge(self.overlay_bridge)
        self.logger.info(f"{self.logger_prefix}Overlay window created and connected to bridge")


        #Connect to Twitch chat
        self.TwitchConnector = TC.TwitchConnection(self.logger)

        #Message central controls messages in and out
        self.msg_central = Message_central(self.logger)

        self.usermanagement = UserRoleManager(self.logger)
        self.cmd_central = Command_central(self.logger)

        self.cmd_runner = Command_runner(self.logger)
        self.cmd_runner.set_command_handler(self.cmd_central)   #The cmd_central will execute commands

        self.overlay_runner = Overlay_runner(self.logger)
        self.overlay_runner.set_command_handler(self.cmd_central)   #The cmd_central will execute commands
        self.overlay_runner.set_gif_handler(self.gif_handler)
        self.overlay_runner.set_overlay(self.overlay)  #Kun for feedback på når ledig for å kjøre neste command
        
        self.cmd_central.set_overlay_runner(self.overlay_runner)
   
        self.cmd_central.set_albot_brain(self)      #For use of shutdown-command
        self.cmd_central.set_cmd_runner(self.cmd_runner)

        self.msg_central.set_tc(self.TwitchConnector)
        self.msg_central.set_ch(self.cmd_central)

        self.cmd_central.set_msg_central(self.msg_central)   #For use of shutdown-command last message
        self.cmd_central.read_commands_from_files() #Setup commands that can be used
        self.cmd_central.set_gifhandler(self.gif_handler)
     
        # Add bridge reference to TwitchConnection
        self.TwitchConnector.set_overlay_runner(self.overlay_runner)
        self.overlay_runner.set_overlay_bridge(self.overlay_bridge)

        #A link back to be able to shut down entirely the program
        self.TwitchConnector.set_albot_brain(self)

        self.TwitchConnector.set_msg_central(self.msg_central)               #For å kunne sende meldinger
        self.TwitchConnector.set_user_manager(self.usermanagement)  #For å fylle på oauth-info til usermanager

        self.cmd_central.set_user_manager(self.usermanagement)      #For å sjekke brukere/seere/chattere 's roller/privilegier.


        #Make overlay - FastAPI-style delete later??
        # self.overlay = OverlaySystem(self.logger)

        # self.TwitchConnector.add_overlay_connection(self.overlay)

        self.shutdown_requested = False  # Add this flag

    async def get_commands_from_db(self):
        # pass
        while True:
            


            min_min_wait = 10
            max_min_wait = 10


            time_between_5_min_and_10_min = random.randint(min_min_wait*60, max_min_wait*60)

            time_between_5_min_and_10_min = 15

            #XMAS_2025_GIFS
            gif_to_show = self.gif_handler.get_random_gif_from_list("XMAS_2025_GIFS")

            # gif_to_show = self.gif_handler.get_random_TSTWTGIFS_list()
            print(f"\n\n\n\tGifToShow:{gif_to_show}\n\n\n")
            await self.overlay_runner.make_tstwtgif_message(gif_to_show)

            await asyncio.sleep(time_between_5_min_and_10_min)


    async def start(self):
        current_log_prefix = self.logger_prefix + "start:"
        self.logger.info(f"{current_log_prefix}Albot brain starting up!")
        print("There's work to be done!")

        await self.overlay_runner.run_gif_setup()

        self.logger.info(f"{current_log_prefix}Albot brain starting up!")

        # Try sending a message through the bridge AFTER delay
        # asyncio.create_task(self.delayed_test_message())

        # Show the overlay with initial message via the bridge
        # self.overlay_bridge.show_message("Hi there!")
        # self.logger.info(f"{current_log_prefix}Overlay window shown via bridge")

        #The analysing of Twich chat is going on in the background
        try:

            self.message_task                   = asyncio.create_task(self.TwitchConnector.start_messsage_loop())
            self.run_commands                   = asyncio.create_task(self.cmd_runner.run_commands_from_queue())
            self.run_overlays                   = asyncio.create_task(self.overlay_runner.run_commands_from_queue())
            self.get_db_cmds                    = asyncio.create_task(self.get_commands_from_db())
            # self.message_pile_queue_organizer   = asyncio.create_task(self.TwitchConnector.commands_to_check_list_divide_into_queues())
            # self.message_pile_queue_handler     = asyncio.create_task(self.TwitchConnector.run_commands_according_to_priority())
            # self.overlay_task_old                   = asyncio.create_task(self.overlay.start_server())

            # Add overlay processing task - PySide6
            self.overlay_task = asyncio.create_task(self.process_qt_events())


            #This is the complete one!
            # tasks = [self.message_task, self.message_pile_queue_organizer, self.message_pile_queue_handler, self.overlay_task]

            tasks = [self.message_task, self.run_commands, self.run_overlays, self.get_db_cmds, self.overlay_task]

            # tasks = [self.message_task, self.message_pile_queue_organizer, self.message_pile_queue_handler]

            # tasks = [self.message_task, self.message_pile_queue_organizer, self.message_pile_queue_handler, self.overlay_task]
            self.logger.info(f"{current_log_prefix}Created {len(tasks)} tasks")
            
            return tasks

        except Exception as e:
            self.logger.error(f"{current_log_prefix}Bot stopped due to an unexpected error -> /{e}/")

        #Other things needed to be done?

    #Fjerne denne?
    async def delayed_test_message(self):
        """Send a test message after a delay to ensure everything is initialized"""
        current_log_prefix = self.logger_prefix + "delayed_test_message:"
        await asyncio.sleep(3)  # Wait 3 seconds
        self.logger.info(f"{current_log_prefix}Sending delayed test message via bridge")
        # self.overlay_bridge.show_message("Visuals active!")

        self.overlay_bridge.play_message("Visuals active", duration = 5000)


        await asyncio.sleep(1)  # Wait a bit for the message to display
        # self.overlay_bridge.animate_message("bounce")

    #PySide6 stuff
    async def process_qt_events(self):
        """Process Qt events in an asyncio-friendly way"""
        current_log_prefix = self.logger_prefix + "process_qt_events:"
        self.logger.info(f"{current_log_prefix}Starting Qt event processing")
        
        while True:
            # Process Qt events
            self.app.processEvents()
            # Yield to other tasks
            await asyncio.sleep(0.01)  # 10ms is usually a good balance


        
    #Stopping entire program when flag i set
    async def shutdown(self):
        """Gracefully shut down the bot"""
        current_log_prefix = self.logger_prefix + "shutdown:"
        self.logger.info(f"{current_log_prefix}Shutdown requested, stopping all tasks...")
        
        self.shutdown_requested = True
        
        # Stop the TwitchConnection
        if hasattr(self, 'TwitchConnector'):
            await self.TwitchConnector.shutdown()
        
        # Close the overlay
        if hasattr(self, 'overlay'):
            self.overlay.close()
        
        # Cancel all running tasks
        tasks_to_cancel = []
        if hasattr(self, 'message_task'):
            tasks_to_cancel.append(self.message_task)
        # if hasattr(self, 'message_pile_queue_organizer'):
        #     tasks_to_cancel.append(self.message_pile_queue_organizer)
        # if hasattr(self, 'message_pile_queue_handler'):
        #     tasks_to_cancel.append(self.message_pile_queue_handler)
        # if hasattr(self, 'overlay_task'):
        #     tasks_to_cancel.append(self.overlay_task)
        
        for task in tasks_to_cancel:
            if not task.done():
                task.cancel()
                
        self.logger.info(f"{current_log_prefix}All tasks cancelled, shutting down...")