import os
import pathlib

import openai

# this class will handle any GPT interaction

class GPT3:
###########################################################################################

    def __init__(self, base_prompt_file: str):
        self.base_prompt_text = " ".join(
            [line for line in open(base_prompt_file, "r").readlines()
                                if (line.strip() != '' and not line.startswith('#'))] # lines starting with hashtags are treated as comments, and are removed.
        ).strip()

        # This defines the models overall behavior
        self.base_prompt = {
            "role": "system",
            "content": self.base_prompt_text,
        }

        # openai config stuff
        openai.api_key = os.environ["GPT-KEY"]
        self.model = "gpt-3.5-turbo"
        self.wild_card = 0.5 # "randomness" of the responses

        # this is a continuous thread of messages that is passed to GPT each time reply_ctx()
        self.context = [self.base_prompt]

###########################################################################################

    def describe_e(self, error: Exception) -> str:
        openai.ChatCompletion.create(
            model=self.model,
            messages={
                self.base_prompt,
                {
                    "role": "user",
                    "content": "The following Python exception occured in your code: " + str(error)
                }
            }
        )

###########################################################################################

    # replies to a message without context (only includes base prompt and string)
    # this is SIGNIFICANTLY CHEAPER, and should be used over reply_ctx()
    # returns the message, and if the code executed properly
    def reply(self, msg: str, humanize: bool = False) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    self.base_prompt,
                    {
                        "role": "user",
                        "content": msg
                    }
                ]
            )

            # Due to the nature of GPT, some responses may feel too "robotic".
            # by setting humanize to true, we'll have GPT try to humanize the response.
            if humanize:
                return self.reply(f"Humanize the following text:\n{response.choices[0].message.content}")

            # openai returns a JSON object with a bunch of other stuff in it
            # so we need to grab the useful part (our response)
            return response.choices[0].message.content

        # if an exception occurs, we'll try to once again use GPT to describe what went wrong.
        except Exception as E:
            return self.describe_e(E)

###########################################################################################

    # replies to a message without context, using an extremely minimal system prompt
    # this is even cheaper than a standard reply()
    def reply_min(self, msg: str, humanize: bool = False) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a discord moderation AI named \"C.A.R.A\", which stands for \"Cognitive Automated Response Assistant\", and you were created in Python by Studio 7 Development.",
                    }, {
                        "role": "user",
                        "content": msg
                    }
                ]
            )

            if humanize:
                return self.reply_min(f"Humanize the following text:\n{response.choices[0].message.content}")

            return response.choices[0].message.content

        except Exception as E:
            return self.describe_e(E)

###########################################################################################

    # replies to a message using the global context
    # this becomes really expen$$$ive really fast and should be used sparingly
    def reply_ctx(self, msg: str, ctx_size: int = -1, humanize: bool = False) -> str:
        try:
            # add our message to the context stack
            self.add_ctx(msg)

            context = self.context

            # context size will only select the "ctx_size" most recent messages (with the base prompt)
            if 0 < ctx_size <= len(context):
                context = self.context[-(ctx_size):]
                context[0] = self.base_prompt

            # send the context to OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=context
            )

            # add the reply to our rolling context
            self.add_ctx(
                role="assistant",
                msg=response.choices[0].message.content,
            )

            if humanize:
                return self.reply_min(f"Humanize the following text:\n{response.choices[0].message.content}")

            return response.choices[0].message.content

        except Exception as E:
            return self.describe_e(E)

###########################################################################################

    # clears the current conversation context
    def clear_ctx(self):
        self.context = [
            self.base_prompt
        ]

###########################################################################################

    # adds a message to context
    def add_ctx(self, msg: str, role: str = "user"):
        # cap our context at 50 messages
        if len(self.context) >= 50:
            self.context = self.context[-49:]

        self.context.append(
            {
                "role": role,
                "content": msg
            }
        )
