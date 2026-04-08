'''Frodo Meet
Author: Sunny Lin
Editors: 
Last modified: Apr 7, 26

Uoft Visual Arts Club exec team's Discord bot for easy meeting plan management.

Can add, cancel, & edit meeting plans with Discord commands.
Also notifies meeting members when a meeting is about to start.
Stores and reads meeting data in meeting_entries.json.

Frameworks & drivers file.

Not for public use.
'''
# TODO: add, cancel, edit functions.
# TODO: Check + notify auto function.

# Get working directory:
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

from discord import Intents, Interaction
from discord.ext import commands

from asyncio import sleep

from common_bot_helper import read_json_file

from constants import DATA_FILE_PATH
import bot_commands
from data_access import get_meetings
from meeting_time import MeetingTime

from add_input_modal import AddInputModal


# CONSTANTS:
NOTIFY_CHANNEL_ID = ... # TODO: Channel ID for the meeting notification channel.

CHECK_INTERVAL = 60 # Seconds between each check for upcoming meetings.
NOTICE_TIME = 5 * 60 # Notify meetings that will begin in less than this number of seconds.
WORD_LIMIT = 2000 # Word limit for Discord messages; might vary, but this is a safe value.


intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print('Logged in as {0.user}'.format(bot))
    # bot.loop.create_task(check_and_notify())


# COMMAND FUNCTIONS:

@bot.command(pass_context = True)
async def show(ctx, *args) -> None:
    await ctx.send(bot_commands.show(
        args,
        get_meetings(read_json_file(DATA_FILE_PATH)),
        MeetingTime.get_now(),
    ))

@bot.tree.command(name='add', description='Create a new meeting!')
async def add(interaction: Interaction) -> None:
    await interaction.response.send_modal(AddInputModal(
        get_meetings(read_json_file(DATA_FILE_PATH))
    ))


# AUTO FUNCTIONS:

async def check_and_notify() -> None:
    await bot.wait_until_ready()
    while not bot.is_closed():
        ...


# THE CODE BODY BELOW CONTAINS SENSITIVE INFORMATION; KEEP COMPRESSED.
if __name__ == '__main__':
    from os import getcwd
    print(f'Current working directory: {getcwd()}')

    bot.run('MTM5MTIwNDQ3MjQwNzA2NDY4OA.GsICWF.64EdmwlT3BDEqV11ZZYaDuz03oyt548Ild3crQ')
