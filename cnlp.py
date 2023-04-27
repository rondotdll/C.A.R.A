
import re

from discord import Message
from const import bot, gpt, nlp, trf

###########################################################################################


def has_question(string: str) -> bool:
    sentences = string.replace("! ", ".")
    sentences = sentences.split(".")
    for sentence in sentences:
        # Parse the sentence
        words = nlp(sentence)

        # Check if the sentence starts with a question word
        if words[0].tag_ == 'WDT' or words[0].tag_ == 'WP' or words[0].tag_ == 'WP$' or words[0].tag_ == 'WRB':
            return True
        else:
            # Check if the sentence contains a verb in the auxiliary or modal form
            has_aux_or_modal = False
            for word in words:
                if word.tag_.startswith('MD') or (word.dep_ == 'aux' and word.head.pos_ == 'VERB'):
                    has_aux_or_modal = True
                    break

            # Check if the sentence contains a question word
            has_question_word = False
            for word in words:
                if word.tag_ == 'WDT' or word.tag_ == 'WP' or word.tag_ == 'WP$' or word.tag_ == 'WRB':
                    has_question_word = True
                    break

            # Check if the sentence ends with a question mark
            ends_with_question_mark = sentence.endswith('?')

            # Check if the sentence is a command or an exclamation
            is_command_or_exclamation = False
            for word in words:
                if word.dep_ == 'ROOT' and (word.tag_ == 'VB' or word.tag_ == 'VBP'):
                    is_command_or_exclamation = True
                    break

            # Combine the rules to determine if the sentence is a question
            if has_question_word or has_aux_or_modal or ends_with_question_mark:
                return True
            elif not is_command_or_exclamation:
                # extra logic
                if sentence.lower().startswith("who") or sentence.lower().startswith(
                        "what") or sentence.lower().startswith("where") or sentence.lower().startswith(
                        "when") or sentence.lower().startswith("why"):
                    return True

                if sentences.index(sentence) == len(sentences) -1:
                    return False

                continue

            # if we are unsure
            else:
                # final guess
                if sentence.lower().startswith("who") or sentence.lower().startswith("what") or sentence.lower().startswith("where") or sentence.lower().startswith("when") or sentence.lower().startswith("why"):
                    return True

                # if we are still unsure on the last sentence just assume it is...?
                if sentences.index(sentence) == len(sentences) -1:
                    return True
                continue

    return False

###########################################################################################


# determine if a message is directed at CARA
def is_directed_at_cara(msg: Message) -> bool:
    # if cara is mentioned explicitly
    if bot.user in msg.mentions:
        return True

    sentences = msg.content.replace("! ", ".")
    sentences = sentences.split(".")
    for sentence in sentences:
        words = nlp(sentence.lower().replace("c.a.r.a", "cara"))

        for word in words:

            # favor cara as a direct object first
            if word.dep_ == "nsubj":
                # direct reference to cara
                if word.orth_ == "cara":
                    return True

                # indirect reference to cara
                elif word.orth_ == "you":
                    try:
                        if gpt.context[-1]["role"] == "assistant":
                            return True

                    except IndexError:
                        ...
                else:
                    break

            # favor cara as a direct object second to as a subject
            elif word.dep_ == "dobj":

                # indirect reference to cara
                if word.orth_ == "you":
                    try:
                        if gpt.context[-1]["role"] == "assistant" or "cara" in sentence:
                            return True

                    except IndexError:
                        ...


        # if the user explicitly mention cara
        if bot.user in msg.mentions or msg.content.lower().replace(".", "").startswith("cara"):
            return True
        else:
            try:
                # if the last message was from Cara
                if gpt.context[-1]["role"] == "assistant":
                    # and the message before the last was by the current message author
                    if gpt.context[-2]["content"].split("]: ")[0].replace("[", "") == (msg.author.display_name or msg.author.name):
                        # and either the previous or current message is a question:
                        if has_question(msg.content):
                            return True


            except IndexError:
                ...

    return False