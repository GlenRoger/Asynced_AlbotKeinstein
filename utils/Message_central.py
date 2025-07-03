import config
import asyncio


#MELDINGER INN:
#Alt som kommer inn her er chat-meldinger, sjekker om det faktisk er en kommando eller ikke og 
#om det er en trygg kommando - før den går videre kommando-veien. Må også sjekke om det faktisk er en kommando også.

#MELDINGER UT:
#Sjekker også lengden på melding som skal sendes ut, dersom den er over 500 tegn lang, så deles den i mindre biter.

class Message_central:


#NOTHING HERE IS TESTED!
#Message pile must also be checked!


    def __init__(self, logger, max_messages_per_minute=60, cooldown_duration=60):
        self.logger_prefix = "utils/Message_central.Message_central=>"
        self.logger = logger

        self.set_twitchconnector = ""
        self.cmd_handler = ""


    #Må bruke albot_msg_to_chat, den ligger i twitchconnector
    def set_tc(self, tc):
        self.set_twitchconnector = tc

    #Videresender potensielle kommandoer til commando_central
    def set_ch(self, cmd_central):
        self.cmd_handler = cmd_central

    #What comes in here? Typical this:
    #coolingenwastaken!coolingenwastaken@coolingenwastaken.tmi.twitch.tv PRIVMSG #thestreamteamwastaken :hei
    async def check_chat_message(self, message):

        current_log_prefix = self.logger_prefix + "check_chat_message=>"
        self.logger.info(f"{current_log_prefix}Message to check{message}")


        if message.startswith("albotkeinstein"):
            self.logger.info(f"Why are you sending commands to yourself albot?? {message}")
            return

        sender, msg_only, params = self.find_sender_and_msg(message)

        if msg_only == "":
            self.logger.info(f"Rejected from find_sender_and_msg")
            return

        if not self.is_safe_command(msg_only):
            self.logger.info(f"Rejected! Might contain code-injection!")
            return
        
        self.logger.info(f"This could be a valid command!")

        await self.cmd_handler.check_command(sender, msg_only, params)


    #######################################################################
    #################### CHECKING IF MESSAGE CAN BE SENT ##################
    #######################################################################


    #Må utarbeides!
    async def albot_to_say(self, called_by_function, msg):
        await self.set_twitchconnector.albot_msg_to_chat(called_by_function, msg)


    #Check if we're not spamming/in cooldown chat already 
    #Check if the message is more than 500 characters, if so then split it. 
    #Returning a list of messages to be sent - usually with only one item as most messages are shot.

    def check_if_can_be_sent(self, outgoing_chat_msg):
        current_log_prefix = "utils/send_message.check_if_can_be_sent=>"
        self.logger.info(f"{current_log_prefix}Check length of incomming msg:{len(self.outgoing_chat_msg)}")

        #Checking if message is larger than 480 characters, if it is, then split it.
        #After this changed outgoing_chat_msg into a list.
        if len(outgoing_chat_msg) < 485:
            outgoing_chat_msg = self.split_large_message(outgoing_chat_msg)

        return [outgoing_chat_msg]


    #Splitting large messages:
    def split_large_message(self, large_message):
        current_log_prefix = self.logger_prefix + "split_large_message:"
        self.logger.info(f"{current_log_prefix}Splitting message of {len(large_message)} characters")
        
        chunk_size = 485
        message_chunks = []
        
        # Split the message into chunks of 485 characters
        for i in range(0, len(large_message), chunk_size):
            chunk = large_message[i:i + chunk_size]
            message_chunks.append(chunk)
        
        self.logger.info(f"{current_log_prefix}Split into {len(message_chunks)} chunks")
        return message_chunks


    ########################################################################
    ############### CHECKING IF INCOMMING CHAT MESSAGE IS OKAY #############
    ########################################################################    


    #Not only for shout outs, but also automatic "Thank you for you support!" to subscribers
    async def check_for_automatic_shout_out(self, msg):
        current_log_prefix = self.logger_prefix + "check_for_automatic_shout_out:"
        
        # :coolingenwastaken!coolingenwastaken@coolingenwastaken.tmi.twitch.tv PRIVMSG #coolingenwastaken :%hei

        #Returnerer alltid brukernavn :)
        username, main_command, params  = self.find_sender_and_msg(msg)
        self.logger.info(f"{current_log_prefix}Checking auto-so for username:{username}")
        self.logger.info(f"{current_log_prefix}Got main_command:{main_command}")
        self.logger.info(f"{current_log_prefix}Got params:{params}")

        username = username.rstrip()

        if username.upper() == config.BOT_USERNAME.upper() or username.upper() == 'ALBOTKEINSTEIN' or username.upper() ==  'TMI.TWITCH.TV' or username.upper() == 'ALBOTKEINSTEIN.TMI.TWITCH.TV':
            self.logger.info(f"{current_log_prefix}Not checking any furter when this user is typing to us (albot or twitch):{username}")
            return


        #SOUNDALERTS!!
        #SOUNDALERT-POKEMON
        #[':soundalerts!soundalerts@soundalerts.tmi.twitch.tv', 'PRIVMSG', '#thestreamteamwastaken', ':flayrestarr', 'played', 'Gotta', 'Catch', 'them', 'ALL!!', 'for', '50', 'Bits\r']
        #username = soundalert, main_command = 'flayrestarr', params = 'played Gotta Catch them ALL!! for 50 Bits\r'
        #SOUNDALERT-SUBSCRIPTION
        #[':streamlabs!streamlabs@streamlabs.tmi.twitch.tv', 'PRIVMSG', '#thestreamteamwastaken', ':flayrestarr', 'just', 'subscribed', 'with', 'Tier', '1!\r']
        #username = soundalert, main_command = 'flayrestarr', params = 'just subscribed with Tier 1!\r'
        #SOUNDALERT-I'm in danger
        #[':soundalerts!soundalerts@soundalerts.tmi.twitch.tv', 'PRIVMSG', '#thestreamteamwastaken', ':Rhastaface', 'played', "I'm", 'in', 'danger!', 'for', '10', 'Bits\r']
        #username = soundalert, main_command = 'Rhastaface', params = 'played I'm in danger! for 10 bits\r'
        #SOUNDALERT-RUN!
        #[':soundalerts!soundalerts@soundalerts.tmi.twitch.tv', 'PRIVMSG', '#thestreamteamwastaken', ':Rhastaface', 'played', 'RUN', 'for', '50', 'Bits\r']
        #username = soundalert, main_command = 'Rhastaface', params = 'played RUN for 50 bits\r'

        #STREAMELEMENTS can also be handled:
        #[':streamelements!streamelements@streamelements.tmi.twitch.tv', 'PRIVMSG', '#thestreamteamwastaken', ':@verstoppel,','verstoppel', 'has', 'been', 'following', 'thestreamteamwastaken', 'for', '', '4', 'years', '6', 'months', '17', 'days', '21', 'hours\r']


        #FIXED:
        #':flayrestarr', 'played', 'Scary!', '"I', 'seeeeee', 'youuuu!"', 'for', '200', 'Bits\r']
        #params = 'played Scary! "I seeeeee youuuu!" for 200 Bits\r'

        #TO BE DONE?
