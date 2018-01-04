import discord
import asyncio
import urllib.request
import requests
import time
from random import randint

# Initialize Discord.py
client = discord.Client()

# Our empty search cache variable
SEARCH_CACHE = []
# A tiny function to get the current time in milliseconds
current_milli_time = lambda: int(round(time.time() * 1000))

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

    # Search command
    if message.content.startswith('!search '):
        # Start search timer
        search_start = current_milli_time()
        # Extract search query
        search_string = message.content.split(" ",1)[1].replace(" ", "+")
        # Set cache level to -1 for unknown
        cache_level = -1

        # Search our RAM cache first
        for entry in SEARCH_CACHE:
            if entry[0] == search_string:
                # If the search term is found in the cache, set cache level to 0 (completely RAM based) and set our entry to a random one
                cache_level = 0
                random_entry = entry[randint(1,len(entry)-1)]
        
        if cache_level == -1:
            # Build and get search from Derpibooru's API
            search_url = "https://derpibooru.org/search.json?q={}".format(search_string)
            r = requests.get(search_url)
            content = r.json()
            entry_count = len(content["search"])

            # Add this search to the RAM cache for later use
            temp_search_cache = [search_string]
            for entry in content["search"]:
                t = {"tags":entry["tags"], "image":entry["image"]}
                temp_search_cache.append(t)
            SEARCH_CACHE.append(temp_search_cache)

            # Select a random entry from the query to be our lucky image
            random_entry = content["search"][randint(0,entry_count-1)]

            # Set cache level to 2, for Derpibooru Server
            cache_level = 2

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
        embed.add_field(name="Search Query Time", value=str(search_end-search_start) + "ms")
        embed.set_image(url="https:"+random_entry["image"])

        # Send our embed
        await client.send_message(message.channel, embed=embed)

# Read and use the bot token
token = ""
with open("token.txt") as m:
    token = m.read().strip()
client.run(token)