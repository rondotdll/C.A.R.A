from cara.gpt.api import GPT3

import os
import spacy

import discord
import openai

# discord config parameters
intents = discord.Intents.all()
status = discord.Status.online
activity = discord.Activity(
    type=discord.ActivityType.watching,
    name="david j on YouTube",
    url="https://www.youtube.com/watch?v=qtVbEJwLaQA",
)


# openai config parameters
openai.api_key = os.environ["GPT-KEY"]
model_engine = "gpt-3.5-turbo"
# max_tokens = 100 # this is unused for chat completion
temperature = 0.5  # "randomness" of the responses

CARA_ID = 1092993211015901246

developer_ids = [
    123456789123456789,  # sample id
]

# gpt = GPT3("./base_prompt.md")
nlp = spacy.load("en_core_web_lg")
trf = None  # spacy.load("en_core_web_trf")
bot = discord.Client(intents=intents, activity=activity)
