import logging
import datetime


#INFO
#DEBUG
#WARNING
#ERROR
#CRITICAL

class LogThis:

    def __init__(self):

        current_time = datetime.datetime.now()
        log_filename = f"bog_{current_time.strftime('%Y%m%d_%H%M%S')}.log"

        #Set up file to log to
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"./logs/{log_filename}", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger  = logging.getLogger("twitch_bot")

    def info(sef):
        pass

    def get_logger(self):
        return self.logger
