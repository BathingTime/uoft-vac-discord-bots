'''Frodo Meet

UofT Visual Arts Club exec team's Discord bot for easy meeting plan management.

Can create and manage meeting with Discord commands.
Also notifies meeting members when a meeting is about to start.
Stores and reads meeting data in meetings_data.json.

Driver file.
'''
# TODO: Show and toggle-active commands.
# TODO: Unique title.
# TODO: Time checking.
# TODO: Less data fetching.
# TODO: Update Summary.md.

from discord import Intents, Interaction, Guild, TextChannel
from discord.ext import commands

from asyncio import sleep

from common_bot_helper import read_json_file, chop_output

from frodo_meet_data import get_meetings, write_meetings, DATA_FILE_PATH
from meeting_time import MeetingTime

import command_show, command_create, command_delete, command_edit
from frodo_meet_background_tasks import notify_meetings, begin_meetings


# CONSTANTS

NOTIFY_CHANNEL_ID = 1491494362205392976

CHECK_INTERVAL_SECS = 60 # Seconds between each check for meetings to notify/begin.
NOTICE_TIME_SECS = 5 * 60 # Notify meetings that will begin in less than this number of minutes.


# LAUNCH

intents = Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents)
tree = bot.tree
command = tree.command

background_task = None

@bot.event
async def on_ready():
    global background_task

    await tree.sync()
    print('Logged in as {0.user}'.format(bot))

    if background_task is not None:
        print('Background task already exists.')
        return

    background_task = bot.loop.create_task(auto_notify_n_begin(
        bot.get_channel(NOTIFY_CHANNEL_ID),
        NOTICE_TIME_SECS
    ))


# COMMANDS

@command(
    name = 'show-meetings',
    description = 'Display recorded meeting plans.'
)
async def show_meetings(interaction: Interaction, filters: str = '') -> None:
    await command_show.show_meetings(
        get_meetings(read_json_file(DATA_FILE_PATH)),
        get_ids_to_names(interaction.guild),
        filters
    )

@command(
    name = 'create-meeting',
    description = 'Create a new meeting!'
)
async def create_meeting(interaction: Interaction) -> None:
    await command_create.create_meeting(
        interaction,
        get_meetings(read_json_file(DATA_FILE_PATH)),
        get_ids_to_names(interaction.guild)
    )

@command(
    name = 'delete-meeting',
    description = 'Delete an existing meeting.'
)
async def delete_meeting(interaction: Interaction, target: str = None) -> None:
    await command_delete.delete_meeting(
        interaction,
        get_meetings(read_json_file(DATA_FILE_PATH)),
        get_ids_to_names(interaction.guild),
        target
    )

@command(
    name = 'edit-meeting',
    description = 'Edit a property for an existing meeting.'
)
async def edit_meeting(interaction: Interaction, target: str = None) -> None:
    await command_edit.edit_meeting(
        interaction,
        get_meetings(read_json_file(DATA_FILE_PATH)),
        get_ids_to_names(interaction.guild),
        target
    )


# BACKGROUND TASKS

async def auto_notify_n_begin(notify_channel: TextChannel, notice_time_secs: int) -> None:
    '''
    Every specified interval:
    1. Check if there are any meetings that are about to start, given a timeframe.
    2. Check if there are any meetings that have begun (meetin time is past current time).
    If these are true, print the appropriate output(s) in the notify channel.

    Sample Usage inapplicable.
    '''
    # Loop as long as bot is online.
    while not bot.is_closed():
        # await notify_channel.send(f'Test: the current time is {MeetingTime.get_now().to_discord()}.')

        meetings = get_meetings(read_json_file(DATA_FILE_PATH))
        now = MeetingTime.get_now()

        # Check for any meetings to notify and get the output.
        notify_output = notify_meetings(meetings, now, notice_time_secs)
        # print('got notify output')

        # Check for any meetings to begin and get the output.
        begin_output = begin_meetings(meetings, now)
        # print('got begin output')

        # Meetings list may be modified, so update data file.
        write_meetings(DATA_FILE_PATH, meetings)

        # If there are meetings to notify, print it in the auto channel.
        if notify_output:
            for suboutput in chop_output(notify_output):
                await notify_channel.send(suboutput)
            print('Meetings have been notified!')
        
        else: print('No meetings to notify.')

        # If there are meetings that have begun, print it in the auto channel.
        if begin_output:
            for suboutput in chop_output(begin_output):
                await notify_channel.send(suboutput)
            print('Meetings have begun!')
        
        else: print('No meetings have begun.')

        # Sleep for the specified interval.
        await sleep(CHECK_INTERVAL_SECS)


# HELPER FUNCTIONS

def get_ids_to_names(guild: Guild) -> dict[str: str]:
    '''Return a dictionary of ID-name pairs for the server's roles and members.'''
    roles_dict = {str(role.id): role.name for role in guild.roles}
    members_dict = {str(member.id): member.display_name for member in guild.members}
    # print(roles_dict, members_dict)

    return roles_dict | members_dict


# THE CODE BODY BELOW CONTAINS SENSITIVE INFORMATION; KEEP COMPRESSED.
if __name__ == '__main__':
    from os import getcwd
    print(f'Current working directory: {getcwd()}')

    bot.run('MTM5MTIwNDQ3MjQwNzA2NDY4OA.GsICWF.64EdmwlT3BDEqV11ZZYaDuz03oyt548Ild3crQ')
