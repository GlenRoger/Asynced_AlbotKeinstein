import asyncio

class Overlay_runner:

    def __init__(self, logger):
        self.logger = logger
        self.logger_prefix =  "commands/overlay_runner.Overlay_runner=>"

        self.run_loop   = True
        self.queue      = []

        self.cmd_handler = ""

        self.isAwake = True

    #This is the place the commands will be executed
    def set_command_handler(self, cmd_handler):
        self.cmd_handler = cmd_handler


    def setAwake_status(self, bool_val):
        current_log_prefix = self.logger_prefix + "setAwake_status:"
        self.logger.info(f"{self.logger_prefix}Awake-status set to: {self.isAwake}")
        self.isAwake = bool_val

    def set_in_queue(self, cmd):
        current_log_prefix = self.logger_prefix + "set_in_queue:"
        self.logger.info(f"{self.logger_prefix}Added another visual command")
        self.queue.append(cmd)




        current_log_prefix = self.logger_prefix + "handle_overlay_commands:"

        self.logger.info(f"{current_log_prefix}Received sender:{sender} and overview_cmd:{overview_cmd}")
        self.logger.info(f"{current_log_prefix}Commando read:/{overview_cmd.upper()}/")


        if not self.isNotSilenced:
            self.logger.info(f"{current_log_prefix}Couldn't complete.. Albot is sleeping! (status not silenced?:{self.isNotSilenced})/")
            return ""


    def run_visual_command(self, cmd):
        
        username = ""

        #If theres is a : , there will be a username connected to the command. Like a "Thank you, CoolingenWasTaken!"
        if ':' in cmd:
            username, cmd = cmd.split(':')


        self.overlay_bridge.show_full_greeting(streamer_name=sender, 
                                                           greeting_text=f'Howdy,{sender}', 
                                                           gif_path="./overlay_media/gifs/MOON_CAKE_CHAOS.gif", 
                                                           sound_path="./overlay_media/sounds/Alarm01.wav")

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






    async def run_commands_from_queue(self):
        current_log_prefix = self.logger_prefix + "run_commands_from_queue:"
        self.logger.info(f"{self.logger_prefix}Starting up the while loop..")

        while self.run_loop:

            #Dersom det er noe i køa, så må vi være våkne for å utføre de
            if self.isAwake:

                #Hvis det er noe i køen
                if self.queue:

                    self.logger.info(f"{self.logger_prefix}Found a command to be run!")
                    cur_cmd_obj = self.queue.pop(0)  #If works bad, check out from collections import deque

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