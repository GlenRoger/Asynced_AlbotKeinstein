import logging
import datetime




#INFO
#DEBUG
#WARNING
#ERROR
#CRITICAL

class DatebaseLogger(logging.Logger):

    def set_db(self, db, albotversion):
        self.db = db
        self.ALBOTVERSION = albotversion
        
    def info(self, message, *args, **kwargs):
        # Write to database
        self._write_to_info_register("INFO", message)
        # Call parent logger
        super().info(message, *args, **kwargs)


    def warning(self, message, *args, **kwargs):
        self._write_to_errors_register("WARNING", message)
        self.logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._write_to_errors_register("ERROR", message)
        super().error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self._write_to_errors_register("CRITICAL", message)
        super().critical(message, *args, **kwargs)


    def _write_to_info_register(self, level, message):
        # print(f"Får inn level:{level} og message {message}")
        pass

#"BOT_VERSION": self.ALBOTVERSION, 
        # #timestamp, action, invoked_by, function_name, parameters, bot_version

        # action = ""
        # invoked_by = ""
        # function_name = ""

        # if "PLAY_MESSAGE" in message.upper():
        #     action = "Showing gif: "
        #     invoked_by = "albot"
        #     function_name = "play_message"
        # elif "BUILD_GIF_GREETINGS" in message.upper():





    def _write_to_errors_register(self, level, message):

        #Ønsker ikke at logging skal bryte sammen
        try:
                

            table_name = "Errors_register"
            severity = ""

            if level.upper() == 'WARNING':
                severity = 'medium'
            elif level.upper() == 'ERROR':
                severity = 'high'
            elif level.upper() == 'CRITICAL':
                severity = 'extreme'


            print(f"Getting message: {message}")

            find_component = message.split('=>')
            component_name = find_component[0]
            not_component = find_component[1]

            print(f"component: {component_name}")
            print(f"not_component: {not_component}")

            find_rest_info = not_component.split(':')

            print(f"find_rest_info: {find_rest_info}")

            function_name = find_rest_info[0]
            print(f"function_name: {function_name}")


            error_message = " ".join(find_rest_info[1:])
            print(f"error_message: {error_message}")
            error_message = error_message.replace('\\', '')
            error_message = error_message.replace('{', '')
            error_message = error_message.replace('}', '')
            error_message = error_message.replace('"', '')

            print(f"error_message fixed: {error_message}")


            value_dict = {"BOT_VERSION": self.ALBOTVERSION, "COMPONENT": component_name, "FUNCTION_NAME": function_name, "SEVERITY": severity, "ERROR_MESSAGE": error_message}
            self.db.insert_into(table_name, value_dict)
        except Exception as e:
            print(f"\n\n\n\t\tError logger.py: Couldn't write to database!!!\n\t\t{e}\n\n\n")



class LogThis():

    def __init__(self, db, ALBOTVERSION):
        self.ALBOTVERSION = ALBOTVERSION

        self.db = db

        current_time = datetime.datetime.now()
        log_filename = f"log_{current_time.strftime('%Y%m%d_%H%M%S')}.log"

        #Set up file to log to
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"./logs/{log_filename}", encoding='utf-8'),
                logging.StreamHandler()

            ]
        )


        logging.setLoggerClass(DatebaseLogger)


#        self.logger = super().logging.__init__("twitch_bot")
        self.logger  = logging.getLogger("twitch_bot")

        self.logger.set_db(self.db, self.ALBOTVERSION)

#        self.logger.set_db(self.db)


    def get_logger(self):
        return self.logger

