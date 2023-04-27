from discord import Message

from const import gpt, nlp

from commands.base import command_list
from commands.kick import kick_command
from commands.ban import ban_command
# unused... from commands.mute import mute_command

# self-explanatory, interprets a message and handles it accordingly
async def handle_command(msg: Message):
    # process the message through our NLP engine
    doc = nlp(msg.content)
    intent = None
    subject = None
    print([t.ent_type_ for t in doc])
    print([t.pos_ for t in doc])

    # parse our NLP output, determining an action & subject.
    for token in doc:
        if token.pos_ == "VERB":
            # Check if the verb is associated with a command
            for command, data in command_list.items():
                if token.lemma_ in data["keywords"]:
                    intent = command
                    break
        if token.dep_ == "dobj":
            # Check if a person's name is mentioned in the message
            subject = token.text

    print(intent, subject)

    if intent == "kick":
        await kick_command(msg, subject)
    elif intent == "ban":
        await ban_command(msg, subject)
    elif intent == "mute":
        ...

    else:
        return await msg.reply(
            gpt.reply_ctx(f"[{msg.author.display_name or msg.author.name}]: {msg.content}", 5)
        )
