#Checking if we really got a valid command by a user who is allowed to use it
import importlib
import config

class Command_central:


    def __init__(self, logger):
        self.logger_prefix = "commands/command_handler.Command_central=>"
        self.logger = logger

        self.logger.info(f"{self.logger_prefix}Command_central successfully initialized!")

    def collect_commands(self):
        pass
        

    #ADD ADVANCED COMMANDS HERE AND ADD THEM TO THE COLLECT_COMMANDS MANUALLY
    #These can also be saved in a file, though need extra programming in TwitchConnection.py
    def advanced_commands(self, sender, cmd):
        current_log_prefix = self.logger_prefix + "advanced_commands:"

        if not sender in config.STREAMERS:
            self.logger.info(f"{current_log_prefix}User {sender} not permitted to use command - STREAMERS only! {cmd}")
            return ["", "", ""]

        #SCARY ONE???
        if cmd.upper() == 'READCONFIGAGAIN' or cmd.upper() == 'RECONFIG' or cmd.upper() == 'REEVALUATE':
            self.logger.info(f"{self.logger_prefix}Command TO READ CONFIG ANEW received! SOLVED LOCALLY!")
            importlib.reload(config)
            return ["RE", "Reading config anew!", ""]

        if cmd.upper() == 'SLEEP' or cmd.upper() == 'SILENCE':
            self.logger.info(f"{self.logger_prefix}Command SLEEP/SILENCE received!")
            return ['cmd', 'SLEEP', "I'll go and relax for now! Be back later! <3"]

        if cmd.upper() == 'WAKEUP' or cmd.upper() == 'AWAKE':
            self.logger.info(f"{self.logger_prefix}Command WAKEUP received!")
            return ['cmd', "WAKEUP", "Ah! I'm back again. Missed me? :D"]
        
        if cmd.upper() == 'REPEAT':
            self.logger.info(f"{self.logger_prefix}Command REPEAT received!")
            return ['cmd', "RESEND_MESSAGE"]

        if cmd.upper() == 'ALBOTREST' or cmd.upper() == 'SHUTDOWN' or cmd.upper() == 'QUIT':
            self.logger.info(f"{self.logger_prefix}Command ALBOTREST/SHUTDOWN/QUIT received!")
            return ['cmd', "QUIT", "See you later everybody! Bye-bye! <3"]


        self.logger.info(f"{current_log_prefix}Not a ADVANCED command!")
        return ["", "", ""]

    def check_valid_commands(self, sender, cmd):
        current_log_prefix = self.logger_prefix + "check_valid_commands:"

        #check other type of commands as well..
        response = self.advanced_commands(sender, cmd)
        
        #Not a known command
        if response[0] == "":
            self.logger.info(f"{self.logger_prefix}No response to give!")
            return ["", "", ""]
        else:
            self.logger.info(f"{self.logger_prefix}Your order is my command! Let it happen!")
            return response

    def read_commands(self):
        current_log_prefix = self.logger_prefix +"read_commands:"
        pass

    #Don't want to restart albot for every new command added to the file - right?
    def reread_commands(self):
        pass



    #For games or something maybe - adding their instructions here.
    def add_valid_commands(self, dictionary_to_be_added):
        #Careful not to overwrite existing commands!
        pass

# def is_safe_message(message, user_id):
#     # Length check
#     if len(message) > 500:
#         logger.warning(f"Message from {user_id} rejected: too long ({len(message)} chars)")
#         return False
        
#     # Check for command rate limiting (implementation depends on how you track users)
#     # if is_user_rate_limited(user_id):
#     #     logger.warning(f"Message from {user_id} rejected: rate limited")
#     #     return False
    
#     # Add other checks as needed
    
#     return True


# #If a command is safe and can be considered as a command
# def command_handler(msg):
#     print(f"In command handler, recieved:{msg}")





# def is_safe_command(command_text):
#     # Define explicitly what characters are allowed
#     allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_+- øæåÆØÅ')
    
#     # Check each character in the command
#     disallowed_found = []
#     for char in command_text:
#         if char not in allowed_chars:
#             disallowed_found.append(char)
    
#     # If we found any disallowed characters
#     if disallowed_found:
#         disallowed_str = ', '.join([f"'{c}'" for c in set(disallowed_found)])
#         logger.info(f"Command rejected. Disallowed characters found: {disallowed_str} in: {command_text}")
#         return False
    
#     return True  