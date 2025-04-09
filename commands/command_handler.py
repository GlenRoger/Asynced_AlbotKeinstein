#Checking if we really got a valid command by a user who is allowed to use it
import importlib
import config


class Albot_Command:

    def __init__(self, cmd_calling, cmd_type, allowed_users_list, response):
        self.cmd_calling        = cmd_calling
        self.cmd_type           = cmd_type
        self.allowed_users_list = allowed_users_list
        self.response           = response





class Command_central:


    def __init__(self, logger):
        self.logger_prefix = "commands/command_handler.Command_central=>"
        self.logger = logger

        self.logger.info(f"{self.logger_prefix}Command_central successfully initialized!")


        self.command_files_path = "./commands/command_files/"
        self.advanced_cmd_file    = "Advanced_commands.csv"
        self.normal_cmd_file    = "Normal_commands.csv"

        self.command_files = [self.normal_cmd_file, self.advanced_cmd_file]

        self.all_commands = {}


        self.read_commands_from_files()


    def collect_commands(self):
        pass
        

    #ADD ADVANCED COMMANDS HERE AND ADD THEM TO THE COLLECT_COMMANDS MANUALLY
    #These can also be saved in a file, though need extra programming in TwitchConnection.py
    def advanced_commands(self, sender, cmd):
        current_log_prefix = self.logger_prefix + "advanced_commands:"
        self.logger.info(f"{self.logger_prefix}Got {cmd} from {sender}")

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

        if cmd.upper() == 'HOWDY' or cmd.upper() == 'HOWDY!':
            return ["RE", "AHOY!", ""]

        self.logger.info(f"{current_log_prefix}Not an ADVANCED command!")
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
    

    def rate_priority_commands(self, cmd):
        current_log_prefix = self.logger_prefix +"rate_priority_commands:"
        self.logger.info(f"{self.logger_prefix}Rating /{cmd}/")

        if cmd.upper() in ("SLEEP", "SILENCE", "WAKEUP", "AWAKE", "REPEAT", "ALBOTREST", "SHUTDOWN", "QUIT"):
            return "high"
        else:
            return "normal"



    def read_commands_from_files(self):
        current_log_prefix = self.logger_prefix +"read_commands_from_files:"

        for file in self.command_files:

            self.logger.info(f"{self.logger_prefix}Reading {self.command_files_path}{file}")

            with open (f"{self.command_files_path}{file}", 'r', encoding='utf-8') as fopen:
                for line in fopen:

                    if line[0] == '#':
                        continue

                    cmd_line = line.rstrip()

                    line_list = cmd_line.split(';')

                    if len(line_list) != 4:
                        self.logger.info(f"{self.logger_prefix}Not correct amount of elements. 4 required got  {len(line_list)}")
                        continue

                    cmd_callings    = line_list[0].split(',')
                    cmd_type        = line_list[1]
                    cmd_users       = line_list[2].split(',')
                    cmd_response    = line_list[3][1:-1]  #Fjerner første og siste "-tegn

                    for cmd_call in cmd_callings:
                        new_cmd = Albot_Command(cmd_call, cmd_type, cmd_users, cmd_response)
                        self.all_commands[cmd_call.upper()] = new_cmd

                        self.logger.info(f"{self.logger_prefix}New command added:{new_cmd}") 


    def check_sender_is_allowed_to_use_this_command(self, sender, lists_to_check):
        current_log_prefix = self.logger_prefix +"check_sender_is_allowed_to_use_this_command:"
        self.logger.info(f"{self.logger_prefix}Have to check if {sender} is in one of these lists:{lists_to_check}") 

        pass



    def get_command_instructions(self, sender, cmd_call):
        current_log_prefix = self.logger_prefix +"get_command_instructions:"
        self.logger.info(f"{self.logger_prefix}Got that {sender} sent:{cmd_call}") 

        cmd_call = cmd_call.upper()

        if cmd_call in self.all_commands.keys():

            cmd_obj = self.all_commands[cmd_call.upper()]

            #DETTE MÅ ENDRES!!!!!!!!!!! mÅ SJEKK MOT LISTENE I CONFIG.PY!
            if sender not in cmd_obj.allowed_users_list:
                self.logger.info(f"{self.logger_prefix}{sender} is allowed to use command:{cmd_call}")
                return cmd_obj
            else:
                self.logger.info(f"{self.logger_prefix}{sender} is NOT allowed to use command:{cmd_call}")
        else:
            self.logger.info(f"{self.logger_prefix}Could not find call: {cmd_call}") 


        #             print(line)



        # print(self.all_commands)
        # print(self.all_commands['SLEEP'])
        # print(self.all_commands['SLEEP'].cmd_calling)
        # print(self.all_commands['SLEEP'].cmd_type)
        # print(self.all_commands['SLEEP'].allowed_users_list)
        # print(self.all_commands['SLEEP'].response)




#all_commands



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