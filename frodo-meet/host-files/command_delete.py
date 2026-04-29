'''Frodo Meet - Delete Meeting Command
'''
from discord import Interaction

from common_bot_helper import ConfirmationViewDefault, RESPONSE_TIMEOUT

from frodo_meet_helper import show_meetings, find_meeting, remove_meeting
from common_views import MeetingSelectView
from frodo_meet_data import write_meetings, DATA_FILE_PATH

from meeting import Meeting


async def delete_meeting(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    target: str
) -> None:
    if not meetings:
        await interaction.response.send_message('There are no meetings to delete. 🧐')
        return
    
    # If no target arg was given, get meeting select.
    if not target:
        await interaction.response.send_message(
            f'Enter the title or index of the meeting you want to delete:\n'
            f'{show_meetings(('all',), meetings, None)}',
            view = MeetingSelectView(meetings, ids_to_names, on_select)
        )
        return
    
    # Get target meeting.
    target_meeting = find_meeting(meetings, target)
    if isinstance(target_meeting, str):
        await interaction.response.send_message(target_meeting)
        return
    
    # Confirmation.
    await interaction.response.send_message(
        content = build_confirmation_content(ids_to_names, target_meeting),
        view = build_confirmation_view(meetings, target_meeting)
    )


# ON MEETING SELECT

async def on_select(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    target_meeting: Meeting
) -> None:
    # Confirmation.
    await interaction.response.edit_message(
        content = build_confirmation_content(ids_to_names, target_meeting),
        view = build_confirmation_view(meetings, target_meeting)
    )


# CONFIRMATION

async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting,
    data_file_path: str,
    **_
) -> None:
    remove_error = remove_meeting(meetings, target_meeting)
    if remove_error:
        await interaction.response.edit_message(
            content = remove_error,
            view = None
        )
        return
    
    write_meetings(data_file_path, meetings)

    await interaction.response.edit_message(
        content = f'{target_meeting.get_title(True)} has been deleted! 💥',
        view = None
    )


async def on_cancel(
    interaction: Interaction,
    target_meeting: Meeting,
    **_
) -> None:
    await interaction.response.edit_message(
        content = f'{target_meeting.get_title(True)} was spared. 😇',
        view = None
    )

# CONFIRMATION ARGS

def build_confirmation_content(ids_to_names: dict[str: str], target_meeting: Meeting) -> str:
    return (
        'Target meeting:\n'
        f'{target_meeting.to_discord(full = True, ids_to_names = ids_to_names,)}\n\n'
        'Would you like to delete this meeting?'
    )

def build_confirmation_view(meetings: list[Meeting], target_meeting: Meeting) -> ConfirmationViewDefault:
    return ConfirmationViewDefault(
        on_confirm = on_confirm,
        on_cancel = on_cancel,
        timeout = RESPONSE_TIMEOUT,
        meetings = meetings,
        target_meeting = target_meeting,
        data_file_path = DATA_FILE_PATH
    )
