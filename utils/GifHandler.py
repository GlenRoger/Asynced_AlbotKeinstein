#Get all gif-owners
import utils.TenorConnection as TC
import config
import os
import asyncio
from PIL import Image
import random

class GifHandler:

    def __init__(self, logger):
        self.logger_prefix = "utils/GifHandler=>"
        self.logger = logger

        self.known_gifs_file = f"{config.MEDIA_FOLDER_GIF}known_gifs.csv"

        self.sub_gif_greetings  = {}
        self.gif_owners_dict    = {}
        self.known_gifs_dict    = {}


        self.list_pokemon_bits_gifs         = []
        self.list_scary_i_see_you_bits_gifs = []
        self.list_halloween_gifs            = []


    def print_all(self):
        print(f"{self.known_gifs_dict}")

    #Called for refreshing gifs command, so refresh lists as well
    async def arrange_gifs(self):

        self.list_pokemon_bits_gifs         = []
        self.list_scary_i_see_you_bits_gifs = []
        self.list_halloween_gifs            = []

        current_log_prefix = self.logger_prefix + "setup:"
        self.logger.info(f"{current_log_prefix}Setup running!")
        self.build_gif_owner_dicts()
        await self.read_known_gifs_into_dict()
        self.build_gif_greetings()

    #Making it easier to search for where the gifs are located on the internet
    def build_gif_owner_dicts(self):
        current_log_prefix = self.logger_prefix + "build_gif_owner_dicts:"
        self.logger.info(f"{current_log_prefix}Building dictionaries for gif-owners")

        self.Tenor_gifs     = TC.TenorConnection(self.logger)
        self.Tenor_gifs.get_api_key()

        self.gif_owners_dict['TENOR'] = self.Tenor_gifs

    #Default blir 5 sek, ellers henter ut utregnet duration
    def get_gif_duration(self, gif_name):
        """Get duration of a known GIF"""
        return self.known_gifs_dict.get(gif_name, {}).get("duration", 5000)

    #Hente ut hele path til et gif
    def get_gif_path(self, gif_name):
        """Get path of a known GIF"""
        return self.known_gifs_dict.get(gif_name, {}).get("path", "")

    #Sjekke om gif eksisterer
    def gif_exists(self, gif_name):
        """Check if GIF exists in our collection"""
        return gif_name in self.known_gifs_dict

    #Utregnet gif-lengde i duration
    def calculate_gif_duration(self, gif_path):
        """Get the total duration of a GIF in milliseconds"""
        try:
            with Image.open(gif_path) as img:
                total_duration = 0
                frame_count = 0
                
                # Loop through all frames
                while True:
                    try:
                        # Get frame duration (in milliseconds)
                        frame_duration = img.info.get('duration', 100)  # Default 100ms if not specified
                        total_duration += frame_duration
                        frame_count += 1
                        img.seek(frame_count)  # Move to next frame
                    except EOFError:
                        break  # No more frames
                        
                return total_duration
        except Exception as e:
            self.logger.error(f"Error getting GIF duration: {e}")
            return 5000  # Default fallback duration
        

    #Download if necessary, if the files in the known_gifs.csv-file isn't already downloaded.
    async def read_known_gifs_into_dict(self):
        current_log_prefix = self.logger_prefix + "read_known_gifs_into_dict:"
        self.logger.info(f"{current_log_prefix}Checking known_gif.csv-file for gifs if we got them already")

        if os.path.exists(self.known_gifs_file):
            self.logger.info(f"{current_log_prefix}File:{self.known_gifs_file} exists.")

            with open(self.known_gifs_file, 'r', encoding='utf8') as file:
                for line in file.readlines():
                    if line.startswith('#'):
                        continue

                    split_list = line.split(';')

                    gif_id = ""
                    gif_owner = ""
                    gif_name = ""

                    if len(split_list) == 3:

                        gif_id      = split_list[0]
                        gif_owner   = split_list[1]
                        gif_name    = split_list[2].rstrip()

                        #Sjekke om noen har kopiert med hele URL'en, da må vi clean'e litt.
                        if gif_id[0] == 'h':
                            gif_id = gif_id.split('-')[-1]


                        got_gif_file = False

                        gif_path = f"{config.MEDIA_FOLDER_GIF}{gif_name}.gif"


                        if not os.path.exists(gif_path):
                            self.logger.info(f"{current_log_prefix}File:{gif_path} does NOT exists. Getting it!")
                            got_gif_file = await self.get_gif(gif_id, gif_owner, gif_name)
                        else:
                            self.logger.info(f"{current_log_prefix}File:{gif_path} exists already.")
                            got_gif_file = True

                        gif_duration = self.calculate_gif_duration(gif_path)

                        self.known_gifs_dict[gif_name] = {
                            "path":gif_path,
                            "duration":gif_duration,
                            "id": gif_id,
                            "owner": gif_owner}

                        if gif_name.startswith("LIST_POKEMON_BITS_"):
                            self.list_pokemon_bits_gifs.append(gif_name)
                        elif gif_name.startswith("LIST_SCARY_I_SEE_YOU_BITS_"):
                            self.list_scary_i_see_you_bits_gifs.append(gif_name)
                        elif gif_name.startswith("LIST_HALLOWEEN_"):
                            self.list_halloween_gifs.append(gif_name)
                    else:
                        self.logger.info(f"{current_log_prefix}Couldn't understand input from file{self.known_gifs}. Input gotten:/{line}/ - could not be split into gif_id, gif_owner and gif_name.")
                        continue


        else:
            self.logger.info(f"{current_log_prefix}File:{self.known_gifs_file} does NOT exists.")

    def get_sub_gif_greetings(self, sender):

        if sender in self.sub_gif_greetings.keys():
            return self.sub_gif_greetings[sender]
        
        return self.sub_gif_greetings['default']

    def got_default_gif(self, sender):

        if sender in self.sub_gif_greetings.keys():
            return False
        
        return True



    def build_gif_greetings(self):
        self.sub_gif_greetings.clear()

        current_log_prefix = self.logger_prefix + "build_gif_greetings:"
        self.logger.info(f"{current_log_prefix}Building special greetings")

        file_with_greetings = config.MEDIA_FOLDER+"subs_greetings.csv"


        if os.path.exists(f"{file_with_greetings}"):

            with open(file_with_greetings, 'r', encoding='utf8') as file:
                self.logger.info(f"{current_log_prefix}Reading file {file_with_greetings}")

                for line in file.readlines():
                    if line.startswith('#'):
                        print(f"SKIPPING LINE {line}")
                        continue

                    print(f"ANALYZING LINE {line}")

                    split_list = line.split(';')


                    twitch_name     = ""
                    gif_to_show     = ""
                    sound_to_play   = ""

                    if len(split_list) == 3:

                        twitch_name         = split_list[0]
                        gif_to_show         = split_list[1]
                        sound_to_play       = split_list[2].rstrip()


                        self.sub_gif_greetings[twitch_name] = f"{gif_to_show}:{sound_to_play}"

                    else:
                        self.logger.info(f"{current_log_prefix}Couldn't understand input from file {file_with_greetings}. Input gotten:/{line}/ - could not be split into Twitch_name, gif_to_show and sound_to_play.")
                        continue

            self.logger.info(f"{current_log_prefix}\n\n\nFINAL RESULT SUB GREETINGS {self.sub_gif_greetings}\n\n\n")


    async def get_gif(self, gif_id, owner, gif_name):
        current_log_prefix = self.logger_prefix + "get_gif:"
        self.logger.info(f"{current_log_prefix}Getting gif: {gif_id} to name it {gif_name} from the {owner}")
        self.logger.info(f"{current_log_prefix}Downloading gif:{gif_name}")

        owner = self.gif_owners_dict[owner]
        success = await owner.get_gif(gif_id, gif_name)

        if success:
            print(f"Downloaded gif: {gif_name}")
            return True
        else:
            print(f"Couldn't download gif: {gif_name}")
            return False
        

    def get_random_pokemon_bits_list(self):
        return random.choice(self.list_pokemon_bits_gifs)
    
    def get_random_scary_i_see_you_bits_list(self):
        return random.choice(self.list_scary_i_see_you_bits_gifs)
    
    def get_random_halloween_list(self):
        return random.choice(self.list_halloween_gifs)