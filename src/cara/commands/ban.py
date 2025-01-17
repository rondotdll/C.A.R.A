from cara.const import *
from src.cara.commands.base import check_subject_present, PROMPT_NO_SUBJECT
from src.cara.flexmatch import match_user, NameConflictError, NoNameError

from discord import Message


###########################################################################################

# this function attempts to ban a user from the server, based on the "subject" variable
# it then generates & sends a reply to the user, depending on the outcome.


async def ban_command(msg: Message, subject: str):
    try:
        msg.mentions.remove(bot.user)
    except ValueError:
        pass

    user = None

    # If we failed to detect a subject, inform the user of this.
    if not check_subject_present(subject, msg):
        return PROMPT_NO_SUBJECT(msg.author)

    # If the user mentioned someone, use the mention as our target.
    if len(msg.mentions) >= 1:
        user = msg.mentions[0]

    # If the user doesn't have permission to kick, inform them.
    if not msg.channel.permissions_for(msg.author).ban_members:
        return (
            f"reply with ONLY a response to {msg.author.mention}, "
            f"stating that they lack permission to ban users."
        )

    # If cara doesn't have permission to kick users, inform the user
    if not msg.channel.permissions_for(msg.guild.get_member(bot.user.id)).ban_members:
        return (
            f"reply with ONLY a response to {msg.author.mention}, "
            f"stating that you lack permission to ban users."
        )

    try:
        # attempt to find a user based on the "subject" string
        user = match_user(subject, msg)

    # this means there are multiple people that match the "subject" provided
    except NameConflictError:
        return (
            f"reply with ONLY a response to `{msg.author.name}`, "
            f"stating that the username they provided was too generic."
        )

    # this means we failed to find a target
    except NoNameError:
        return (
            f"reply with ONLY a response to `{msg.author.name}`,"
            f"stating that you couldn't figure out who they were referring to."
        )

    # attempt to kick the target user.
    try:
        await msg.guild.ban(user)
    # this exception should only be triggered if the user in question
    # has a higher server rank than Cara
    except Exception:
        return (
            f"reply with ONLY a response to {msg.author.name}, "
            f"stating that the person they are trying to ban is higher ranked than you are."
        )

    # reply saying we succeeded in kicking them
    return (
        f"reply with ONLY a response to {msg.author.name}, "
        f"stating that you have kicked %APPLESAUCE% from the server"
    ).replace("%APPLESAUCE%", user.mention)
