# utils/twitch_interface.py

import re

#Example of API-interactions from Twitch API, (only informational?):
# Kan også legge til andre forespørslerl mot API'et, f.eks. hente mods, VIPS og kanskje subs(?).
#:tmi.twitch.tv 001 albotkeinstein :Welcome, GLHF!
#:tmi.twitch.tv 002 albotkeinstein :Your host is tmi.twitch.tv
#:tmi.twitch.tv 003 albotkeinstein :This server is rather new
#:tmi.twitch.tv 004 albotkeinstein :-
#:tmi.twitch.tv 375 albotkeinstein :-
#:tmi.twitch.tv 372 albotkeinstein :You are in a maze of twisty passages, all alike.
#:tmi.twitch.tv 376 albotkeinstein :>


#Example of messages to be handled from Twitch and connecting, 
# nothing needs to be done with these:
#:albotkeinstein!albotkeinstein@albotkeinstein.tmi.twitch.tv JOIN #coolingenwastaken
#:albotkeinstein.tmi.twitch.tv 353 albotkeinstein = #coolingenwastaken :albotkeinstein
#:albotkeinstein.tmi.twitch.tv 366 albotkeinstein #coolingenwastaken :End of /NAMES list


#Example messages from chat - written by coolingenwastaken:
# :coolingenwastaken!coolingenwastaken@coolingenwastaken.tmi.twitch.tv PRIVMSG #coolingenwastaken :!albotrest


#Regex, escape these chars => . ^ $ * + - ? ( ) [ ] { } \ |


class TwitchInterface:
    def __init__(self, connection):
        self.connection = connection
        self.messages_sent = 0

    def set_name(self, name):
        self.name = name

    def set_channel(self, channel):
        self.channel = channel

    def set_command_sign(self, command_sign):
        self.command_sign = command_sign

    def send_message(self, message):
        print(f"I'm asked to send /{message}/")
        ret_val = self.connection.send(f"PRIVMSG #{self.channel} :{message}\n".encode("utf-8"))
        print(f"ret_val from sending:/{ret_val}/")
        self.messages_sent += 1

    def get_nr_messages_sent(self):
        return self.messages_sent

    def set_allowed_users_of_commands(self, list_of_allowed_users):
        self.list_of_allowed_users = list_of_allowed_users
  
    def on_the_nice_list_of_allowed_users(self, username):
        if username in self.list_of_allowed_users:
            return True
        return False

    def safety_check(self, raw_message):

        #There can only be one PRIVMSG
        if len(raw_message.split(".tmi.twitch.tv PRIVMSG #")) != 2:
            print(f"This message doesn't belong here! Either PRIVMSG is missing or someone wrote that in chat.. got {raw_message}")
            return False

        return True
    
    def parse_message(self, raw_message):
        # Parse message implementation

        print("In parse_message..")

        #Safety checks
        if not self.safety_check(raw_message):
            return ""

        raw_message_split_at_PRIVMSG = raw_message.split(".tmi.twitch.tv PRIVMSG #")
        #what we start with
        #:coolingenwastaken!coolingenwastaken@coolingenwastaken.tmi.twitch.tv PRIVMSG #coolingenwastaken :!albotsing

        chat_info = raw_message_split_at_PRIVMSG[1].rstrip()
        #What we have after this line:
        #coolingenwastaken :!albotsing

        print(chat_info)

        username_pattern = re.compile('\s*([a-z0-9\_]+)\s+:{1}')

        re_pattern_to_accept = re.compile('\s*([a-z0-9\_]+)\s+:{1}([a-z0-9æøå\-\s*\+' +self.command_sign +']*)', re.IGNORECASE)
                                          
        match_list = re.findall(re_pattern_to_accept, chat_info)

        username = match_list[0][0]
        command = ""

        print(f"Regex magic ended up with:/{match_list}/")

        if len(match_list[0]) == 2:
            print(f"Got Gold? => user /{match_list[0][0]}/:/{match_list[0][1]}/")
            if match_list[0][1].startswith(self.command_sign):
                command = match_list[0][1]
            else:
                print("No gold!!")
        else:
            print(f"Got trash? length:{len(match_list[0])}=2? Didn't start with '!'? => /{match_list}/")

        # parse_response = raw_message.split(f"#{username} :")[1].rstrip()

        parsed_data = ""

        print("Leaving parse_message..")

        return [username, command]
        
    #Brukes når vi skal motta mer info fra Twitch API i form av https-request(?)
    #Kanskje f.eks. når vi hente info om Mods, VIPs og subs?
    def parse_api_response(self, response):
        # Parse API response
        parsed_data = ""
        return parsed_data