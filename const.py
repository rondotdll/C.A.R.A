import os

from gpt import GPT3

import os

import discord
import openai

# discord config parameters
token = os.environ["TOKEN"]
intents = discord.Intents.all()
status = discord.Status.online
activity = discord.Activity(
    type=discord.ActivityType.watching,
    name="david j on YouTube",
    url="https://www.youtube.com/watch?v=qtVbEJwLaQA"
)


# openai config parameters
openai.api_key = os.environ["GPT-KEY"]
model_engine = "gpt-3.5-turbo"
#max_tokens = 100 # this is unused for chat completion
temperature = 0.5 # "randomness" of the responses

developer_ids = [
    715019722336370788, # root
    846498827238506499, # david j
    525089462892625929, # Diamonds.
]

gpt = GPT3("base_prompt.md")

commands = {
        "kick": {"keywords": ["kick", "boot", "remove"]},
        "ban": {"keywords": ["ban", "block", "banish", "vaporize"]},
        "mute": {"keywords": ["mute", "silence", "quiet", "shutup"]}
    }