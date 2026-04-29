'''Frodo Meet - Common Views
'''
from discord import Interaction, SelectOption
from discord.ui import View, Select

from common_bot_helper import RESPONSE_TIMEOUT, MAX_SELECTS

from frodo_meet_helper import find_meeting

from meeting import Meeting


# MEETING SELECT

class MeetingSelectView(View):
    def __init__(self,
        meetings: list[Meeting],
        ids_to_names: dict[str: str],
        on_select: callable
    ) -> None:
        super().__init__(timeout = RESPONSE_TIMEOUT)
        self.add_item(MeetingSelect(meetings, ids_to_names, on_select))
    
class MeetingSelect(Select):
    def __init__(self,
        meetings: list[Meeting],
        ids_to_names: dict[str: str],
        on_select: callable
    ) -> None:
        self._meetings = meetings
        self._ids_to_names = ids_to_names
        self._on_select = on_select

        super().__init__(
            placeholder = 'Select meeting…',
            options = [
                SelectOption(
                    label = f'{meetings_i + 1}. {meeting.get_title()}',
                    value = meeting.get_title()
                    # Does not use index as values since an index can still be valid even if the target meeting no longer exists.
                    # Use titles since they are unique.
                )
                for meetings_i, meeting in enumerate(meetings[:MAX_SELECTS])
            ]
        )

    async def callback(self, interaction: Interaction):
        meetings = self._meetings

        # Get target meeting.
        target_meeting = find_meeting(meetings, self.values[0])
        if isinstance(target_meeting, str):
            await interaction.followup.send(target_meeting)
            return

        # Execute followup process.
        await self._on_select(
            interaction,
            meetings,
            self._ids_to_names,
            target_meeting
        )
