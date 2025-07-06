'''Frodo Meet
Last edited: Jul 5, 25

Uoft Visual Arts Club exec team's Discord bot for easy meeting plan management.

Can add, cancel, and edit meeting plans with Discord commands.
Meeting plan information includes: title, description, time (date + hour), and members.
Also notifies meeting members when a meeting is about to take place.

Not for public use.
'''

import discord
from discord.ext import commands
from asyncio import sleep
from time import strftime

# Constants:
...


intents = discord.Intents.all()
client = commands.Bot(command_prefix = '.', intents = intents)

# When the bot goes online.
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

    # Connect all auto functions.
    client.loop.create_task(auto_func_eg)


# Command functions: functions that fire when a Discord user types in the command name.
# The function name is the command name.
# E.g. If the function name is command_func_eg, then the user would type ".command_func_eg …"
@client.command(pass_context = True)
async def command_func_eg(ctx, *args) -> None:
    ...

...


# Auto functions: functions that fire when the bot goes online.
async def auto_func_eg() -> None:

    # Begin only when the bot is online.
    await client.wait_until_ready()

    # Program loop; keep running unless the bot goes offline.
    while not client.is_closed():
        ...


# Activate bot.
# THE CODE BODY BELOW CONTAINS SENSITIVE INFORMATION; KEEP COMPRESSED.
if __name__ == '__main__':
    client.run('MTM5MTIwNDQ3MjQwNzA2NDY4OA.GsICWF.64EdmwlT3BDEqV11ZZYaDuz03oyt548Ild3crQ')