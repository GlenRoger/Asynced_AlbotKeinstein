#Checking if we really got a valid command by a user who is allowed to use it
import importlib
import config
import asyncio
import random


class Albot_Command:

    def __init__(self, cmd_calling, cmd_type, privileges_to_run, response, priority='Normal', params = "", sender = ""):
        self.cmd_calling        = cmd_calling
        self.cmd_type           = cmd_type
        self.params             = params
        self.privileges_to_run  = privileges_to_run
        self.response           = response
        self.priority           = priority
        self.sender             = sender

    #What is the commands name we can call it by (like "HOWDY")
    def get_cmd_calling(self):
        return self.cmd_calling
    
    #Either CMD for command or RE for replay, SO for shout out
    def get_cmd_type(self):
        return self.cmd_type
    
    def get_params(self):
        return self.params

    #List over roles that is needed to use this
    def get_privileges_to_run(self):
        return self.privileges_to_run
    
    def get_response(self):
        return self.response

    def get_priority(self):
        return self.priority

    def get_sender(self):
        return self.sender

class Command_central:

    def __init__(self, logger):
        self.logger_prefix = "commands/command_handler.Command_central=>"
        self.logger = logger

        self.isAwake            = True

        #For shutdown
        self.albot_brain = ""

        #For sjekk av privilegier rundt hvilke kommandoer kan kjøres
        self.usermanagement = ""

        self.msg_central    = ""
        self.cmd_runner     = ""
        self.overlay_runner = ""
        self.gif_handler    = ""
        

        self.command_files_path = "./commands/command_files/"
        self.advanced_cmd_file    = "Advanced_commands.csv"
        self.normal_cmd_file    = "Normal_commands.csv"

        self.command_files = [self.normal_cmd_file, self.advanced_cmd_file]

        self.all_commands = {}

        self.gotten_auto_shout_outs = []
        self.gotten_auto_thanks     = []
        self.gotten_auto_greetings  = []

        #%halloween on/off - bakgrunnsoppgaven som viser halloween-gifs, None når av
        self.halloween_gifs_task = None

        self.read_commands_from_files()

        self.logger.info(f"{self.logger_prefix}Command_central successfully initialized!")


    #To be able to shut down the program completely
    def set_albot_brain(self, albot_brain):
        """Set reference to AlbotBrain for shutdown purposes"""
        self.albot_brain = albot_brain

    #For å sjekke privilegier rundt hvilke kommandoer du kan kjøre
    def set_user_manager(self, um):
        self.usermanagement = um

    #Kun til bruk ved shutdown - som kjøres med en gang
    def set_msg_central(self, mc):
        self.msg_central = mc

    def set_cmd_runner(self, cmd_runner):
        self.cmd_runner = cmd_runner

    def set_overlay_runner(self, overlay_runner):
        self.overlay_runner = overlay_runner

    def set_gifhandler(self, gif_handler):
        self.gif_handler = gif_handler


    async def check_auto_greetings(self, username):

        current_log_prefix = self.logger_prefix + "check_auto_greetings:"
        self.logger.info(f"{current_log_prefix}Auto-greetings for /{username}/ if they don't have default gif.")

        #Do the auto-greetings for everybody
        # if not self.usermanagement.is_Subscriber(username):
        #     return

        if username in self.gotten_auto_greetings:
            return
        
        # if username in config.TSTWTMEMBERS:
        #     return


        self.gotten_auto_greetings.append(username)

        if self.gif_handler.got_default_gif(username):
            return

        self.overlay_runner.set_in_queue(f"{username}:GREETINGS")

        #Just for my own example to look at. Delete later.
        # self.overlay_runner.set_in_queue(f"{username}:Thank you")



    async def check_auto_thanks_for_subscribers(self, username):

        if not self.usermanagement.is_Subscriber(username):
            return

        if username in self.gotten_auto_thanks:
            return
        
        # if username in config.TSTWTMEMBERS:
        #     return


        self.gotten_auto_thanks.append(username)

        self.overlay_runner.set_in_queue(f"{username}:Thank you")


    #is_auto_so is boolean = True if automatic shout out is given, False if done by user-command
    async def create_auto_shout_out(self, username, is_auto_so=False):
        current_log_prefix = self.logger_prefix + "create_auto_shout_out:"
        self.logger.info(f"{current_log_prefix}Try to create shout out for /{username}/")

        #Check if we can give automatic so and if hasn't been done earlier this stream
        if is_auto_so:
            if username.lower() in self.gotten_auto_shout_outs:
                return
            
            if username.lower() not in config.AUTOMATIC_SHOUTOUT_LIST:
                return

        message = ""

        current_log_prefix = self.logger_prefix + "create_custom_shoutout:"
        
        try:

            messsage = ""

            # Get what the streamer was last playing
            game_name = await self.usermanagement.get_streamer_last_game(username)
            
            # Craft message based on available info
            if game_name:
                message = f"Check out {username} at https://twitch.tv/{username} - they were last playing {game_name}!"
            else:
                message = f"Check out {username} at https://twitch.tv/{username} - they're an awesome streamer!"
            
            self.shout_out_queue.append(message)

            self.logger.info(f"{current_log_prefix}Adding shoutout for {username} to so-queue")
            
        except Exception as e:
            self.logger.error(f"{current_log_prefix}Failed to send enhanced shoutout: {e}")


        #Alright Buildin shout-out-command for user here
        cmd_call        = "SO"
        cmd_type        = "SO"
        cmd_users       = ["TSTWTMEMBERS", "MODS"]
        cmd_response    = message
        priority        = "Normal"
        cmd_obj = Albot_Command(cmd_call, cmd_type, cmd_users, cmd_response, priority)

        self.cmd_runner.set_in_queue_normal_priority(cmd_obj)

        self.gotten_auto_shout_outs.append(username.lower())



    async def run_if_instant_commands(self, sender, cmd, params):
        current_log_prefix = self.logger_prefix + "run_if_instant_commands:"
        self.logger.info(f"{current_log_prefix}Checking if it is a 'instant' command: /{cmd}/")


        #COMMANDS TO BE RUN IMMIDIATELY
        if (cmd.upper() == 'ALBOTREST' or cmd.upper() == 'SHUTDOWN' or cmd.upper() == 'QUIT'):
            if self.check_user_match_privileges_to_run_command(sender, ["TSTWTMEMBERS"]):
                await self.albot_brain.shutdown()
            else:
                self.logger.info(f"{current_log_prefix}User:{sender} doesn't have necessary role (TSTWTMEMBERS) to run this command:/{cmd}/")
            return True


        elif (cmd.upper() == 'SLEEP' or cmd.upper() == 'SILENCE') and self.check_user_match_privileges_to_run_command(sender, ["MODS", "TSTWTMEMBERS"]):

            if self.isAwake:
                await self.overlay_runner.setAwake_status(False)
                self.isAwake = False
                self.cmd_runner.setAwake_status = self.isAwake
                self.logger.info(f"{current_log_prefix}Command SLEEP/SILENCE received!")
                await self.msg_central.albot_to_say("command_central.check_command", "I'll go and relax for now! Be back later! <3")
                
            else:
                self.isAwake = False
                self.cmd_runner.setAwake_status = self.isAwake
                self.logger.info(f"{current_log_prefix}Command SLEEP/SILENCE received.. but is already sleeping")
            return True


        elif (cmd.upper() == 'WAKEUP' or cmd.upper() == 'AWAKE') and self.check_user_match_privileges_to_run_command(sender, ["MODS", "TSTWTMEMBERS"]):
            if not self.isAwake:
                await self.overlay_runner.setAwake_status(True)
                self.logger.info(f"{current_log_prefix}Command WAKEUP received!")
                self.isAwake = True
                self.cmd_runner.setAwake_status = self.isAwake
                await self.msg_central.albot_to_say("command_central.check_command", "Ah! I'm back again. Missed me? :D")
            else:
                self.isAwake = True
                self.cmd_runner.setAwake_status = self.isAwake
                await self.msg_central.albot_to_say("command_central.check_command", "I'm not asleep - you're asleep! xD")
            return True
                

        elif cmd.upper() == 'HALLOWEEN':
            if self.check_user_match_privileges_to_run_command(sender, ["MODS", "TSTWTMEMBERS"]):
                await self.halloween_command(sender, params)
            else:
                self.logger.info(f"{current_log_prefix}User:{sender} doesn't have necessary role (MODS, TSTWTMEMBERS) to run this command:/{cmd}/")
            return True


        elif cmd.upper() == 'SO':
            if self.check_user_match_privileges_to_run_command(sender, ["MODS", "TSTWTMEMBERS"]):
                await self.create_auto_shout_out(params, is_auto_so = False)
            else:
                self.logger.info(f"{self.logger_prefix}Does not have the right privileges to run the SO-command..")
            return True
        return False

    #%halloween on, %halloween off, %halloween (status)
    async def halloween_command(self, sender, params):
        current_log_prefix = self.logger_prefix + "halloween_command:"

        option = params.strip().lower() if params else ""
        is_on = self.halloween_gifs_task is not None

        if option == "on":
            if is_on:
                await self.msg_central.albot_to_say("command_central.halloween_command", "Halloween mode is already on! 👻")
                return

            self.logger.info(f"{current_log_prefix}Halloween gifs turned ON by {sender}")
            self.halloween_gifs_task = asyncio.create_task(self.halloween_gifs_loop())
            self.save_halloween_status()

            if self.isAwake:
                await self.msg_central.albot_to_say("command_central.halloween_command", "Spooky season activated! 🎃 Watch out...")
            else:
                await self.msg_central.albot_to_say("command_central.halloween_command", "Halloween mode is on! 🎃 The scares start when I wake up...")

        elif option == "off":
            if not is_on:
                await self.msg_central.albot_to_say("command_central.halloween_command", "Halloween mode is already off.")
                return

            self.logger.info(f"{current_log_prefix}Halloween gifs turned OFF by {sender}")
            self.halloween_gifs_task.cancel()
            self.halloween_gifs_task = None
            self.save_halloween_status()
            await self.msg_central.albot_to_say("command_central.halloween_command", "Halloween mode off. No more scares... for now! 👻")

        else:
            status = "ON 🎃" if is_on else "OFF"
            await self.msg_central.albot_to_say("command_central.halloween_command", f"Halloween mode is {status}. Use {config.PREFIX_FOR_BOT_TO_READ}halloween on / {config.PREFIX_FOR_BOT_TO_READ}halloween off")


    #Fra dashboardet - skrur av/på lyden til halloween-gifene, ingen melding i chatten
    def set_halloween_sound(self, sound_on, sender):
        current_log_prefix = self.logger_prefix + "set_halloween_sound:"
        self.logger.info(f"{current_log_prefix}Halloween sound turned {'ON' if sound_on else 'OFF'} by {sender}")

        self.overlay_runner.halloween_sound_on = sound_on
        self.save_halloween_status()


    #Lagrer halloween-innstillingene i databasen, så dashboardet kan vise dem
    def save_halloween_status(self):
        current_log_prefix = self.logger_prefix + "save_halloween_status:"

        try:
            self.albot_brain.db.set_status("HALLOWEEN_MODE", "ON" if self.halloween_gifs_task else "OFF")
            self.albot_brain.db.set_status("HALLOWEEN_SOUND", "ON" if self.overlay_runner.halloween_sound_on else "OFF")
        except Exception as e:
            self.logger.error(f"{current_log_prefix}Could not save halloween status to the database -> /{e}/")


    #Viser en tilfeldig halloween-gif med en gang, og deretter hvert 5. til 10. minutt
    async def halloween_gifs_loop(self):
        current_log_prefix = self.logger_prefix + "halloween_gifs_loop:"

        while True:
            #Når Albot sover skal det ikke legges gifs i køen, ellers spilles alle av på rad når han våkner
            if self.isAwake:
                await self.show_halloween_gif()

            await asyncio.sleep(random.randint(5*60, 10*60))


    #Fra dashboardets spøkelse-knapp - én halloween-gif med en gang, uavhengig av halloween-modus
    async def fire_halloween_gif(self, sender):
        current_log_prefix = self.logger_prefix + "fire_halloween_gif:"

        if not self.isAwake:
            self.logger.info(f"{current_log_prefix}Albot is asleep - not showing the halloween gif {sender} asked for")
            return

        self.logger.info(f"{current_log_prefix}Halloween gif fired by {sender}")
        await self.show_halloween_gif()


    async def show_halloween_gif(self):
        current_log_prefix = self.logger_prefix + "show_halloween_gif:"

        try:
            gif_to_show = self.gif_handler.get_random_halloween_list()
            await self.overlay_runner.make_halloween_message(gif_to_show)
        except IndexError:
            self.logger.warning(f"{current_log_prefix}No halloween gifs found - add gifs named LIST_HALLOWEEN_... to known_gifs.csv")


    async def check_command(self, sender, cmd, params):
        current_log_prefix = self.logger_prefix + "check_command:"
        self.logger.info(f"{current_log_prefix}Time to check if this a valid command: /{cmd}/ also getting param /{params}/")


        if cmd.upper() in self.all_commands.keys():

            #Visual commands are handled elsewhere
            if self.all_commands[cmd.upper()].get_cmd_type() == "OVERLAY":

                if sender == 'thestreamteamwastaken' and cmd.upper() == 'GREETINGS' and params != "" and params.upper() == 'PHEXTHEFLEX':
                    self.logger.info(f"{current_log_prefix}Passing command {cmd} to Overlay-runner (set_in_queue_tstwt_msg)")
                    self.overlay_runner.set_in_queue_tstwt_msg(params)
                    return


                self.logger.info(f"{current_log_prefix}Passing command {cmd} to Overlay-runner")
                self.overlay_runner.set_in_queue(f"{sender}:{cmd}")
                return

            if await self.run_if_instant_commands(sender, cmd, params):
                return

             #Other commands that isn't so urgent to be run
            self.logger.info(f"{current_log_prefix}Command found!")
            cmd_obj = self.all_commands[cmd.upper()]

            if self.check_user_match_privileges_to_run_command(sender, cmd_obj.get_privileges_to_run()):

                if cmd_obj.get_cmd_type() == 'ADVANCED':
                    cmd_obj.params = params
                    cmd_obj.sender = sender
 
                if cmd_obj.priority == 'HIGH':
                    self.cmd_runner.set_in_queue_high_priority(cmd_obj)
                else:
                    self.cmd_runner.set_in_queue_normal_priority(cmd_obj)

            else:
                self.logger.info(f"{self.logger_prefix}Does not have the right privileges to run command..")
        else:
             self.logger.info(f"{self.logger_prefix}Not a known command:{cmd.upper()}")
             print(f"{self.all_commands.keys()}")


    #Sending main_command in this case is the user activating soundalert, params is the soundalert info
    async def soundalert_gif(self, main_command, params):
        current_log_prefix = self.logger_prefix + "soundalert_gif:"
        self.logger.info(f"{current_log_prefix}Can we play:/{params}/ played by /{main_command}/")

        if "gotta catch them all!!" in params.lower():
            random_pokemon_gif = self.gif_handler.get_random_pokemon_bits_list()
            make_dict_not_more = {"text":f"Let's catch them all, {main_command}! <3","gif":random_pokemon_gif,"sound":"",'duration':14000}
            self.overlay_runner.set_in_queue(f"{main_command}:{make_dict_not_more}")

        elif "i seeeeee youuuu!" in params.lower():
            random_scary_i_see_you_gif = self.gif_handler.get_random_scary_i_see_you_bits_list()
            make_dict_not_more = {"text":f"You scared me, {main_command}! <3","gif":random_scary_i_see_you_gif,"sound":"",'duration':5000}
            self.overlay_runner.set_in_queue(f"{main_command}:{make_dict_not_more}")




    #Her kjøres faktik kommandoene, som tidligere har blitt plassert i kø.
    async def run_command(self, cmd_obj):

        current_log_prefix = self.logger_prefix + "run_command:"
        self.logger.info(f"{current_log_prefix}Run command:{cmd_obj.get_cmd_calling()}")

        if cmd_obj.get_cmd_type() == "RE":
            await self.msg_central.albot_to_say("Command_central.run_command", cmd_obj.get_response())
        elif cmd_obj.get_cmd_type() == "SO":
            await self.msg_central.albot_to_say("Command_central.run_command", cmd_obj.get_response())
        elif cmd_obj.get_cmd_calling() == "FOLLOWNUMBER":
            follow_nr = self.usermanagement.get_user_follower_nr(cmd_obj.get_sender())

            if follow_nr != -1:
                msg_back_to_sender = f"Dear @{cmd_obj.get_sender()} you are follower #{follow_nr} <3"
            else:
                msg_back_to_sender = f"Dear @{cmd_obj.get_sender()}.. are you sure you're following us? Maybe I need to refresh my followerlist again ':D"
            await self.msg_central.albot_to_say("Command_central.run_command", msg_back_to_sender)

        elif cmd_obj.get_cmd_calling() == "REFRESH":
            
            updated_list = False

            if cmd_obj.get_params().upper() == 'MODS':
                await self.usermanagement.buildlists('MODS')
                updated_list = True
            elif cmd_obj.get_params().upper() == 'SUBSCRIBERS':
                await self.usermanagement.buildlists('SUBSCRIBERS')
                updated_list = True
            elif cmd_obj.get_params().upper() == 'VIPS':
                await self.usermanagement.buildlists('VIPS')
                updated_list = True
            elif cmd_obj.get_params().upper() == 'FOLLOWERS':
                await self.usermanagement.buildlists('FOLLOWERS')
                updated_list = True
            elif cmd_obj.get_params().upper() == 'CONFIG':
                await self.logger.info(f"{current_log_prefix}REFRESH CONFIG: To be added!! Or do we need it at all?")
                updated_list = False
            elif cmd_obj.get_params().upper() == 'GREETINGS':
                self.gif_handler.build_gif_greetings()
                updated_list = True
            elif cmd_obj.get_params().upper() == 'GIFS':
                await self.gif_handler.arrange_gifs()
                updated_list = True
            else:
                self.logger.info(f"{current_log_prefix}Don't know what to REFRESH? What is {cmd_obj.get_params().upper()}?")
                updated_list = False

            if updated_list:
                await self.msg_central.albot_to_say("Command_central.run_command", f"Done! Refreshed the '{cmd_obj.get_params()}'-list!")
            else:
                await self.msg_central.albot_to_say("Command_central.run_command", f"Could not update.. what is this '{cmd_obj.get_params()}'?")

        else:
            self.logger.info(f"{self.logger_prefix}Command to be made:{cmd_obj.get_cmd_type()}")



    #Checking if list items is in another list.
    def check_user_match_privileges_to_run_command(self, sender, privileges_to_match):

        current_log_prefix = self.logger_prefix + "check_user_match_privileges_to_run_command:"


        if privileges_to_match == [] or "EVERYBODY" in privileges_to_match or "EVERYONE" in privileges_to_match:
            self.logger.info(f"{current_log_prefix}Yes! Run command.. for everybody!")
            return True

        self.logger.info(f"{current_log_prefix}Do sender {sender} have the privileges to run command?")


        user_roles = self.usermanagement.get_all_user_roles(sender)

        self.logger.info(f"{current_log_prefix}Privileges for sender: {sender}, needed: {privileges_to_match}?")


        if any(item in user_roles for item in privileges_to_match):
            self.logger.info(f"{current_log_prefix}Yes! Run command!")
            return True


        self.logger.info(f"{current_log_prefix}No! Don't run command!")
        return False


    #Shutdown-kommandoene kjøres med en gang, andre commandoer som repeat, sleep, osv er høy pri
    #resten er normal pri.
    def get_cmd_priority(self, cmd):
        pass


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

                    if len(line_list) != 5:
                        self.logger.info(f"{self.logger_prefix}Not correct amount of elements. 4 required got {len(line_list)}")
                        continue

                    cmd_callings    = line_list[0].split(',')
                    cmd_type        = line_list[1]
                    cmd_users       = line_list[2].split(',')  #privileges_to_run
                    cmd_response    = line_list[3]  #Fjerner første og siste "-tegn
                    priority        = line_list[4][1:-1]  #Fjerner første og siste "-tegn

                    if cmd_users == "EVERYBODY":
                        cmd_users = ""

                    for cmd_call in cmd_callings:
                        new_cmd = Albot_Command(cmd_call, cmd_type, cmd_users, cmd_response, priority)
                        self.all_commands[cmd_call.upper()] = new_cmd

                        self.logger.info(f"{self.logger_prefix}New command added: calling='{new_cmd.cmd_calling}', type='{new_cmd.cmd_type}', allprivileges_to_run={new_cmd.privileges_to_run}, response='{new_cmd.response}', priority='{priority}")

            print("Done reading commands from file!")
            print(f"{self.all_commands}")


    def get_command_object(self, cmd_call):
        current_log_prefix = self.logger_prefix +"get_command_instructions:"
        self.logger.info(f"{self.logger_prefix}Looking into what the command:{cmd_call} can do.") 

        cmd_call = cmd_call.upper()

        if cmd_call in self.all_commands.keys():
            cmd_obj = self.all_commands[cmd_call.upper()]
            return cmd_obj
        elif cmd_call.upper().startswith('SO '):
            return Albot_Command("SHOUTOUT","RE",["TSTWTMEMBERS", "MODS", "VIPS"], cmd_call)


        self.logger.info(f"{self.logger_prefix}Could not find call: {cmd_call}") 
        return ""

