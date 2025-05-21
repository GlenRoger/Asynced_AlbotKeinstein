import sys
import os
import config
# import asyncio
# import websockets
# import os
# import utils.send_message as sm
# import commands.command_handler as ch
# import requests
# import time
# import utils.GifHandler as GH

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from utils.send_message import Message_sending_central
# from commands.command_handler import Command_central
# from utils.logger import LogThis


# from utils.TwitchConnection import TwitchConnection as TC
# from utils.TwitchConnection import TwitchConnection
from utils.logger import LogThis
from commands.command_handler import Albot_Command



# def test_commanded_change_sleep():
# def test_commanded_change_wakeup():
# def test_commanded_change_quit():


#SLEEP,SILENCE;cmd;TSTWTMEMBERS;"I'll go and relax for now! Be back later! <3"
#AWAKE,WAKEUP,UNSLEEP;cmd;TSTWTMEMBERS;"Ah! I'm back again. Missed me? :D"
#ALBOTREST,SHUTDOWN,QUIT;CMD;TSTWTMEMBERS;"Alright, I'm outta here! Have a great time everyone! Miss you! <3"

# Albot_Command
                    # cmd_callings    = line_list[0].split(',')
                    # cmd_type        = line_list[1]
                    # cmd_users       = line_list[2].split(',')
                    # cmd_response    = line_list[3][1:-1]  #Fjerner første og siste "-tegn





def sum_this():
    one = 2+2
    assert one == 4

# def test_commanded_change_commands():
#     logger = LogThis().get_logger()
    
#     twitch_connection = TwitchConnection(logger)

#     cmd_obj = Albot_Command(['SLEEP','SILENCE'], 'cmd', 'TSTWTMEMBERS', "I'll go and relax for now! Be back later! <3")

#     result = twitch_connection.commanded_change(cmd_obj)

#     assert twitch_connection.isNotSilenced == True
#     assert result == True