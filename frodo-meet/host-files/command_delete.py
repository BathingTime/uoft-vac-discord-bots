'''Delete Meeting Command
'''
from discord import Interaction

from common_bot_helper import await_message_default, ConfirmationViewDefault, RESPONSE_TIMEOUT

from frodo_meet_helper import find_meeting, show_meetings
from frodo_meet_data import write_meetings, DATA_FILE_PATH

from meeting import Meeting


async def delete_meeting(interaction: Interaction, target: str, meetings: list[Meeting], ids_to_names: dict[str: str]) -> None:
    await interaction.response.defer()

    if not meetings:
        await interaction.followup.send('There are no meetings to delete. 🧐')
        return
    
    # If no target arg was given, display meetings and wait for target.
    if not target:
        await interaction.followup.send(
            f'Enter the title or index of the meeting you want to delete:\n'
            f'{show_meetings(('all',), meetings, None)}'
        )
        try:
            target_message = await await_message_default(interaction, RESPONSE_TIMEOUT)
        except TimeoutError:
            await interaction.followup.send('Response timeout. ⚠️')
            return
        
        target = target_message.content
    
    # Get target meeting.
    target_meeting = find_meeting(meetings, target)

    # If no meeting could be found, send error message.
    if isinstance(target_meeting, str):
        await interaction.followup.send(target_meeting)
        return
    
    # Otherwise, target meeting has been found.
    # Confirmation.
    await interaction.followup.send(
        content = (
            'Target meeting:\n'
            f'{target_meeting.to_discord(full = True, ids_to_names = ids_to_names,)}\n\n'
            'Would you like to delete this meeting?'
        ),
        view = ConfirmationViewDefault(
            on_confirm = on_confirm,
            on_cancel = on_cancel,
            response_timeout = RESPONSE_TIMEOUT,
            meetings = meetings,
            target_meeting = target_meeting,
            data_file_path = DATA_FILE_PATH
        )
    )


async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting,
    data_file_path: str,
    **_
) -> None:
    # If meeting is no longer in meetings list, print a message.
    # Possible if a meeting began before confirming.
    if not target_meeting in meetings:
        await interaction.message.edit(content =
            f'It seems {target_meeting.get_title(True)} does not exist at the time of confirmation; nothing to delete. 🧐',
            view = None
        )

    meetings.remove(target_meeting)
    write_meetings(data_file_path, meetings)

    await interaction.message.edit(content =
        f'{target_meeting.get_title(True)} has been deleted! 💥',
        view = None
    )

async def on_cancel(
    interaction: Interaction,
    target_meeting: Meeting,
    **_
) -> None:
    await interaction.message.edit(content =
        f'{target_meeting.get_title(True)} was spared. 😇',
        view = None
    )
