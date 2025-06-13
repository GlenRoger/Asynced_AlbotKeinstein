import asyncio
import requests
import config
import sys


class UserRoleManager:


    def __init__(self, logger):
        self.logger_prefix = "utils/UserRoleManager=>"
        self.logger = logger
        

        self.client_id          = ""
        self.access_token       = ""

        self.client_id_br       = ""
        self.access_token_br    = ""

        #To be filled
        self.MODs_list                  = []
        self.VIPs_list                  = []
        self.subscribers_list           = []
        self.followers_list             = []
        self.followers_dict             = {}

        self.cron_sorted_followers      = []
        self.cron_sorted_followers_names_only = []


    async def buildlists(self, refresh_list = "all"):
        current_log_prefix = self.logger_prefix + "buildlists:"

        self.logger.info(f"\n\n#################### BUILDING LISTS START #########################\n{current_log_prefix}Bygger lister over MODs, VIPs, subscribers og followers.")

        if refresh_list.upper() == 'ALL' or refresh_list == 'MODS':
            await self.get_MODs_list()
            # print(f"MODs list:{self.MODs_list}")

        if  refresh_list.upper() == 'ALL' or refresh_list == 'VIPS':
            await self.get_VIPs_list()
            # print(f"VIPs list:{self.VIPs_list}")

        if  refresh_list.upper() == 'ALL' or refresh_list == 'SUBSCRIBERS':
            await self.get_subscribers_list()
            # print(f"Subscribers:{self.subscribers_list}")

        if  refresh_list.upper() == 'ALL' or refresh_list == 'FOLLOWERS':

            await self.get_followers_list()
            # print(f"Followers:{self.followers_list}")

            self.make_cron_sorted_followers_list()



            #TEST
            # teller = 1
            # for fl in self.cron_sorted_followers:
            #     self.logger.info(f"{teller}:{fl}")
            #     print(f"{teller}:{fl}")
            #     teller += 1

            #For å test at alt er ok.
            self.get_xfirst_follower(10)

        # sys.exit()


        self.logger.info(f"{current_log_prefix}Ferdig med å bygge lister!\n#################### BUILDING LISTS END   #########################\n\n")

        for user_name in ["coolingenwastaken", "nurseiplier", "mammaronning", "syrinvakyrie02", "verstoppel", "flayrestarr", "VillandTV", "PhexTheFlex", "Prompeten" ]:
            roles =  self.get_all_user_roles(user_name)
            print(f"user: {user_name} got following roles: {roles} and was follower#{self.get_user_follower_nr(user_name)}")


    def setOauthTokens(self, token, token_br):
        self.access_token       = token
        self.access_token_br    = token_br


    def setCliend_ids(self, client, client_br):
        self.client_id          = client
        self.client_id_br       = client_br


    #Henter ut alle mods
    async def get_MODs_list(self):

        self.MODs_list.clear()

        current_log_prefix = self.logger_prefix + "get_MODs_list:"

        self.logger.info(f"{current_log_prefix}Contacting server for logging in")
      
        token = self.access_token_br.replace("oauth:", "")

        headers = {"Authorization": f"Bearer {token}", "Client-ID": self.client_id_br}
        response = requests.get(f"https://api.twitch.tv/helix/users?login={config.CHANNEL}", headers=headers)
        channel_id = response.json()["data"][0]["id"]

        if response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get channel ID: {response.text}")
            return

        channel_id = response.json()["data"][0]["id"]
        self.logger.info(f"{current_log_prefix}Got channel ID: {channel_id} for {config.CHANNEL}")
    
        # Now get the MODs
        mods_response = requests.get(
            f"https://api.twitch.tv/helix/moderation/moderators?broadcaster_id={channel_id}", 
            headers=headers
        )
        
        if mods_response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get MODs: {mods_response.text}")
            return
        
        mods_data = mods_response.json()["data"]
        mods_usernames = [mod["user_name"] for mod in mods_data]
        
        self.logger.info(f"{current_log_prefix}Found {len(mods_usernames)} MODs.\n")
        self.MODs_list =  mods_usernames


    #Henter ut alle VIPs
    async def get_VIPs_list(self):

        self.VIPs_list.clear()

        current_log_prefix = self.logger_prefix + "get_VIPs_list:"

        self.logger.info(f"{current_log_prefix}Contacting server for logging in")
      
        token = self.access_token_br.replace("oauth:", "")
        

        headers = {"Authorization": f"Bearer {token}", "Client-ID": self.client_id_br}
        response = requests.get(f"https://api.twitch.tv/helix/users?login={config.CHANNEL}", headers=headers)
        channel_id = response.json()["data"][0]["id"]

        if response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get channel ID: {response.text}")
            return

        channel_id = response.json()["data"][0]["id"]
        self.logger.info(f"{current_log_prefix}Got channel ID: {channel_id} for {config.CHANNEL}")
    
        # Now get the VIPs
        vip_response = requests.get(
            f"https://api.twitch.tv/helix/channels/vips?broadcaster_id={channel_id}", 
            headers=headers
        )
        
        if vip_response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get VIPs: {vip_response.text}")
            return
        
        vips_data = vip_response.json()["data"]
        vip_usernames = [vip["user_name"] for vip in vips_data]
        
        self.logger.info(f"{current_log_prefix}Found {len(vip_usernames)} VIPs.\n")
        self.VIPs_list =  vip_usernames

    #Henter ut alle subscribers vi har
    async def get_subscribers_list(self):

        self.subscribers_list.clear()

        current_log_prefix = self.logger_prefix + "get_subscribers_list:"

        self.logger.info(f"{current_log_prefix}Contacting server for logging in")
      
        token = self.access_token_br.replace("oauth:", "")

        headers = {"Authorization": f"Bearer {token}", "Client-ID": self.client_id_br}
        response = requests.get(f"https://api.twitch.tv/helix/users?login={config.CHANNEL}", headers=headers)
        channel_id = response.json()["data"][0]["id"]

        self.logger.info(f"{current_log_prefix}Gotten the {channel_id} for {config.CHANNEL}")

        headers = {"Authorization": f"Bearer {token}", "Client-ID": self.client_id_br}
        sub_response = requests.get(f"https://api.twitch.tv/helix/subscriptions?broadcaster_id={channel_id}", headers=headers)

        if sub_response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get subscribers: {sub_response.text}")
            return
        
        subs_data = sub_response.json()["data"]
        subs_usernames = [sub["user_name"] for sub in subs_data]
        
        self.logger.info(f"{current_log_prefix}Found {len(subs_usernames)} subscribers.\n")
        self.subscribers_list =  subs_usernames


    #Henter alle følgere vi har
    async def get_followers_list(self):

        self.followers_list.clear()
        self.followers_dict.clear()

        current_log_prefix = self.logger_prefix + "get_followers_list:"
        
        self.logger.info(f"{current_log_prefix}Getting followers for channel {config.CHANNEL}")
        
        token = self.access_token_br.replace("oauth:", "")

        # print(f"TOKEN:/{token}/")

        # First get the channel ID
        headers = {"Authorization": f"Bearer {token}", 
                "Client-ID": self.client_id_br}
        
        response = requests.get(f"https://api.twitch.tv/helix/users?login={config.CHANNEL}", 
                            headers=headers)
        
        if response.status_code != 200:
            self.logger.error(f"{current_log_prefix}Failed to get channel ID: {response.text}")
            return
            
        channel_id = response.json()["data"][0]["id"]
        
        # Get followers
        followers = []
        pagination = ""
        
        count_pagination = 0

        # We need to paginate through results since Twitch limits to 100 per request
        while True:

            count_pagination += 1

            pagination_query = f"&after={pagination}" if pagination else ""
            followers_url = f"https://api.twitch.tv/helix/channels/followers?broadcaster_id={channel_id}&first=100{pagination_query}"
            
            followers_response = requests.get(followers_url, headers=headers)
            
            if followers_response.status_code != 200:
                self.logger.error(f"{current_log_prefix}Failed to get followers: {followers_response.text}")
                break
                
            result = followers_response.json()
            followers.extend(result["data"])
            
            # Check if we need to paginate more
            if "pagination" in result and "cursor" in result["pagination"]:
                pagination = result["pagination"]["cursor"]
                self.logger.info(f"{current_log_prefix}Getting next page of followers...{count_pagination}")
            else:
                break
        
        self.logger.info(f"{current_log_prefix}Found {len(followers)} followers.\n")
        
        # Each follower object contains follow date info
        for follower in followers:
            # if follower['user_name'].upper() != follower['user_login'].upper():
                # print(f"name: {follower['user_name'].upper()} != login: {follower['user_login'].upper()}")
                # sys.exit()
            # follower_name = follower["user_name"]  # => In chat we see the user_login name, not the user_name!
            follower_name = follower["user_login"]
            followed_at = follower["followed_at"]  # ISO format date string
            # self.logger.info(f"{current_log_prefix}User {follower_name} following since {followed_at}")
            self.followers_dict[follower_name] = followed_at

        # self.logger.info(followers)


        self.followers_list = followers

    #Returns bool
    def is_Subscriber(self, username):
        return username in self.subscribers_list

    #Henter ut alle roller en bruker har (TSTWTMEMBERS, MODS, VIPS, SUBSCRIBERS, FOLLOWERS eller bare [] hvis du ikke følger oss.)
    def get_all_user_roles(self, user):

        current_log_prefix = self.logger_prefix + "get_all_user_roles:"
        
        self.logger.info(f"{current_log_prefix}Checking roles for {user}")

        all_roles_list = []

        if user in config.TSTWTMEMBERS:
            all_roles_list.append("TSTWTMEMBERS")
        
        if user in self.MODs_list:
            all_roles_list.append("MODS")

        if user in self.VIPs_list:
            all_roles_list.append("VIPS")

        if user in self.subscribers_list:
            all_roles_list.append("SUBSCRIBERS")

        if user in self.followers_dict.keys():
            all_roles_list.append("FOLLOWERS")


        self.logger.info(f"{current_log_prefix}User:{user} have the following roles:{all_roles_list}")

        return all_roles_list


    #Sorterer følgere basert på tidspunktet de starte å følge oss, legger navnet i en liste før senere søking.
    def make_cron_sorted_followers_list(self):
        # Sort by follow date descending (most recent first)
        self.cron_sorted_followers = sorted(self.followers_dict.items(), key=lambda x: x[1], reverse=False)

        for sorted_follower in self.cron_sorted_followers:
            self.cron_sorted_followers_names_only.append(sorted_follower[0])



    #Henter ut hvilken nummer i rekken følgere en seer er, returnerer -1, dersom seeren ikke følger oss.
    def get_user_follower_nr(self, user):

        if user.lower() in self.cron_sorted_followers_names_only:
            return self.cron_sorted_followers_names_only.index(user.lower()) + 1
        
        return -1


    #Kan brukes til å finne OG - kanskje ikke bruke for stream..
    def get_xfirst_follower(self, xfirst):

        # Get the top X (e.g., top 5)
        top_x = xfirst
        top_followers = self.cron_sorted_followers[:top_x]

        # Print or use the results
        for username, followed_at in top_followers:
            print(f"{username} followed on {followed_at}")

    #Hente ut siste spill av streamer, for <username> som skal få shoutout
    async def get_streamer_last_game(self, username):
        """Get the last game played by a streamer from Twitch API"""
        current_log_prefix = self.logger_prefix + "get_streamer_last_game:"
        
        try:
            # Prepare API request
            token = self.access_token_br.replace("oauth:", "")
            headers = {
                "Authorization": f"Bearer {token}", 
                "Client-ID": self.client_id_br
            }
            
            # First get the user ID from username
            response = requests.get(
                f"https://api.twitch.tv/helix/users?login={username.lower()}", 
                headers=headers
            )
            
            if response.status_code != 200:
                self.logger.error(f"{current_log_prefix}Failed to get user ID: {response.text}")
                return None
                
            user_id = response.json()["data"][0]["id"]
            
            # Then get the channel information including game
            channel_response = requests.get(
                f"https://api.twitch.tv/helix/channels?broadcaster_id={user_id}", 
                headers=headers
            )
            
            if channel_response.status_code != 200:
                self.logger.error(f"{current_log_prefix}Failed to get channel info: {channel_response.text}")
                return None
                
            channel_data = channel_response.json()["data"][0]
            game_name = channel_data.get("game_name", "")
            
            self.logger.info(f"{current_log_prefix}Found game for {username}: {game_name}")
            return game_name
            
        except Exception as e:
            self.logger.error(f"{current_log_prefix}Error getting game info: {e}")
            return None