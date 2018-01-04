import discord
import asyncio
import urllib.request
import requests
import time
from random import randint

client = discord.Client()
SEARCH_CACHE = []

current_milli_time = lambda: int(round(time.time() * 1000))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.content.startswith('!privacy'):
        await client.send_message(message.channel, '**DerpiBot Privacy Policy**\n1. DerpiBot will anonymously track search queries for the purpose of determining popular searches and images to cache in RAM. Never is your user ID, name, etc. stored in this process.\n2. DerpiBot will never store any user identifiers (such as usernames, user ids, etc) unless absolutely required, such as for user preset searches.')

    if message.content.startswith('!search '):
        search_start = current_milli_time()
        search_string = message.content.split(" ",1)[1].replace(" ", "+")
        cache_level = -1

        for entry in SEARCH_CACHE:
            if entry[0] == search_string:
                cache_level = 0
                random_entry = entry[randint(1,len(entry)-1)]
        
        if cache_level == -1:
            search_url = "https://derpibooru.org/search.json?q={}".format(search_string)
            r = requests.get(search_url)
            content = r.json()
            entry_count = len(content["search"])

            temp_search_cache = [search_string]
            for entry in content["search"]:
                t = {"tags":entry["tags"], "image":entry["image"]}
                temp_search_cache.append(t)
            SEARCH_CACHE.append(temp_search_cache)

            random_entry = content["search"][randint(0,entry_count-1)]

            cache_level = 2

        search_end = current_milli_time()

        embed = discord.Embed(color=discord.Color.green())
        embed.add_field(name="Tags", value=random_entry["tags"])
        if cache_level == 2:
            embed.add_field(name="Search Level", value="Derpibooru Server [SLOW]")
        elif cache_level == 0:
            embed.add_field(name="Search Level", value="RAM Search Cache [FAST]")
        else:
            embed.add_field(name="Search Level", value="Unknown")
        embed.add_field(name="Search Query Time", value=str(search_end-search_start) + "ms")
        embed.set_image(url="https:"+random_entry["image"])

        await client.send_message(message.channel, embed=embed)

token = ""
with open("token.txt") as m:
    token = m.read().strip()
client.run(token)