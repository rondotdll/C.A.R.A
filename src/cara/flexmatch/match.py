import re

from enum import Enum
from dataclasses import dataclass
from discord import Message, User, NotFound

from src.cara.flexmatch import strings
from src.cara.flexmatch.levenshtein import min_distance


class MatchType(Enum):
    substr = 2
    editdist = 1
    none = 0


class NoNameError(Exception):
    pass


def flatten(matches: list[str], map: dict):
    result = []
    for match in matches:
        result += map[match]
    return result


@dataclass
class NameConflictError(Exception):
    # todo: accept conflicting users as parameters
    conflicts: list[int]
    pass


def __match_is_unique(input, vals) -> bool:
    return not (len(input) > 1 or len(vals[input[0]]) > 1)


async def match_user(input: str, context: Message) -> User:
    # check if the input string is a discord snowflake ID
    user_id = re.findall(r"\d{18}", input, re.MULTILINE)

    # if we found users by id
    if len(user_id) >= 1:
        try:
            user_obj = context.bot.get_user(user_id[0])
            return user_obj
        except NotFound:
            pass

    # check usernames & nicknames in the guild
    guild_username_map = {}
    guild_nickname_map = {}
    for member in context.guild.members:
        normalized_name = strings.normalize(member.name).lower()

        # if the name was already found, replace it with the current ID
        if normalized_name in guild_username_map:
            guild_username_map[normalized_name].append(member.id)
        else:
            guild_username_map.update({normalized_name: [member.id]})

        if member.nick and len(member.nick) > 0:  # checks if the member has a nickname
            normalized_nick = strings.normalize(member.nick).lower()
            if normalized_nick in guild_nickname_map:
                guild_nickname_map[normalized_nick].append(member.id)
            else:
                guild_nickname_map.update({normalized_nick: [member.id]})

    # check both nicknames and usernames.
    uname_matches, uname_match_type, uname_distance = match(
        input, list(guild_username_map.keys())
    )

    # this handles the EXTREMELY unlikely chance that nobody in the server has a nickname:
    nick_matches, nick_match_type, nick_distance = [], MatchType.none, -1
    if len(guild_nickname_map) > 0:
        nick_matches, nick_match_type, nick_distance = match(
            input, list(guild_nickname_map.keys())
        )

    if uname_match_type == nick_match_type:
        if nick_match_type == MatchType.editdist:
            # precondition: both matches have results with edit distance

            if uname_distance < nick_distance:
                if (
                    len(uname_matches) != 1
                    or len(guild_username_map[uname_matches[0]]) > 1
                ):
                    raise NameConflictError(flatten(uname_matches, guild_username_map))
                member = context.guild.get_member(
                    guild_username_map[uname_matches[0]][0]
                )
                return member._user

            elif nick_distance < uname_distance:
                if (
                    len(nick_matches) != 1
                    or len(guild_nickname_map[nick_matches[0]]) > 1
                ):
                    raise NameConflictError(flatten(nick_matches, guild_nickname_map))
                member = context.guild.get_member(
                    guild_nickname_map[nick_matches[0]][0]
                )
                return member._user

            else:
                # nick dist = name dist
                raise NameConflictError(
                    list(
                        set(
                            flatten(uname_matches, guild_username_map)
                            + flatten(nick_matches, guild_nickname_map)
                        )
                    )
                )

        elif nick_match_type == MatchType.substr:
            # both are substring matches...
            raise NameConflictError(
                flatten(uname_matches, guild_username_map)
                + flatten(nick_matches, guild_nickname_map)
            )
        else:
            raise NoNameError

    else:
        if uname_match_type.value > nick_match_type.value:
            # precondition: name_match has greater than or equal to one match
            if len(uname_matches) > 1 or len(guild_username_map[uname_matches[0]]) > 1:
                raise NameConflictError(flatten(uname_matches, guild_username_map))

            member = context.guild.get_member(guild_username_map[uname_matches[0]][0])
            return member._user

        elif uname_match_type.value < nick_match_type.value:
            if len(nick_matches) > 1 or len(guild_nickname_map[nick_matches[0]]) > 1:
                raise NameConflictError(flatten(nick_matches, guild_nickname_map))

            member = context.guild.get_member(guild_nickname_map[nick_matches[0]][0])
            return member._user

    print("I should not be executing. There is a problem.")
    return None


# tries matching "input" string to "vals" list of strings
def match(input: str, vals: list[str]) -> (list[str], MatchType, int):
    # verifies that only alphanumeric characters are in the string
    def sanitize(value: str) -> str:
        always_acceptable = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )
        output = [
            c if c in always_acceptable or c in value else "" for c in value
        ]  # if there is a non-normalized character in our input, keep it
        return "".join(output)

    # we only want prefixed substrings
    # for example: "ric" in "rick ross"
    def substr_viable_matches(matches: list[str]) -> list[str]:
        output = []
        for match in matches:
            if " " in match:  # if the match is multiple words
                words = match.split(" ")  # split it
                for word in words:
                    if word.startswith(input):
                        output.append(match)
            elif match.startswith(input):
                output.append(match)

        return output

    # a map of "sanitized":"un-sanitized"
    sanitized_map = {sanitize(val): val for val in vals}
    sanitized_values = list(sanitized_map.keys())

    # find the closest sanitized levenshtein & substring matches to our input
    lvshtn_match, lvshtn_distance = min_distance(input, sanitized_values)
    substring_match = strings.substr_match(input, sanitized_values)

    # if there are substring matches (that are not 100% matches)
    if len(substring_match) != 0 and lvshtn_distance != 0:
        # if the match is at least 50% similar to "input"
        if lvshtn_distance < (len(input) / 2):
            viable_substr_matches = substr_viable_matches(sanitized_values)

            if len(viable_substr_matches) > 0:
                return (
                    [
                        sanitized_map[viable_substr]
                        for viable_substr in viable_substr_matches
                    ],
                    MatchType.substr,
                    -1,
                )
        else:
            return (
                [sanitized_map[match] for match in substring_match],
                MatchType.substr,
                -1,
            )

    # if "input" is less than 50% similar to any "vals"
    elif lvshtn_distance >= len(input) * 1 / 2:
        return None, MatchType.none, -1

    return (
        [sanitized_map[match] for match in lvshtn_match],
        MatchType.editdist,
        lvshtn_distance,
    )
