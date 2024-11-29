# examples/bot.py

import discord
from discord.ext import commands
from flowlib import initialize_flow_library, FlowView, button, register_view
import asyncio

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize the flow library with the bot and database URL
initialize_flow_library(bot, database_url="sqlite+aiosqlite:///flowlib.db")
# For PostgreSQL: database_url="postgresql+asyncpg://user:password@localhost/dbname"

# Define your views

@register_view('start')
class StartView(FlowView):
    def __init__(self, user_id):
        super().__init__(user_id=user_id)
        # Initialize state asynchronously
        asyncio.create_task(self.update_state(step='start'))

    @button(label="Proceed", next_step='confirmation', custom_id="start_proceed")
    async def proceed(self, interaction: discord.Interaction):
        await self.update_state(step='confirmation')
        await interaction.response.defer()

@register_view('confirmation')
class ConfirmationView(FlowView):
    def __init__(self, user_id):
        super().__init__(user_id=user_id)
        # Update state asynchronously
        asyncio.create_task(self.update_state(step='confirmation'))

    @button(label="Confirm", style=discord.ButtonStyle.success, custom_id="confirm_confirm")
    async def confirm(self, interaction: discord.Interaction):
        await self.update_state(confirmed=True, step=None)
        await interaction.response.send_message("Confirmed!", ephemeral=True)
        # Optionally, clear the user's state
        # await self.update_state(step=None, confirmed=None)

    @button(label="Cancel", style=discord.ButtonStyle.danger, next_step='start', custom_id="confirm_cancel")
    async def cancel(self, interaction: discord.Interaction):
        await self.update_state(confirmed=False)
        await interaction.response.defer()

# Command to start the workflow
@bot.command()
async def start(ctx):
    user_id = str(ctx.author.id)
    view = StartView(user_id=user_id)
    await ctx.send("Welcome to the workflow!", view=view)
    # Register the view
    bot.add_view(view)

# Run the bot
bot.run('YOUR_BOT_TOKEN')
