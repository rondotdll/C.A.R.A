from cara.const import *
from cara.cnlp import is_directed_at_cara
from src.cara.commands import handle_command


###########################################################################################

# this is a security feature to verify that our base prompt was parsed correctly
# an invalid base prompt can result in strange & unpredictable behavior from GPT


def initial_confirmation(base_prompt):
    print(base_prompt + "\n")
    res = input("Please confirm this base prompt is correct [Y/n] > ")
    if res.upper() not in ["Y", ""]:
        print("Failed to validate base prompt.\nStopping...")
        exit(1)


###########################################################################################

# verify this file is being run as a program and not a module
if __name__ == "__main__":
    initial_confirmation(gpt.base_prompt_text)

    # triggered when a stable connection to discord has been made
    @bot.event
    async def on_ready():
        # give cara something to do
        print(
            f"Successfully logged in as {bot.user.name}#{bot.user.discriminator} [{bot.user.id}]"
        )

    # triggered everytime a message is sent
    @bot.event
    async def on_message(msg: discord.Message):
        # print(str(msg.author.id) + " >> " + msg.content)

        # determine if CARA is the message author
        if msg.author == bot.user:
            # if this message was already added to our context stack
            if gpt.context[-1]["content"] != msg.content:
                gpt.add_ctx(msg.content, "assistant")
            return

        if not is_directed_at_cara(msg):
            gpt.add_ctx(
                f"[{msg.author.display_name or msg.author.name}]: {msg.content}"
            )
            return

        # restrict non-developers from using Cara (for testing)
        if msg.author.id not in developer_ids:
            return

        # display the "C.A.R.A is typing..." text
        async with msg.channel.typing():
            await handle_command(msg)

    bot.run(token)
