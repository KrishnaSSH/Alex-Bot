import os
from typing import Any

import discord
from discord.ext import commands
from dotenv import load_dotenv

from cogs import COMMANDS, EVENT_HANDLERS
from bot_utilities.config_loader import config

load_dotenv('.env')

class AIBot(commands.AutoShardedBot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if config['AUTO_SHARDING']:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(shard_count=1, *args, **kwargs)

    async def setup_hook(self) -> None:
        # Load cogs
        for cog in COMMANDS:
            cog_name = cog.split('.')[-1]
            discord.client._log.info(f"Loaded Command {cog_name}")
            await self.load_extension(f"{cog}")
        for cog in EVENT_HANDLERS:
            cog_name = cog.split('.')[-1]
            discord.client._log.info(f"Loaded Event Handler {cog_name}")
            await self.load_extension(f"{cog}")
        
        # Define command with integration_types and contexts
        @bot.tree.command()
        async def ping(interaction: discord.Interaction, hide: bool = False):
            """Replies with the bot's current ping."""
            await interaction.response.send_message(
                f'Pong! {round(bot.latency * 1000)}ms', ephemeral=hide
            )
        
        # Adding integration types and contexts
        ping_command = bot.tree.get_command("ping")
        if ping_command:
            ping_command.integration_types = [0, 1]
            ping_command.contexts = [0, 1, 2]

        print('If syncing commands is taking longer than usual you are being ratelimited')
        await self.tree.sync()  # Syncing commands globally
        discord.client._log.info(f"Loaded {len(self.tree.get_commands())} global commands")

bot = AIBot(command_prefix=[], intents=discord.Intents.all(), help_command=None)

TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    print("\033[31mLooks like you haven't properly set up a Discord token environment variable in the `.env` file. (Secrets on replit)\033[0m")
    print("\033[33mNote: If you don't have a Discord token environment variable, you will have to input it every time. \033[0m")
    TOKEN = input("Please enter your Discord token: ")

bot.run(TOKEN, reconnect=True)
