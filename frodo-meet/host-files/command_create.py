'''Create Meeting Command
'''
from discord import Interaction, SelectOption, ButtonStyle
from discord.ui import Modal, TextInput, View, Select, button, Button

from common_bot_helper import await_message_default, RESPONSE_TIMEOUT, NULL_OPTION_VALUE

from frodo_meet_helper import add_meeting
from frodo_meet_data import write_meetings, DATA_FILE_PATH

from meeting import Meeting, DAILY_LABEL, WEEKLY_LABEL, YEARLY_LABEL
from meeting_time import MeetingTime


async def create_meeting(interaction: Interaction, meetings: list[Meeting], ids_to_names: dict[str: str]) -> None:
    await interaction.response.defer()

    await interaction.response.send_modal(CreateInputModal(
        meetings,
        ids_to_names
    ))


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
        await interaction.response.defer()

        # If time input was invalid, send error message.
        time = MeetingTime.from_input(self._time_input.value)
        if isinstance(time, str):
            await interaction.followup.send(time)
            return
        
        # STEP 2: Get participants on next message.
        await interaction.followup.send(
            'Enter **pings** for all participants you want to add for this meeting, separated by spaces. (roles or users)\n'
            'E.g. @Lead @Frodo Meet\n'
            'Or type any non-ping message to skip.'
        )
        try:
            participants_message = await await_message_default(interaction, RESPONSE_TIMEOUT)
        except TimeoutError:
            await interaction.followup.send('Response timeout. ⚠️')
            return
        
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

        # STEP 3: Get optional recurring option.
        await interaction.followup.send(
            'Would you like to make this a recurrence meeting?\n'
            'For a one-time meeting, select *One-time*.',
            view = RecurringOptionsView(self._meetings, self._ids_to_names, new_meeting)
        )


class RecurringOptionsView(View):
    _meetings: list[Meeting]
    _ids_to_names: dict[str: str]
    _new_meeting: Meeting

    def __init__(self, meetings: list[Meeting], ids_to_names: dict[str: str], new_meeting: Meeting) -> None:
        super().__init__(timeout = RESPONSE_TIMEOUT)

        self._meetings = meetings
        self._ids_to_names = ids_to_names
        self._new_meeting = new_meeting

        self.add_item(RecurringOptionSelection(self))

class RecurringOptionSelection(Select):
    _parent_view: RecurringOptionsView

    def __init__(self, parent_view: RecurringOptionsView) -> None:
        super().__init__(
            placeholder = "Select…",
            options = [
                SelectOption(label = "One-time", value = NULL_OPTION_VALUE),
                SelectOption(label = "Daily", value = DAILY_LABEL),
                SelectOption(label = "Weekly", value = WEEKLY_LABEL),
                SelectOption(label = "Yearly", value = YEARLY_LABEL),
            ]
        )

        self._parent_view = parent_view
    
    async def callback(self, interaction: Interaction) -> None:
        recurring_label = self.values[0]

        parent_view = self._parent_view
        new_meeting = parent_view._new_meeting

        # If a recurring label was selected, add it.
        if recurring_label != NULL_OPTION_VALUE:
            new_meeting.add_label(recurring_label)

        # STEP 4: Get confirmation to create meeting.
        await interaction.followup.send(
            content = (
                'New meeting:\n'
                f'{new_meeting.to_discord(full = True, ids_to_names = parent_view._ids_to_names,)}\n\n'
                'Would you like to create this meeting?'
            ),
            view = ConfirmationView(parent_view._meetings, new_meeting)
        )


class ConfirmationView(View):
    _meetings: list[Meeting]
    _new_meeting: Meeting

    def __init__(self, meetings: list[Meeting], new_meeting: Meeting) -> None:
        super().__init__(timeout = RESPONSE_TIMEOUT)
        self._meetings = meetings
        self._new_meeting = new_meeting

    # CONFIRM
    @button(label = 'Yes', style = ButtonStyle.green)
    async def confirm(self, interaction: Interaction, _: Button):
        meetings, new_meeting = self._meetings, self._new_meeting

        # Add meeting to meetings list and update data file.
        add_meeting(meetings, new_meeting)
        write_meetings(DATA_FILE_PATH, meetings)

        await interaction.followup.send(
            content = f'{new_meeting.get_title(True)} has been created! ✨',
            view = None
        )

    # CANCEL
    @button(label = 'No', style = ButtonStyle.red)
    async def cancel(self, interaction: Interaction, _: Button):
        await interaction.followup.send(
            content = f'{self._new_meeting.get_title(True)} has been discarded. 🗑️',
            view = None
        )
