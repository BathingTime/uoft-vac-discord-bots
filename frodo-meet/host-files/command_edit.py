'''Frodo Meet - Edit Meeting Command
'''
from discord import Interaction, SelectOption
from discord.ui import View, Select

from copy import deepcopy

from common_bot_helper import get_response, ConfirmationViewDefault, RESPONSE_TIMEOUT, NULL_SELECT_VALUE

from frodo_meet_helper import get_meetings_to_discord, find_meeting, add_meeting, remove_meeting
from frodo_meet_discord_views import MeetingSelectView, RecurrenceSelectView
from frodo_meet_data import write_meetings, DATA_FILE_PATH

from meeting import Meeting,\
    ATTRIBUTE_TITLE,\
    ATTRIBUTE_TIME,\
    ATTRIBUTE_DESCRIPTION,\
    ATTRIBUTE_PARTICIPANTS,\
    ATTRIBUTE_RECURRENCE
from meeting_time import MeetingTime


async def edit_meeting(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    target: str
) -> None:
    if not meetings:
        await interaction.response.send_message('There are no meetings to edit. 🧐')
        return
    
    # STEP 1: If no target arg was given, display meetings and wait for target.
    if not target:
        await interaction.response.send_message(
            content = (
                f'Enter the title or index of the meeting you want to delete:\n'
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
    
    # STEP 2: Get property to edit.
    await interaction.response.send_message(
        content = build_on_meeting_select_content(target_meeting),
        view = EditPropertySelectView(meetings, ids_to_names, target_meeting)
    )


# ON MEETING SELECT

async def on_meeting_select(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    target_meeting: Meeting
) -> None:
    # STEP 2: Get property to edit.
    await interaction.response.edit_message(
        content = build_on_meeting_select_content(target_meeting),
        view = EditPropertySelectView(meetings, ids_to_names, target_meeting)
    )

def build_on_meeting_select_content(target_meeting: Meeting) -> str:
    return (
        f'You are editing {target_meeting.get_title(True)}.\n'
        'Which property would you like to edit?'
    )


# EDIT PROPERTY SELECT

class EditPropertySelectView(View):
    def __init__(self,
        meetings: list[Meeting],
        ids_to_names: dict[str: str],
        target_meeting: Meeting
    ) -> None:
        super().__init__(timeout = RESPONSE_TIMEOUT)
        self.add_item(EditPropertySlect(meetings, ids_to_names, target_meeting))

class EditPropertySlect(Select):
    _meetings: list[Meeting]
    _ids_to_names: dict[str: str]
    _target_meeting: Meeting

    def __init__(self, meetings: list[Meeting],
        ids_to_names: dict[str: str],
        target_meeting: Meeting
    ) -> None:
        self._meetings = meetings
        self._ids_to_names = ids_to_names
        self._target_meeting = target_meeting

        super().__init__(
            placeholder = 'Select property…',
            options = [
                SelectOption(label = ATTRIBUTE_TITLE.capitalize(), value = ATTRIBUTE_TITLE),
                SelectOption(label = ATTRIBUTE_TIME.capitalize(), value = ATTRIBUTE_TIME),
                SelectOption(label = ATTRIBUTE_DESCRIPTION.capitalize(), value = ATTRIBUTE_DESCRIPTION),
                SelectOption(label = ATTRIBUTE_PARTICIPANTS.capitalize(), value = ATTRIBUTE_PARTICIPANTS),
                SelectOption(label = ATTRIBUTE_RECURRENCE.capitalize(), value = ATTRIBUTE_RECURRENCE)
            ]
        )
    
    async def callback(self, interaction: Interaction) -> None:
        target_property = self.values[0]

        meetings = self._meetings
        ids_to_names = self._ids_to_names
        target_meeting = self._target_meeting

        updated_meeting = deepcopy(target_meeting)

        # STEP 3: Get new value.
        # If editing recurrence, go to recurrence select view.
        if target_property == ATTRIBUTE_RECURRENCE:
            await interaction.response.edit_message(
                content = (
                    f'You are editing the __{target_property}__ of {target_meeting.get_title(True)}.\n'
                    'Please select the new recurrence.\n'
                    'For a one-time meeting, select *Normal (one-time)*.'
                ),
                view = RecurrenceSelectView(
                    on_select = on_recurrence_select,
                    meetings = meetings,
                    ids_to_names = ids_to_names,
                    target_meeting = target_meeting,
                    updated_meeting = updated_meeting
                )
            )
            return

        # Otherwise, await new value as a response.
        await interaction.response.edit_message(
            content = (
                f'You are editing the __{target_property}__ of {target_meeting.get_title(True)}.\n'
                'Please enter the new value.'
            ),
            view = None
        )
        
        new_value_message = await get_response(interaction, RESPONSE_TIMEOUT)

        # If editing time:
        if target_property == ATTRIBUTE_TIME:
            new_value = MeetingTime.from_input(new_value_message.content)

            if isinstance(new_value, str):
                await interaction.followup.send(new_value)
                return
            
            updated_meeting.set_time(new_value)
            updated_meeting.set_soon()
        
        # If editing participants:
        elif target_property == ATTRIBUTE_PARTICIPANTS:
            new_value = (
                [f"<@&{role.id}>" for role in new_value_message.role_mentions] +
                [f"<@{user.id}>" for user in new_value_message.mentions]
            )

            updated_meeting.set_participants(new_value)
        
        # Otherwise, editing title/description:
        else:
            new_value = new_value_message.content

            if target_property == ATTRIBUTE_TITLE:
                updated_meeting.set_title(new_value)
            else:
                updated_meeting.set_description(new_value)

        # STEP 4: Confirmation.
        await interaction.followup.send(
            content = build_confirmation_content(
                ids_to_names,
                updated_meeting
            ),
            view = build_confirmation_view(
                meetings,
                target_meeting,
                updated_meeting
            )
        )


# ON RECURRENCE SELECT

async def on_recurrence_select(
    interaction: Interaction,
    recurrence: str,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    target_meeting: Meeting,
    updated_meeting: Meeting,
    **_
) -> None:
    # Set recurrence.
    updated_meeting.set_recurrence(recurrence if recurrence != NULL_SELECT_VALUE else '')

    # STEP 4: Confirmation.
    await interaction.response.edit_message(
        content = build_confirmation_content(
            ids_to_names,
            updated_meeting
        ),
        view = build_confirmation_view(
            meetings,
            target_meeting,
            updated_meeting
        )
    )


# CONFIRMATION

async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting,
    updated_meeting: Meeting,
    data_file_path: str,
    **_
) -> None:
    # Remove original meeting.
    remove_error = remove_meeting(meetings, target_meeting)
    if remove_error:
        await interaction.response.edit_message(
            content = f'{remove_error}\nNothing to edit.',
            view = None
        )
        return
    
    # Add updated meeting.
    add_meeting(meetings, updated_meeting)

    write_meetings(data_file_path, meetings)

    await interaction.response.edit_message(
        content = f'Changes to {target_meeting.get_title(True)} have been saved! ✨',
        view = None
    )

async def on_cancel(
    interaction: Interaction,
    target_meeting: Meeting,
    **_
) -> None:
    await interaction.response.edit_message(
        content = f'Changes for {target_meeting.get_title(True)} have been discarded! 🗑️',
        view = None
    )


def build_confirmation_content(
    ids_to_names: dict[str: str],
    updated_meeting: Meeting
) -> str:
    return (
        'Updated meeting:\n'
        f'{updated_meeting.to_discord(full = True, ids_to_names = ids_to_names,)}\n\n'
        'Would you like to save these changes?'
    )

def build_confirmation_view(
    meetings: list[Meeting],
    target_meeting: Meeting,
    updated_meeting: Meeting
) -> ConfirmationViewDefault:
    return ConfirmationViewDefault(
        on_confirm = on_confirm,
        on_cancel = on_cancel,
        timeout = RESPONSE_TIMEOUT,
        meetings = meetings,
        target_meeting = target_meeting,
        updated_meeting = updated_meeting,
        data_file_path = DATA_FILE_PATH
    )
