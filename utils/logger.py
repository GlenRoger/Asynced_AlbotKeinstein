import logging



#INFO
#DEBUG
#WARNING
#ERROR
#CRITICAL

class LogThis:

    def __init__(self):

        #Set up file to log to
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("bot.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger  = logging.getLogger("twitch_bot")

    def get_logger(self):
        return self.logger
