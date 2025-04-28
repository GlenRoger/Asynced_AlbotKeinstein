
#Usage: https://developers.google.com/tenor/guides/quickstart#python
#Tips for more stuff: https://developers.google.com/tenor/guides/response-objects-and-errors
#Maybe gif-transparent would be fun to try out some time later..

#Rate and limits:
#1 per sec, but store and cache those used often
#More info: https://developers.google.com/tenor/guides/rate-limits-and-caching
#Should not be a problem, since a gif lasts longer than a second and we only play one at a time

import config
import os
import requests
import asyncio

class TenorConnection:


    def __init__(self, logger):
        self.logger_prefix = "utils/TwitchConnection=>"
        self.logger = logger
        self.api_key = ''
        # self.api_client_key = config.TENOR_CLIENT_NAME  #Not sure we need to use this..
        self.save_folder = config.MEDIA_FOLDER_GIF


    def get_api_key(self):
        file_to_read = config.TENOR_API_KEY

        if os.path.exists(file_to_read):

            with open(file_to_read, 'r') as f:
                self.api_key = f.read().strip()
                # self.logger.info(f"{self.api_key}OAuth token loaded from file: /{self.api_key}/")


    #downloading the gif and saves it to the fold for gifs
    async def get_gif(self, gif_id, gif_name):
        current_log_prefix = self.logger_prefix + "get_gif:"
        self.logger.info(f"{current_log_prefix}Downloading gif:{gif_name}, belonging to Tenor.")


        # Make the API request to get the specific GIF
        endpoint = f"https://tenor.googleapis.com/v2/posts?ids={gif_id}&key={self.api_key}"

        self.logger.info(f"{current_log_prefix}Building up endpoint belonging to Tenor {endpoint}")

        response = requests.get(endpoint)

        data = response.json()

        # Extract the GIF URL
        if "results" in data and len(data["results"]) > 0:
            # Get the GIF URL from the response
            gif_url = data["results"][0]["media_formats"]["gif"]["url"]
            self.logger.info(f"{current_log_prefix}Downloading gif:{gif_url}, belonging to Tenor.")
    

            gif_response = requests.get(gif_url)
            download_gif_file = f"{self.save_folder}{gif_name}.gif"

            if not os.path.exists(download_gif_file):
                with open(download_gif_file, "wb") as f:
                    f.write(gif_response.content)
                    print(f"GIF downloaded as {download_gif_file}")
                    return True
            else:
                self.logger.info(f"{current_log_prefix}Couldn't download GIF, already existed:{download_gif_file}")
                return False

        else:
            self.logger.info(f"{current_log_prefix}GIF not found or error in response:{data}")
            return False

#Maybe could be fun?? AI-search for gif.
# lmt = 8
# ckey = "my_test_app"  # set the client_key for the integration and use the same value for all API calls

# # our test search
# search_term = "excited"

# # get the top 8 GIFs for the search term
# r = requests.get(
#     "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey,  lmt))

# if r.status_code == 200:
#     # load the GIFs using the urls for the smaller GIF sizes
#     top_8gifs = json.loads(r.content)
#     print(top_8gifs)
# else:
#     top_8gifs = None