#         utils/TwitchConnection=>start_messsage_loop:Catch-all-messages:/:soundalerts!soundalerts@soundalerts.tmi.twitch.tv PRIVMSG #thestreamteamwastaken :Rhastaface played
# I'm in danger! for 10 Bits
# logs\bog_20250602_222317.log:239:2025-06-02 22:38:22,515 - twitch_bot - INFO -
# utils/TwitchConnection=>start_messsage_loop:Catch-all-messages:/:soundalerts!soundalerts@soundalerts.tmi.twitch.tv PRIVMSG #thestreamteamwastaken :Rhastaface played
# RUN for 50 Bits
# logs\bog_20250602_222317.log:343:2025-06-02 22:50:06,740 - twitch_bot - INFO -
# utils/TwitchConnection=>start_messsage_loop:Catch-all-messages:/:soundalerts!soundalerts@soundalerts.tmi.twitch.tv PRIVMSG #thestreamteamwastaken :Rhastaface played
# GG  for 10 Bits

        self.logger.info(f"{current_log_prefix}Moment of truth:{username}=coolingenwastaken?({username=='coolingenwastaken'})")


        if username == 'soundalerts'.lower() or username.lower() == 'coolingenwastaken':
            self.logger.info(f"{current_log_prefix}Whoa! It's a soundalert! Check if we play a gif to this!")
            await self.cmd_handler.soundalert_gif(main_command, params) #Sending main_command in this case is the user activating soundalert, params is the soundalert info
        else:
            await self.cmd_handler.check_auto_greetings(username)
            await self.cmd_handler.create_auto_shout_out(username, is_auto_so = True)
            await self.cmd_handler.check_auto_thanks_for_subscribers(username)


    #STEP 1 - Splitting the message into sender and message
    def find_sender_and_msg(self, chat_msg):

        current_log_prefix = self.logger_prefix + "find_sender_and_msg:"
        # :coolingenwastaken!coolingenwastaken@coolingenwastaken.tmi.twitch.tv PRIVMSG #coolingenwastaken :%hei

        split_chat = chat_msg.split(' ')


        self.logger.info(f"{current_log_prefix}Message split: {split_chat}")


        is_PRIVMSG = split_chat[1] == "PRIVMSG"

        #Format :coolingenwastaken!coolingenwastaken@coolingenwastaken.tmi.twitch.tv - want the first coolingenwastaken
        username_sending_message = split_chat[0][1:].split('!')[0]

        self.logger.info(f"{current_log_prefix}Detected sender: {username_sending_message}")

        if not is_PRIVMSG:
            self.logger.info(f"{current_log_prefix}Not a PRIVMSG-message - not for us:{chat_msg}")
            return[username_sending_message,"", ""]


        is_command = split_chat[3][1].startswith(f"{config.PREFIX_FOR_BOT_TO_READ}")

        if is_command or username_sending_message in ['soundalert', 'coolingenwastaken']:

            #If soundalerts, then we don't remove the first letter, since it won't be a '%'
            if is_command:
                split_chat[3]   = split_chat[3][2:]
            else:
                self.logger.info(f"{current_log_prefix}Before split_chat[3]:/{split_chat[3]}/")
                split_chat[3]   = split_chat[3][1:]
                self.logger.info(f"{current_log_prefix}After split_chat[3]:/{split_chat[3]}/")


            split_chat[-1]  = split_chat[-1].rstrip()
            main_command    = split_chat[3]

            params          = ""

            if len(split_chat) > 4:
                params = (' ').join(split_chat[4:])

            self.logger.info(f"{current_log_prefix}Command rebuilt! Let's get it up and running: /{main_command}/ with params:{params}")
            return([username_sending_message, main_command, params])
        else:
            self.logger.info(f"{current_log_prefix}Doesn't start with:/{config.PREFIX_FOR_BOT_TO_READ}/, starts with:{split_chat[3][1]}")
            return[username_sending_message,"", ""]
        

    #STEP 2 - Checking if the sent message contains any characters not allowed?
    #Don't want code-injections!
    def is_safe_command(self, chat_msg_sent):
        current_log_prefix = self.logger_prefix + "is_safe_command:"

        # Define explicitly what characters are allowed
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_+- øæåÆØÅ')
        
        # Check each character in the command
        disallowed_found = []
        for char in chat_msg_sent:
            if char not in allowed_chars:
                disallowed_found.append(char)
        
        # If we found any disallowed characters
        if disallowed_found:
            disallowed_str = ', '.join([f"'{c}'" for c in set(disallowed_found)])
            self.logger.info(f"{current_log_prefix}Command rejected. Disallowed characters found: {disallowed_str} in: {chat_msg_sent}")
            return False
        
        return True  

#IF WE LATER ON WANT TO CHECK THE REVERSE - CHECKING FOR UNSAFE LETTERS, IN THIS CASE SUCH AS KOREAN AND JAPANESE LETTERS
#CAN ALSO PASS THROUGH. We don't have commands for other languages per now any way - so not a issue for the forseeable future.
# def is_safe_command(self, chat_msg_sent):
#     current_log_prefix = self.logger_prefix + "is_safe_command:"
    
#     # Define explicitly what characters are NOT allowed
#     # This blocks common injection attempts while allowing all Unicode characters
#     disallowed_chars = set('{}[]()<>|\\;\'"`&$%^!*')
    
#     # Check for any disallowed characters
#     disallowed_found = []
#     for char in chat_msg_sent:
#         if char in disallowed_chars:
#             disallowed_found.append(char)
    
#     # If we found any disallowed characters
#     if disallowed_found:
#         disallowed_str = ', '.join([f"'{c}'" for c in set(disallowed_found)])
#         self.logger.info(f"{current_log_prefix}Command rejected. Disallowed characters found: {disallowed_str} in: {chat_msg_sent}")
#         return False
    
#     return True