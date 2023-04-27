from const import gpt

from discord import Message

###########################################################################################

# list of currently supported commands
command_list = {
        "kick": {"keywords": ["kick", "boot", "remove", "escort"]},
        "ban": {"keywords": ["ban", "block", "banish", "vaporize"]},
        "mute": {"keywords": ["mute", "silence", "quiet", "shutup"]}
    }

# function to check if a subject exists in the message
# (saves on code space)

###########################################################################################

async def check_subject_present(subject, msg: Message) -> bool:
    if subject is None and len(msg.mentions) < 1:
        await msg.reply(
            gpt.reply(
                f"reply with ONLY a response to `{msg.author.mention}`, "
                f"stating that you had trouble interpreting the subject of the message.")
        )
        return False
    return True
