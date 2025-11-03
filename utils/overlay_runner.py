import asyncio
import utils.overlay_bridge


class Overlay_runner:

    def __init__(self, logger):
        self.logger = logger
        self.logger_prefix =  "utils/overlay_runner.Overlay_runner=>"

        self.run_loop   = True
        self.queue      = []

        self.cmd_handler    = ""  # For å kunne ...?
        self.overlay_bridge = ""  # For å kunne sende signaler for å kjøre async med PySide6-app
        self.gif_handler    = ""  # For å hente gifs og info om gifs
        self.overlay        = ""  # Trenger å vite når over er klar til å vise mer tekst/gif

        self.isAwake = True

        self.use_this_halloween_gif = ""

        self.logger.info(f"{self.logger_prefix}Command_central successfully initialized!")


    #This is the place the commands will be executed - har vi behov for denne?
    def set_command_handler(self, cmd_handler):
        self.cmd_handler = cmd_handler

    def set_overlay_bridge(self, ob):
        self.overlay_bridge = ob

    def set_gif_handler(self, gif_handler):
        self.gif_handler = gif_handler

    def set_overlay(self, overlay):
        self.overlay = overlay


    async def run_gif_setup(self):
        current_log_prefix = self.logger_prefix + "run_gif_setup:"
        self.logger.info(f"{current_log_prefix}Running GIF-setup.")
        await self.gif_handler.arrange_gifs()
        self.gif_handler.print_all()

    async def setAwake_status(self, bool_val):
        current_log_prefix = self.logger_prefix + "setAwake_status:"
        self.logger.info(f"{current_log_prefix}Setting new Awake status: {bool_val}")

        #Anitmate this for albot to show it's going to sleep/awake
        if bool_val:
            await self.run_visual_command({"text":"Getting back up again!","gif":"MOOSE_AWAKE","sound":""})
            #,"gif":"MOON_CAKE_CHAOS","sound":"Alarm01.wav"})
        else:
            await self.interrupt_run_visual_command({"text":"Going to sleep!","gif":"MOOSE_GO_SLEEP","sound":""})
            #self.run_visual_command({"text":"Getting up!","gif":"MOON_CAKE_CHAOS","sound":"Alarm01.wav"})

        current_log_prefix = self.logger_prefix + "setAwake_status:"
        self.logger.info(f"{current_log_prefix}Awake-status set to: {self.isAwake}")
        self.isAwake = bool_val

    #Hva er cmd her? username:cmd?
    def set_in_queue(self, cmd):
        current_log_prefix = self.logger_prefix + "set_in_queue:"
        self.logger.info(f"{current_log_prefix}Added another visual command")

        command_built = self.build_command(cmd)

        if command_built:
            self.logger.info(f"{current_log_prefix}Command added to queue:{command_built}")
            self.queue.append(command_built)
        else:
            self.logger.info(f"{current_log_prefix}Resultet in no commands!! {cmd}")

    async def make_thank_you_message(self, username):
        await self.set_in_queue({"text":"Thank you!!","gif":"THANK_YOU_FOR_SUPPORT","sound":""})

    async def make_halloween_message(self, gif_to_show):
        current_log_prefix = self.logger_prefix + "make_halloween_message:"
        self.logger.info(f"{current_log_prefix}Added another visual command - Halloween!")

        self.use_this_halloween_gif = gif_to_show

        print(f"\n\n\n\tHalloween: {gif_to_show}\n\n\n")

        # await self.set_in_queue({"text":"BOOOH!!","gif":gif_to_show,"sound":"PLAY_THIS_Halloween_sound.wav"})
