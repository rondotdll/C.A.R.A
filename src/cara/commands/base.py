from discord import Message

###########################################################################################

# list of currently supported commands
command_list = {
    "kick": {"keywords": ["kick", "boot", "remove", "escort"]},
    "ban": {"keywords": ["ban", "block", "banish", "vaporize"]},
    "mute": {"keywords": ["mute", "silence", "quiet", "shutup"]},
}

PROMPT_NO_SUBJECT = lambda author: (
    f"reply with ONLY a response to `{author.mention}`, "
    f"stating that you had trouble interpreting the subject of the message."
)


# function to check if a subject exists in the message
# (saves on code space)

###########################################################################################


def check_subject_present(subject, msg: Message) -> bool:
    # if subject is None and len(msg.mentions) < 1:
    #     return False
    # return True

    return subject is not None or len(msg.mentions) >= 1
