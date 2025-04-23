#Checking if we really got a valid command by a user who is allowed to use it
import importlib
import config


class Albot_Command:

    def __init__(self, cmd_calling, cmd_type, allowed_users_list, response):
        self.cmd_calling        = cmd_calling
        self.cmd_type           = cmd_type
        self.allowed_users_list = allowed_users_list
        self.response           = response

    def get_cmd_calling(self):
        return self.cmd_calling
    
    def get_cmd_type(self):
        return self.cmd_type

    def get_allowed_users_list(self):
        return self.allowed_users_list

    def get_response(self):
        return self.response
    

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

        # Overlay test commands
        if cmd.upper().startswith('OVERLAY '):
            return ["OVERLAY", "", ""]
            # parts = cmd.split(' ', 2)  # Split into 3 parts: 'OVERLAY', action, [params]
            # if len(parts) >= 2:
            #     action = parts[1].upper()
                
            #     if action == 'MESSAGE' and len(parts) >= 3:
            #         return ["OVERLAY", "MESSAGE", parts[2]]
            #     elif action == 'GREETING' and len(parts) >= 3:
            #         return ["OVERLAY", "GREETING", parts[2]]
            #     elif action == 'HIDE':
            #         return ["OVERLAY", "HIDE", ""]        

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
    

    def is_command(self, cmd):
        current_log_prefix = self.logger_prefix +"is_command:"
        self.logger.info(f"{self.logger_prefix}Does this command exist: /{cmd}/")

        if cmd.upper() in self.all_commands.keys():
            self.logger.info(f"{self.logger_prefix}It does exist!")
            return True
        elif cmd.upper().startswith("SO "):
            self.logger.info(f"{self.logger_prefix}It does exist!")
            return True
        elif cmd.upper().startswith("OVERLAY "):
            self.logger.info(f"{self.logger_prefix}It does exist!")
            return True
        
        self.logger.info(f"{self.logger_prefix}It does NOT exist!")
        return False

    def rate_priority_commands(self, cmd):
        current_log_prefix = self.logger_prefix +"rate_priority_commands:"
        self.logger.info(f"{self.logger_prefix}Rating /{cmd}/")

        if cmd.upper() in ("SLEEP", "SILENCE", "WAKEUP", "AWAKE", "REPEAT", "ALBOTREST", "SHUTDOWN", "QUIT"):
            return "high"
        elif cmd.upper().startswith("SO "):
            return "shoutout"
        elif cmd.upper().startswith("OVERLAY "):
            return "overlay"
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
                        self.logger.info(f"{self.logger_prefix}Not correct amount of elements. 4 required got {len(line_list)}")
                        continue

                    cmd_callings    = line_list[0].split(',')
                    cmd_type        = line_list[1]
                    cmd_users       = line_list[2].split(',')
                    cmd_response    = line_list[3][1:-1]  #Fjerner første og siste "-tegn

                    for cmd_call in cmd_callings:
                        new_cmd = Albot_Command(cmd_call, cmd_type, cmd_users, cmd_response)
                        self.all_commands[cmd_call.upper()] = new_cmd

                        self.logger.info(f"{self.logger_prefix}New command added: calling='{new_cmd.cmd_calling}', type='{new_cmd.cmd_type}', allowed_users={new_cmd.allowed_users_list}, response='{new_cmd.response}'")



    def get_command_object(self, cmd_call):
        current_log_prefix = self.logger_prefix +"get_command_instructions:"
        self.logger.info(f"{self.logger_prefix}Looking into what the command:{cmd_call} can do.") 

        cmd_call = cmd_call.upper()

        if cmd_call in self.all_commands.keys():
            cmd_obj = self.all_commands[cmd_call.upper()]
            return cmd_obj
        elif cmd_call.upper().startswith('SO '):
            return Albot_Command("SHOUTOUT","RE",["STREAMERS", "MODS", "VIPS"], cmd_call)


        self.logger.info(f"{self.logger_prefix}Could not find call: {cmd_call}") 
        return ""

