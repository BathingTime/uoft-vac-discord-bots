'''Frodo Meet - Create Meeting Command
'''
from discord import Interaction, SelectOption
from discord.ui import Modal, TextInput, View, Select

from common_bot_helper import get_response, ConfirmationViewDefault, RESPONSE_TIMEOUT, NULL_SELECT_VALUE

from frodo_meet_helper import add_meeting
from frodo_meet_data import write_meetings, DATA_FILE_PATH

from meeting import Meeting, DAILY_LABEL, WEEKLY_LABEL, YEARLY_LABEL
from meeting_time import MeetingTime


async def create_meeting(interaction: Interaction, meetings: list[Meeting], ids_to_names: dict[str: str]) -> None:
    await interaction.response.send_modal(CreateInputModal(
        meetings,
        ids_to_names
    ))


# INITIAL MODAL

class CreateInputModal(Modal, title = 'Create Meeting'):
    _meetings: list[Meeting]
    _ids_to_names: dict[str: str]

    # STEP 1: Get title, time, and description.
    _title_input = TextInput(label='Title')
    _time_input = TextInput(label='Time')
    _description_input = TextInput(label='Description', required=False)

    def __init__(self, meetings: list[Meeting], ids_to_names: dict[str: str]) -> None:
        super().__init__()
        self._meetings = meetings
        self._ids_to_names = ids_to_names

    async def on_submit(self, interaction: Interaction) -> None:

        # If time input was invalid, print error message.
        time = MeetingTime.from_input(self._time_input.value)
        if isinstance(time, str):
            await interaction.response.send_message(time)
            return
        
        # STEP 2: Get participants.
        await interaction.response.send_message(
            'Enter **pings** for all participants you want to add for this meeting, separated by spaces. (roles or users)\n'
            'E.g. @Lead @Frodo Meet\n'
            'Or type any non-ping message to skip.'
        )

        participants_message = await get_response(interaction, RESPONSE_TIMEOUT)
        
        participants = (
            [f"<@&{role.id}>" for role in participants_message.role_mentions] +
            [f"<@{user.id}>" for user in participants_message.mentions]
        )

        # Initialise meeting object.
        new_meeting = Meeting(
            self._title_input.value,
            time,
            self._description_input.value,
            participants,
        )

        # STEP 3: Get recurrence option.
        await interaction.followup.send(
            'Would you like to make this a recurring meeting?\n'
            'For a one-time meeting, select __Normal (one-time)__.',
            view = RecurrenceSelectView(self._meetings, self._ids_to_names, new_meeting)
        )


# RECURRENCE SELECT

class RecurrenceSelectView(View):
    def __init__(self,
        meetings: list[Meeting],
        ids_to_names: dict[str: str],
        new_meeting: Meeting
    ) -> None:
        super().__init__(timeout = RESPONSE_TIMEOUT)
        self.add_item(RecurrenceSelect(meetings, ids_to_names, new_meeting))

class RecurrenceSelect(Select):
    _meetings: list[Meeting]
    _ids_to_names: dict[str: str]
    _new_meeting: Meeting

    def __init__(self,
        meetings: list[Meeting],
        ids_to_names: dict[str: str],
        new_meeting: Meeting
    ) -> None:
        self._meetings = meetings
        self._ids_to_names = ids_to_names
        self._new_meeting = new_meeting

        super().__init__(
            placeholder = 'Select recurrence option…',
            options = [
                SelectOption(label = 'Normal (one-time)', value = NULL_SELECT_VALUE),
                SelectOption(label = 'Daily', value = DAILY_LABEL),
                SelectOption(label = 'Weekly', value = WEEKLY_LABEL),
                SelectOption(label = 'Yearly', value = YEARLY_LABEL),
            ]
        )
    
    async def callback(self, interaction: Interaction) -> None:
        recurring_label = self.values[0]

        meetings = self._meetings
        ids_to_names = self._ids_to_names
        new_meeting = self._new_meeting

        # If a recurring label was selected, add it.
        if recurring_label != NULL_SELECT_VALUE:
            new_meeting.add_label(recurring_label)

        # STEP 4: Confirmation.
        await interaction.response.edit_message(
            content = (
                'New meeting:\n'
                f'{new_meeting.to_discord(full = True, ids_to_names = ids_to_names,)}\n\n'
                'Would you like to create this meeting?'
            ),
            view = ConfirmationViewDefault(
                on_confirm = on_confirm,
                on_cancel = on_cancel,
                timeout = RESPONSE_TIMEOUT,
                meetings = meetings,
                ids_to_names = ids_to_names,
                new_meeting = new_meeting,
                data_file_path = DATA_FILE_PATH
            )
        )


# CONFIRMATION

async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    new_meeting: Meeting,
    data_file_path: str,
    **_
) -> None:
    add_meeting(meetings, new_meeting)
    write_meetings(data_file_path, meetings)

    await interaction.message.edit(
        content = f'{new_meeting.get_title(True)} has been created! ✨',
        view = None
    )

async def on_cancel(
    interaction: Interaction,
    new_meeting: Meeting,
    **_
) -> None:
    await interaction.message.edit(
        content = f'{new_meeting.get_title(True)} has been discarded! 🗑️',
        view = None
    )
