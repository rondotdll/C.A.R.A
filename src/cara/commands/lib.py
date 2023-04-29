from discord import Message

from cara.const import gpt, nlp

from src.cara.commands.kick import kick_command
from src.cara.commands.ban import ban_command

# unused... from commands.mute import mute_command

# self-explanatory, interprets a message and handles it accordingly
import re


# this function was generated by GPT, and needs to be modified
async def handle_command(msg: Message):
    # define regular expression to extract command and subject

    command_regex = re.compile(r"^(kick|ban|mute|timeout) (.+)$", re.IGNORECASE)

    # extract command and subject from message
    match = command_regex.match(msg.content)
    if match:
        intent = match.group(1)
        subject = match.group(2)
    else:
        intent = None
        subject = None

        # process the message through our NLP engine
        doc = nlp(msg.content)

        # extract intent and subject using dependency parser
        for token in doc:
            if token.pos_ == "VERB":
                for child in token.children:
                    if child.dep_ == "nsubj":
                        intent = token.lemma_
                        subject = child.text
                        break

    print(intent, subject)

    # handle intent
    if intent == "kick":
        await kick_command(msg, subject)
    elif intent == "ban":
        await ban_command(msg, subject)
    elif intent == "mute":
        ...  # await mute_command(msg, subject)
    elif intent == "timeout":
        ...  # await timeout_command(msg, subject)
    else:
        # handle invalid command
        return await msg.reply(
            gpt.reply_ctx(
                f"[{msg.author.display_name or msg.author.name}]: {msg.content}", 5
            )
        )