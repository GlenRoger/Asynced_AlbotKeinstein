#Get all gif-owners
import utils.TenorConnection as TC
import config
import os
import asyncio


class GifHandler:

    def __init__(self, logger):
        self.logger_prefix = "utils/GifHandler=>"
        self.logger = logger

        self.known_gifs_file = f"{config.MEDIA_FOLDER_GIF}known_gifs.csv"

        self.sub_gif_greetings  = {}
        self.gif_owners_dict    = {}
        self.known_gifs_dict    = {}


    async def setup(self):
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



                        if not os.path.exists(f"{config.MEDIA_FOLDER_GIF}{gif_name}.gif"):
                            self.logger.info(f"{current_log_prefix}File:{config.MEDIA_FOLDER_GIF}{gif_name}.gif does NOT exists. Getting it!")
                            await self.get_gif(gif_id, gif_owner, gif_name)
                        else:
                            self.logger.info(f"{current_log_prefix}File:{config.MEDIA_FOLDER_GIF}{gif_name}.gif exists already.")

                    else:
                        self.logger.info(f"{current_log_prefix}Couldn't understand input from file{self.known_gifs}. Input gotten:/{line}/ - could not be split into gif_id, gif_owner and gif_name.")
                        continue


        else:
            self.logger.info(f"{current_log_prefix}File:{self.known_gifs_file} does NOT exists.")


    def build_gif_greetings(self):
        current_log_prefix = self.logger_prefix + "build_gif_greetings:"
        self.logger.info(f"{current_log_prefix}Building special greetings")


        file_with_greetings = config.MEDIA_FOLDER_GIF+"subs_greetings.csv"


        if os.path.exists(f"{file_with_greetings}"):

            with open(file_with_greetings, 'r', encoding='utf8') as file:
                
                for line in file.readlines():
                    if line.startswith('#'):
                        continue

                    split_list = line.split(';')


                    twitch_name     = ""
                    gif_to_show     = ""
                    sound_to_play   = ""

                    if len(split_list) == 3:

                        twitch_name         = split_list[0]
                        gif_to_show         = split_list[1]
                        sound_to_play       = split_list[2].rstrip()


                        self.sub_gif_greetings[twitch_name] = f"{gif_to_show};{sound_to_play}"

                    else:
                        self.logger.info(f"{current_log_prefix}Couldn't understand input from file {file_with_greetings}. Input gotten:/{line}/ - could not be split into Twitch_name, gif_to_show and sound_to_play.")
                        continue




    async def get_gif(self, gif_id, owner, gif_name):
        current_log_prefix = self.logger_prefix + "get_gif:"
        self.logger.info(f"{current_log_prefix}Getting gif: {gif_id} to name it {gif_name} from the {owner}")

        current_log_prefix = self.logger_prefix + "get_gif:"
        self.logger.info(f"{current_log_prefix}Downloading gif:{gif_name}")

        owner = self.gif_owners_dict[owner]
        success = await owner.get_gif(gif_id, gif_name)

        if success:
            print(f"Downloaded gif: {gif_name}")
        else:
            print(f"Couldn't download gif: {gif_name}")