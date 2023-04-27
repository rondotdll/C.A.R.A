
from discord import Message
from const import bot, gpt, nlp

def is_directed_at_cara(msg: Message) -> bool:
    # determine if the message is directed at CARA
    # if cara isn't mentioned explicitly
    if not (bot.user in msg.mentions or msg.content.lower().replace(".", "").startswith("cara")):
        # add the message to our context stack
        gpt.add_ctx(f"[{msg.author.display_name or msg.author.name}]: {msg.content}", "user")

        # if the last message wasn't from Cara, do nothing.
        if gpt.context[-2]["role"] != "assistant":
                if gpt.context[-3]["content"].split("]:")[0].replace("[", "") == (msg.author.display_name or msg.author.name):
            return