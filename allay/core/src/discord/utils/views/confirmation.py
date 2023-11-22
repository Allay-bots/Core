from typing import Callable, Optional, Union

from discord import ButtonStyle, Interaction, Message, ui

###  Usage example  ###

# confirm_view = ConfirmView(
#     validation=lambda inter: inter.user.id == interaction.user.id,
#     send_confirmation=False
# )
# await interaction.followup.send(
#     "This giveaway is still ongoing! Are you sure you want to delete it?",
#     view=confirm_view
# )
# await confirm_view.wait()
# if confirm_view.value is None: # timeout
#     await confirm_view.disable(interaction)
#     return
# if not confirm_view.value: # cancelled
#     await confirm_view.disable(interaction)
#     return
# # confirmed
# await interaction.followup.send("Deleting giveaway...", ephemeral=True)


class ConfirmView(ui.View):
    "A simple view used to confirm an action"

    def __init__(self, validation: Callable[[Interaction], bool],
                 ephemeral: bool=True, timeout: int=60, send_confirmation: bool=True):
        super().__init__(timeout=timeout)
        self.value: Optional[bool] = None
        self.validation = validation
        self.ephemeral = ephemeral
        self.send_confirmation = send_confirmation

    @ui.button(label="Confirm", style=ButtonStyle.green)
    async def confirm(self, interaction: Interaction, _button):
        "Confirm the action when clicking"
        if not self.validation(interaction):
            return
        if self.send_confirmation:
            await interaction.response.send_message("Confirmed!", ephemeral=self.ephemeral)
        self.value = True
        self.stop()

    @ui.button(label="Cancel", style=ButtonStyle.grey)
    async def cancel(self, interaction: Interaction, _button):
        "Cancel the action when clicking"
        if not self.validation(interaction):
            return
        await interaction.response.send_message("Cancelled!", ephemeral=self.ephemeral)
        self.value = False
        self.stop()

    async def disable(self, interaction: Union[Message, Interaction]):
        "Called when the timeout has expired"
        for child in self.children:
            child.disabled = True # type: ignore
        if isinstance(interaction, Interaction):
            if interaction.message is None:
                return
            await interaction.followup.edit_message(
                interaction.message.id,
                content=interaction.message.content,
                view=self
            )
        else:
            await interaction.edit(content=interaction.content, view=self)
        self.stop()
