'''Frodo Meet - Toggle Active Command
'''
from discord import Interaction

from common_bot_helper import ConfirmationViewDefault

from frodo_meet_helper import get_meetings_to_discord, find_meeting, remove_meeting
from frodo_meet_discord_views import MeetingSelectView
from frodo_meet_data import write_meetings, DATA_FILE_PATH

from meeting import Meeting


async def delete_meeting(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    target: str
) -> None:
    if not meetings:
        await interaction.response.send_message('There are no meetings to toggle. 🧐')
        return
    
    # If no target arg was given, get meeting select.
    if not target:
        await interaction.response.send_message(
            content = (
                f'Enter the title or index of the meeting whose active status you want to toggle:\n'
                f'{get_meetings_to_discord(('all',), meetings, None)}'
            ),
            view = MeetingSelectView(
                on_meeting_select,
                meetings,
                ids_to_names
            )
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

async def on_meeting_select(
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
    title = target_meeting.get_title(True)

    if not target_meeting in meetings:
        interaction.response.edit_message(
            content = (
                f'It seems {title} does not exist at the time of confirmation. 🧐\n'
                'No status to toggle.'
            ),
            view = None
        )
        return
    
    new_active = target_meeting.toggle_active()
    
    write_meetings(data_file_path, meetings)

    content_final = (
        f'{title} has been activated! 🔊' if new_active else
        f'{title} has been deactivated! 🔇'
    )

    await interaction.response.edit_message(
        content = content_final,
        view = None
    )

async def on_cancel(
    interaction: Interaction,
    target_meeting: Meeting,
    **_
) -> None:
    title = target_meeting.get_title(True)

    content_final = (
        f'{title} will remain active! 🔊' if target_meeting.get_active() else
        f'{title} will remain inactive! 🔇'
    )

    await interaction.response.edit_message(
        content = content_final,
        view = None
    )


def build_confirmation_content(target_meeting: Meeting) -> str:
    title = target_meeting.get_title(True)

    if target_meeting.get_active():
        return (
            f'{title} is currently __active__.\n'
            f'Would you like to deactivate {title}? (Will not notify)'
        )
    
    return (
        f'{title} is currently __inactive__.\n'
        f'Would you like to activate {title}? (Will notify)'
    )

def build_confirmation_view(meetings: list[Meeting], target_meeting: Meeting) -> ConfirmationViewDefault:
    return ConfirmationViewDefault(
        on_confirm = on_confirm,
        on_cancel = on_cancel,
        meetings = meetings,
        target_meeting = target_meeting,
        data_file_path = DATA_FILE_PATH
    )