#        await self.set_in_queue({"text":"BOOOH!!","gif":gif_to_show,"sound":"PLAY_THIS_Halloween_sound.wav"})
        self.set_in_queue(f"BOOOH!!:HALLOWEEN")


    #From recipes figure out what gifs to use, what sounds to use and what text to show and so on.
    #the end result should be thrown as trash or put in queue on this format:
    #"text='text_goes_here';gif_path="./overlay_media/gifs/MOON_CAKE_CHAOS.gif;sound_path='./overlay_media/sounds/Alarm01'"
    #or even better like a dictionary or list
    #["text_to_be_shown","./overlay_media/gifs/MOON_CAKE_CHAOS.gif", './overlay_media/sounds/Alarm01']
    #{"text":"text_to_be_shown", "gif":./overlay_media/gif/"", "sound":"./overlay_media/sounds/.."}

    #Input parameter på foramt cmd = username:cmd
    def build_command(self, cmd):
        current_log_prefix = self.logger_prefix + "build_command:"
        self.logger.info(f"{current_log_prefix}Incomming params: {cmd}")

        username, cmd = cmd.split(':', 1)

        self.logger.info(f"{current_log_prefix}params split into username:{username}-and-cmd:{cmd}")

        if cmd.upper() == "THANK YOU":
            return {"text":f"Thank you, {username}! <3","gif":"THANK_YOU_FOR_SUPPORT","sound":""}
        
        elif cmd.upper() == "GREETINGS":
            self.logger.info(f"{current_log_prefix}It's a greetings command!")

            #Get back this => f"{gif_to_show};{sound_to_play}" or just ""
            sub_greetings_info  = self.gif_handler.get_sub_gif_greetings(username)

            self.logger.info(f"{current_log_prefix}It's a greetings command! For {username} we got {sub_greetings_info}")


            if sub_greetings_info:
                gif_to_show, sound_to_play = sub_greetings_info.split(':')
                self.logger.info(f"{current_log_prefix}It's a greetings command!")
                return {"text":f"How are you, {username}?","gif":gif_to_show,"sound":sound_to_play}
            return ""
        #Already finished made for putting it in the queue!
        elif cmd.startswith('{'):

            cmd = eval(cmd)
            self.logger.info(f"{current_log_prefix}It's already on the right format: {cmd}")
            return cmd

        elif cmd.upper() == "ALBOTSTARTUP":
            return {"text":"Albot up and running!","gif":"MOOSE_WAVE_HI","sound":""}

        elif cmd.upper() == "HALLOWEEN":
            print("\n\n\n\tHALLLOOOOOWWWEEEEEEEN!\n\n\n\n")
            return {"text":"BOOH!!","gif":self.use_this_halloween_gif,"sound":"PLAY_THIS_Halloween_sound.wav"}

    #For immidiate commands - like Sleep
    async def interrupt_run_visual_command(self, cmd_dict):
        current_log_prefix = self.logger_prefix + "interrupt_run_visual_command:"
        self.logger.info(f"{current_log_prefix}Received interrupting command to run: {cmd_dict}")

        if not self.overlay.ready_to_show_more():
                    self.logger.info(f"{current_log_prefix}Interrupting current overlay show! Busy? {not self.overlay.ready_to_show_more()}")

                    self.overlay.stop_sound()
                    text_to_show    = "INTERRUPTING!"
                    gif_to_show     = self.gif_handler.get_gif_path('TV_NOISE')
                    # gif_length      = self.gif_handler.get_gif_duration('TV_NOISE') #+ 2000
                    gif_length      = 1000
                    sound_to_play   = ""
                    self.overlay_bridge.play_message(text_to_show = text_to_show, gif_to_show = gif_to_show, sound_to_play = sound_to_play, duration=gif_length)


        await asyncio.sleep(1)
        self.logger.info(f"{current_log_prefix}Not interrupting anymore, let's play {cmd_dict}")
        await self.run_visual_command(cmd_dict)


    async def run_visual_command(self, cmd_dict):
        current_log_prefix = self.logger_prefix + "run_visual_command:"
        self.logger.info(f"{current_log_prefix}Received command to run: {cmd_dict}")


        self.logger.info(f"{current_log_prefix}input param: cmd_dict is of type {type(cmd_dict).__name__}")


        # username = ""

        #If theres is a : , there will be a username connected to the command. Like a "Thank you, CoolingenWasTaken!"
        # if ':' in cmd:
        #     username, cmd = cmd.split(':')

        text_to_show    = cmd_dict['text']
        self.logger.info(f"{current_log_prefix}Text ok: {text_to_show}")


        gif_to_show     = self.gif_handler.get_gif_path(cmd_dict['gif'])

        self.logger.info(f"{current_log_prefix}Gif found: {gif_to_show}")



        gif_length = 0

        if "duration" in cmd_dict.keys():
            gif_length = cmd_dict['duration']
        else:
            gif_length      = self.gif_handler.get_gif_duration(cmd_dict['gif']) #+ 2000


        sound_to_play   = cmd_dict['sound']

        print(f"Sound to play: {sound_to_play}")


        if gif_length < 3000:
            gif_length = 3000



        self.logger.info(f"{current_log_prefix}Text to show: {text_to_show}")
        self.logger.info(f"{current_log_prefix}Gif to show: {gif_to_show}")
        self.logger.info(f"{current_log_prefix}Gif duration set to: {gif_length}")
        self.logger.info(f"{current_log_prefix}Sound to play: {sound_to_play}")

        self.overlay_bridge.play_message(text_to_show = text_to_show, gif_to_show = gif_to_show, sound_to_play = sound_to_play, duration=gif_length)


    async def run_commands_from_queue(self):
        current_log_prefix = self.logger_prefix + "run_commands_from_queue:"
        self.logger.info(f"{current_log_prefix}Starting up the while loop..")

        while self.run_loop:

            #Dersom det er noe i køa, så må vi være våkne for å utføre de
            if self.isAwake and self.overlay.ready_to_show_more():
                # self.logger.info(f"{current_log_prefix}Awake:{self.isAwake} and ready_to_show_more:{self.overlay.ready_to_show_more()}")

                #Hvis det er noe i køen
                if self.queue:

                    cur_cmd_obj = self.queue.pop(0)  #If works bad, check out from collections import deque

                    self.logger.info(f"{current_log_prefix}Found a command to be run:{cur_cmd_obj}")

                    await self.run_visual_command(cur_cmd_obj)



                #TRENGER EN FORM FOR COOL DOWN? Eller venting
                    # if cur_cmd_obj.cmd_type == 'SO':

                    #     if self.so_cooldown == 0:
                    #         await self.run_visual_command(cur_cmd_obj)
                    #         self.logger.info(f"{self.logger_prefix}Activating 60 seconds of SO-cooldown")
                    #         self.so_cooldown = 60
                    #     else:
                    #         self.set_in_queue_normal_priority(cur_cmd_obj)

                    #  else:
                    #     await self.run_visual_command(cur_cmd_obj)



            #Alltid sove litt etter godt stykke arbeid utførst ;)
            await asyncio.sleep(1)


            # if self.so_cooldown > 0:
            #     self.so_cooldown -= 1
                # self.logger.info(f"{self.logger_prefix}Current cooldown at: {self.so_cooldown}")






        # current_log_prefix = self.logger_prefix + "handle_overlay_commands:"

        # self.logger.info(f"{current_log_prefix}Received sender:{username} and overview_cmd:{cmd}")
        # self.logger.info(f"{current_log_prefix}Commando read:/{cmd}/")


        # self.overlay_bridge.show_full_greeting(streamer_name=username, 
        #                                                    greeting_text=f'Howdy,{username}', 
        #                                                    gif_path="./overlay_media/gifs/MOON_CAKE_CHAOS.gif", 
        #                                                    sound_path="./overlay_media/sounds/Alarm01.wav")


