import discord
import asyncio
import urllib.request
import requests
import time
from random import randint

# Initialize Discord.py
client = discord.Client()

# Read Derpibooru key
DERPIBOORU_KEY = ""
with open("derpikey.txt") as m:
    DERPIBOORU_KEY = m.read().strip()

# Our empty search cache variable
# The format is ["search string", {"tags":"image tags", "image":"image url"}, {"tags":"image tags", "image":"image url"}, ...]
SEARCH_CACHE = {}
IMAGE_CACHE = {}
# A tiny function to get the current time in milliseconds
current_milli_time = lambda: round(time.time() * 1000, 3)

@client.event
async def on_ready():
    # We are now logged in, for now we just print some basic info
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    # Our Privacy Policy
    if message.content.startswith('!privacy'):
        await client.send_message(message.channel, '**DerpiBot Privacy Policy**\n1. DerpiBot will anonymously track search queries for the purpose of determining popular searches and images to cache in RAM. Never is your user ID, name, etc. stored in this process.\n2. DerpiBot will never store any user identifiers (such as usernames, user ids, etc) unless absolutely required, such as for user preset searches.')

    if message.content == "!caches":
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="[RAM] Image Cache", value=str(len(IMAGE_CACHE)))
        embed.add_field(name="[RAM] Search Cache", value=str(len(SEARCH_CACHE)))
        await client.send_message(message.channel, embed=embed)

    if message.content == "!bench":
        average_time = 0
        test = "!search pt,safe,solo"
        for i in range(1000000):
            # Start search timer
            search_start = current_milli_time()
            # Extract search query
            search_string = test[8:].replace(" ", "+")
            # Set cache level to -1 for unknown
            cache_level = -1

            # Search our RAM cache first
            try:
                random_entry = IMAGE_CACHE[SEARCH_CACHE[search_string][randint(0,len(SEARCH_CACHE[search_string])-1)]]
                cache_level = 0
            except KeyError:
                pass

            search_end = current_milli_time()

            average_time += search_end-search_start

        await client.send_message(message.channel, str((average_time/1000000)*1000) + "μs")

    # Search command
    if message.content.startswith('!search '):
        # Start search timer
        search_start = current_milli_time()
        # Extract search query
        search_string = message.content[8:].replace(" ", "+")
        # Set cache level to -1 for unknown
        cache_level = -1

        # Search our RAM cache first
        try:
            random_entry = IMAGE_CACHE[SEARCH_CACHE[search_string][randint(0,len(SEARCH_CACHE[search_string])-1)]]
            cache_level = 0
        except KeyError:
            # Build and get search from Derpibooru's API
            search_url = "https://derpibooru.org/search.json?q={}&key={}".format(search_string, DERPIBOORU_KEY)
            r = requests.get(search_url)
            content = r.json()
            entry_count = len(content["search"])

            # If our array of images is empty, Derpibooru didn't send us any results. Error out.
            if len(content["search"]) == 0:
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name="Error!", value="No results were returned.")
                await client.send_message(message.channel, embed=embed)
                return

            # Add this search to the RAM cache for later use
            temp_search_cache = []
            for entry in content["search"]:
                temp_search_cache.append(int(entry["id"]))
                if entry["id"] not in IMAGE_CACHE:
                    t = {"tags":entry["tags"], "image":entry["image"]}
                    IMAGE_CACHE[int(entry["id"])] = t
            SEARCH_CACHE[search_string] = temp_search_cache

            # Set cache level to 2, for Derpibooru Server
            cache_level = 2

            # Select a random entry from the query to be our lucky image
            random_entry = content["search"][randint(0,len(content["search"])-1)]

        # Done searching, end the timer
        search_end = current_milli_time()

        # Build our embed
        embed = discord.Embed(color=discord.Color.green())
        embed.add_field(name="Tags", value=random_entry["tags"])
        # Set cache level label appropriately
        if cache_level == 2:
            embed.add_field(name="Search Level", value="Derpibooru Server [SLOW]")
        elif cache_level == 0:
            embed.add_field(name="Search Level", value="RAM Search Cache [FAST]")
        else:
            embed.add_field(name="Search Level", value="Unknown")
        search_time = search_end-search_start
        if search_time < 0.9:
            embed.add_field(name="Search Query Time", value=str(search_time*1000) + "μs")
        else:
            embed.add_field(name="Search Query Time", value=str(search_time) + "ms")
        embed.set_image(url="https:"+random_entry["image"])

        # Send our embed
        await client.send_message(message.channel, embed=embed)

# Read and use the bot token
token = ""
with open("token.txt") as m:
    token = m.read().strip()
client.run(token)