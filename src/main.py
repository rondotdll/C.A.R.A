import os

import discord
from discord.ext.commands import AutoShardedBot

from cara.commands.lib import handle_command
from cara.const import *
from cara.cnlp import is_directed_at_cara
from cara.gpt.context import ContextCollection

token = os.environ["TOKEN"]

###########################################################################################

# this is a security feature to verify that our base prompt was parsed correctly
# an invalid base prompt can result in strange & unpredictable behavior from GPT


def initial_confirmation(base_prompt):
    print(base_prompt + "\n")
    res = input("Please confirm this base prompt is correct [Y/n] > ")
    if res.upper() not in ["Y", ""]:
        print("Failed to validate base prompt.\nStopping...")
        exit(1)


###########################################################################################


class CARABot(AutoShardedBot):
    def __init__(self):
        super().__init__(
            intents=intents, status=status, activity=activity, command_prefix=""
        )

        self.contexts = None
        self.gpt = GPT3("./base_prompt.md")

    async def on_ready(self):
        # give cara something to do
        print(
            f"Successfully logged in as {bot.user.name}#{bot.user.discriminator} [{bot.user.id}]"
        )

        self.contexts = ContextCollection(assistant_user=self.user)

    async def on_message(self, msg: discord.Message):
        # restrict non-developers from using Cara (for testing)
        if msg.author.id not in developer_ids:
            return

        # determine if CARA is the message author
        if msg.author == bot.user:
            return

        # get the appropriate context for this message
        context = self.contexts[msg.author, msg.channel]

        # add the message to the context...
        context += msg
        print(f"{context.for_user.display_name}: {len(context)} messages")

        if not is_directed_at_cara(context, msg):
            return

        # display the "C.A.R.A is typing..." text
        async with msg.channel.typing():
            # prompt = await handle_command(msg)
            response = self.gpt.continue_conversation(context)
            await msg.reply(response)


# verify this file is being run as a program and not a module
if __name__ == "__main__":
    bot = CARABot()
    bot.run(token)
