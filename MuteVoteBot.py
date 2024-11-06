import discord
from discord.ext import commands
import asyncio

# Define the bot's command prefix and intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

class VoteButtons(discord.ui.View):
    def __init__(self, ctx, user):
        super().__init__(timeout=30)  # Vote will end after 30 seconds
        self.ctx = ctx
        self.user = user  # The user being voted on
        self.mute_votes = 0
        self.do_not_mute_votes = 0
        self.voters = set()

    @discord.ui.button(label="Mute", style=discord.ButtonStyle.green)
    async def mute_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.user:
            await interaction.response.send_message("You cannot vote on your own mute.", ephemeral=True)
            return

        if interaction.user not in self.voters and interaction.user.voice and interaction.user.voice.channel == self.ctx.author.voice.channel:
            self.mute_votes += 1
            self.voters.add(interaction.user)
            await interaction.response.send_message(f"{interaction.user.mention} voted to Mute.", ephemeral=True)
        else:
            await interaction.response.send_message("You have already voted or are not in the correct voice channel.", ephemeral=True)

    @discord.ui.button(label="Do Not Mute", style=discord.ButtonStyle.red)
    async def do_not_mute_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.user:
            await interaction.response.send_message("You cannot vote on your own mute.", ephemeral=True)
            return

        if interaction.user not in self.voters and interaction.user.voice and interaction.user.voice.channel == self.ctx.author.voice.channel:
            self.do_not_mute_votes += 1
            self.voters.add(interaction.user)
            await interaction.response.send_message(f"{interaction.user.mention} voted Do Not Mute.", ephemeral=True)
        else:
            await interaction.response.send_message("You have already voted or are not in the correct voice channel.", ephemeral=True)

    async def on_timeout(self):
        # Calculate the result after 30 seconds
        if self.mute_votes > self.do_not_mute_votes:
            await self.ctx.send(f"The majority voted to mute {self.user.mention}. They will be muted for 3 minutes.")
            await self.user.edit(mute=True)
            
            # Unmute after 3 minutes
            await asyncio.sleep(180)
            await self.user.edit(mute=False)
            await self.ctx.send(f"{self.user.mention} has been unmuted.")
        else:
            await self.ctx.send(f"The majority voted not to mute {self.user.mention}.")


@bot.command()
async def MuteVote(ctx, user: discord.Member):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("You must be in a voice channel to start a mute vote.")
        return
    
    if user.voice is None:
        await ctx.send("The mentioned user is not in a voice channel.")
        return

    # Start the voting process with buttons
    await ctx.send(f"A vote has started to mute {user.mention} for 3 minutes! You have 30 seconds to vote.", view=VoteButtons(ctx, user))

# Run the bot
bot.run('YOUR_BOT_TOKEN')