#OLD FUNCTIONALITY WE MIGHT STILL WANT TO HAVE

# MUST FIX!!!
        # self.overlay_bridge.show_full_greeting(streamer_name=sender, 
        #                                                    greeting_text=f'Howdy,{username}', 
        #                                                    gif_path="./overlay_media/gifs/MOON_CAKE_CHAOS.gif", 
        #                                                    sound_path="./overlay_media/sounds/Alarm01.wav")

        # if overview_cmd.upper().startswith('OVERLAY '):

        #     self.logger.info(f"{current_log_prefix}It's an overlay!")

        #     parts = overview_cmd.split(' ', 2)  # Split into 3 parts: 'OVERLAY', action, [params]

        #     if len(parts) >= 2:
        #         action = parts[1].upper()

        #         self.logger.info(f"{current_log_prefix}-len >= 2: True and action understood as:/{action}/")



        #         if action.upper() == 'MESSAGE' and len(parts) >= 3:
        #             self.overlay_bridge.show_message(' '.join(parts[2:]))
        #         elif action.upper() == 'SOUND':
        #             self.overlay_bridge.play_sound("./overlay_media/sounds/Alarm01.wav")
        #         elif action.upper() == 'GIF':
        #             self.overlay_bridge.show_gif("./overlay_media/gifs/MOON_CAKE_CHAOS.gif")
        #         elif action.upper() == 'GREETINGS':
        #             self.overlay_bridge.show_full_greeting(streamer_name=sender, 
        #                                                    greeting_text=f'Howdy,{sender}', 
        #                                                    gif_path="./overlay_media/gifs/MOON_CAKE_CHAOS.gif", 
        #                                                    sound_path="./overlay_media/sounds/Alarm01.wav")
        #         elif action.upper() == 'HIDE':
        #             self.overlay_bridge.hide_overlay()
            
        #         # Animation commands
        #         elif action.upper() == 'ANIMATE' and len(parts) >= 3:
        #             anim_parts = parts[2].split(' ', 1)
        #             anim_type = anim_parts[0].lower()
                    
        #             # Get message if provided, otherwise use default
        #             message = anim_parts[1] if len(anim_parts) > 1 else f"Animation by {sender}!"
                    
        #             # Show message with the specified animation
        #             self.overlay_bridge.show_message(message, run_alone=True)
        #             self.overlay_bridge.animate_message(anim_type)

        #         # Combined fade-in/fade-out animation - show a message that fades in, stays visible, then fades out
        #         elif action == 'FADE' and len(parts) >= 3:
        #             message = parts[2]
        #             self.logger.info(f"{current_log_prefix}Combined fade animation with message: {message}")
                    
        #             # Show message with initially zero opacity
        #             self.overlay_bridge.show_message(message, run_alone=True)
                    
        #             # Start the combined fade animation - default 6000ms total (2000ms fade-in, 2000ms display, 2000ms fade-out)
        #             self.overlay_bridge.animate_message("fade")



        #         # Specific animation shortcuts
        #         elif action.upper() in ['BOUNCE', 'SPIN', 'ROLL', 'SHAKE', 'WAVE', 'PULSE'] and len(parts) >= 3:
        #             self.logger.info(f"{current_log_prefix}Action recognized as animation action:{action.upper()}")
        #             # First show the message
        #             self.overlay_bridge.show_message(parts[2], run_alone=True)
        #             # Then animate it
        #             self.overlay_bridge.animate_message(action.lower())

