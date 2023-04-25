import time
import spacy
import discord

from const import *
from flexmatch.match import *

from discord import Embed, Message, Permissions

nlp = spacy.load("en_core_web_lg")
bot = discord.Client(intents=intents)

def initial_confirmation(base_prompt):
    print(base_prompt + "\n")
    res = input("Please confirm this base prompt is correct [Y/n] > ")
    if res.upper() not in ["Y", ""]:
        print("Failed to validate base prompt.\nStopping...")
        exit(1)

async def handle_command(msg: Message):
    doc = nlp(msg.content)
    intent = None
    subject = None
    print([t.ent_type_ for t in doc])
    print([t.pos_ for t in doc])

    for token in doc:
        if token.pos_ == "VERB":
            # Check if the verb is associated with a command
            for command, data in commands.items():
                if token.lemma_ in data["keywords"]:
                    intent = command
                    break
        if token.dep_ == "dobj":
            # Check if a person's name is mentioned in the message
            subject = token.text

    print(intent, subject)

    if intent == "kick":
        if subject == None:
            return await msg.reply(
                gpt.reply(f"reply with ONLY a response to `{msg.author.mention}`, stating that you had trouble interpreting the subject of the message.")
            )

        if not msg.channel.permissions_for(msg.author).kick_members:
            return await msg.reply(
                gpt.reply(
                    f"reply with ONLY a response to {msg.author.mention}, stating that they lack permission to kick users.")
            )

        try:
            user = await match_user(subject, msg)
            print("kicked this nerd")
            await msg.guild.kick(user)
            await msg.reply(
                gpt.reply_min(f"reply with ONLY a response to {msg.author.name}, stating that you have kicked %APPLESAUCE% from the server")
                .replace("%APPLESAUCE%", user.mention)
            )

        except NameConflictError:
            return await msg.reply(
                gpt.reply_min(f"reply with ONLY a response to `{msg.author.name}`, stating that the username they provided was too generic.")
            )
        except NoNameError:
            return await msg.reply(
                gpt.reply_min(
                    f"tell `{msg.author.mention}` you had couldn't figure out who they were referring to, and do not thank them.")
            )

    else:
        return await msg.reply(
            gpt.reply_ctx(f"[{msg.author.display_name or msg.author.name}]: {msg.content}", 5)
        )


if __name__ == "__main__":
    initial_confirmation(gpt.base_prompt_text)

    def handle_intent_embed(mention, intent):
        embed = Embed(
            title="Moderation",
            color=0xff365a
        ).add_field(name="Action", value=intent.upper())\
            .add_field(name="Subject", value=mention[0])
        return embed

    @bot.event
    async def on_ready():
        print(f"Successfully logged in as {bot.user.name}#{bot.user.discriminator} [{bot.user.id}]")

    @bot.event
    async def on_message(msg: discord.Message):

        # determine if CARA is the message author
        if msg.author == bot.user:
            if gpt.context[-1]["content"] != msg.content:
                gpt.add_ctx(msg.content, "assistant")
            return

        # determine if the message is directed at CARA
        if not (bot.user in msg.mentions or msg.content.lower().replace(".", "").startswith("cara")):
            gpt.add_ctx(f"[{msg.author.display_name or msg.author.name}]: {msg.content}", "user")
            if gpt.context[-2]["role"] != "assistant" and \
                    gpt.context[-3]["content"].split("]:")[0].replace("[", "") == (msg.author.display_name or msg.author.name):
                return

        # display the "C.A.R.A is typing..." text
        async with msg.channel.typing():
            # restrict non-developers from using Cara (for testing)
            if msg.author.id not in developer_ids:
                time.sleep(1.8)
                await msg.reply(
                    "Sorry, but as of right now I'm currently in a \"*show-and-tell*\" state, and am only a proof of "
                    "concept. As such, my access has been restricted to only Studio 7 developers."
                )
                return

            await handle_command(msg)


    bot.run(token)