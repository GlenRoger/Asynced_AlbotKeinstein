import asyncio

class Command_runner:

    def __init__(self, logger):
        self.logger = logger
        self.logger_prefix =  "commands/command_runner.Command_runner=>"

        self.run_loop   = True
        self.queue      = []

        self.cmd_handler = ""

        self.isAwake = True

        self.so_cooldown = 0

    #This is the place the commands will be executed
    def set_command_handler(self, cmd_handler):
        self.cmd_handler = cmd_handler


    def setAwake_status(self, bool_val):
        current_log_prefix = self.logger_prefix + "setAwake_status:"
        self.logger.info(f"{self.logger_prefix}Awake-status set to: {self.isAwake}")
        self.isAwake = bool_val

    def set_in_queue_normal_priority(self, cmd):
        current_log_prefix = self.logger_prefix + "set_in_queue_normal_priority:"
        self.logger.info(f"{self.logger_prefix}Added a normal priority command")
        self.queue.append(cmd)

    def set_in_queue_high_priority(self, cmd):
        current_log_prefix = self.logger_prefix + "set_in_queue_high_priority:"
        self.logger.info(f"{self.logger_prefix}Added a high priority command")
        self.queue.insert(0, cmd)

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

                    if cur_cmd_obj.cmd_type == 'SO':

                        if self.so_cooldown == 0:
                            await self.cmd_handler.run_command(cur_cmd_obj)
                            self.logger.info(f"{self.logger_prefix}Activating 60 seconds of SO-cooldown")
                            self.so_cooldown = 60
                        else:
                            self.set_in_queue_normal_priority(cur_cmd_obj)

                    else:
                        await self.cmd_handler.run_command(cur_cmd_obj)


            #Alltid sove litt etter godt stykke arbeid utførst ;)
            await asyncio.sleep(1)


            if self.so_cooldown > 0:
                self.so_cooldown -= 1
                # self.logger.info(f"{self.logger_prefix}Current cooldown at: {self.so_cooldown}")
    