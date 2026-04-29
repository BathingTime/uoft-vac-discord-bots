'''Frodo Meet - Edit Meeting Command
'''
from discord import Interaction, SelectOption
from discord.ui import View, Select

from copy import deepcopy

from common_bot_helper import get_response, ConfirmationViewDefault, RESPONSE_TIMEOUT

from frodo_meet_helper import show_meetings, find_meeting, add_meeting, remove_meeting
from common_views import MeetingSelectView
from frodo_meet_data import write_meetings, DATA_FILE_PATH,\
    ATTRIBUTE_TITLE,\
    ATTRIBUTE_TIME,\
    ATTRIBUTE_DESCRIPTION,\
    ATTRIBUTE_PARTICIPANTS

from meeting import Meeting
from meeting_time import MeetingTime

EDIT_PROPERTY_SELECT_MESSAGE_CONTENT = 'Which property would you like to edit?'


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
    
    # STEP 2: Get property to edit.
    await interaction.response.send_message(
        content = EDIT_PROPERTY_SELECT_MESSAGE_CONTENT,
        view = EditPropertySelectView(meetings, ids_to_names, target_meeting)
    )


# ON MEETING SELECT

async def on_select(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    target_meeting: Meeting
) -> None:
    # STEP 2: Get property to edit.
    await interaction.response.edit_message(
        content = EDIT_PROPERTY_SELECT_MESSAGE_CONTENT,
        view = EditPropertySelectView(meetings, ids_to_names, target_meeting)
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
                SelectOption(label = 'Recurrence', value = 'recurrence')
            ]
        )
    
    async def callback(self, interaction: Interaction) -> None:
        target_property = self.values[0]

        meetings = self._meetings
        ids_to_names = self._ids_to_names
        target_meeting = self._target_meeting

        await interaction.response.edit_message(
            content = (
                f'You are editing the __{target_property}__ of {target_meeting.get_title(True)}.\n'
                'Please enter the new value.'
            ),
            view = None
        )

        # STEP 3: Get new value.
        new_value_message = await get_response(interaction, RESPONSE_TIMEOUT)

        updated_meeting = deepcopy(target_meeting)

        # If editing time:
        if target_property == ATTRIBUTE_TIME:
            new_value = MeetingTime.from_input(new_value_message.content)

            if isinstance(new_value, str):
                await interaction.followup.send(new_value)
                return
            
            updated_meeting.set_time(new_value)
        
        # If editing participants:
        elif target_property == ATTRIBUTE_PARTICIPANTS:
            new_value = (
                [f"<@&{role.id}>" for role in new_value_message.role_mentions] +
                [f"<@{user.id}>" for user in new_value_message.mentions]
            )

            updated_meeting.set_participants(new_value)
        
        # If editing recurrence:
        elif target_property == 'recurrence':
            ...
        
        # Otherwise, editing title/description:
        else:
            new_value = new_value_message.content

            if target_property == ATTRIBUTE_TITLE:
                updated_meeting.set_title(new_value)
            else:
                updated_meeting.set_description(new_value)

        # STEP 4: Confirmation.
        await interaction.followup.send(
            content = (
                'Updated meeting:\n'
                f'{updated_meeting.to_discord(full = True, ids_to_names = ids_to_names,)}\n\n'
                'Would you like to save these changes?'
            ),
            view = ConfirmationViewDefault(
                on_confirm = on_confirm,
                on_cancel = on_cancel,
                timeout = RESPONSE_TIMEOUT,
                meetings = meetings,
                ids_to_names = ids_to_names,
                target_meeting = target_meeting,
                updated_meeting = updated_meeting,
                data_file_path = DATA_FILE_PATH
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
    remove_error = remove_meeting(meetings, target_meeting)
    if remove_error:
        await interaction.response.edit_message(
            content = remove_error,
            view = None
        )
        return
    
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
