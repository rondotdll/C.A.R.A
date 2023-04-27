import time
import spacy
import discord

from commands.lib import handle_command

from const import *
from flexmatch.match import *

from discord import Embed, Message, Permissions

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

# verify this file is being run as a program and not a module
if __name__ == "__main__":
    initial_confirmation(gpt.base_prompt_text)

    # triggered when a stable connection to discord has been made
    @bot.event
    async def on_ready():
        # give cara something to do
        bot.activity = activity
        print(f"Successfully logged in as {bot.user.name}#{bot.user.discriminator} [{bot.user.id}]")

    # triggered everytime a message is sent
    @bot.event
    async def on_message(msg: discord.Message):

        # determine if CARA is the message author
        if msg.author == bot.user:
            # if this message was already added to our context stack
            if gpt.context[-1]["content"] != msg.content:
                gpt.add_ctx(msg.content, "assistant")
            return



        # restrict non-developers from using Cara (for testing)
        if msg.author.id not in developer_ids:
            return

        # display the "C.A.R.A is typing..." text
        async with msg.channel.typing():

            await handle_command(msg)


    bot.run(token)