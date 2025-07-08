'''Frodo Meet
Author: Sunny Lin
Editor(s):
Last edited: Jul 6, 25

Uoft Visual Arts Club exec team's Discord bot for easy meeting plan management.

Can add, cancel, & edit meeting plans with Discord commands.
Meeting plan information includes: title, details, time (date + hour & minute), & participants.
Also notifies meeting members when a meeting is about to take place.

Uses helper functions from common_bot_helper.py & frodo_meet_helper.py.
Stores & reads meeting plan data from meeting_entries.txt.

Not for public use.
'''
# TODO: Primary command functions - show, add, cancel, edit.
# TODO: Check + notify auto function.

from discord import Intents
from discord.ext import commands

from asyncio import sleep
from time import strftime

import common_bot_helper
import frodo_meet_helper

# Constants:
WORD_LIMIT = 2000 # Word limit for Discord messages; might vary, but this is a safe value.
CHANNEL_ID = ... # TODO: Channel ID for the meeting notification channel.
CHECK_INTERVAL = 60 # Seconds between each check for upcoming meetings.

ENTRIES_FILE_PATH = 'meeting-entries.txt'


client = commands.Bot(command_prefix = '.', intents = Intents.all())

# Bot goes online event.
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

    # Connect all auto functions.
    client.loop.create_task(auto_func_eg)


# Command functions:
@client.command(pass_context = True)
async def show(ctx, *args) -> None:
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