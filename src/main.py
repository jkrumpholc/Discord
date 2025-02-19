from discord import app_commands
from discord.ext import commands
import discord
import Anime
import System
import Notes
# import Guide
import time as Time

TOKEN = System.credentials("DISCORD_BOT")
GUILD = System.credentials("DISCORD_GUILD")
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print('Bot is ready')
    # Notes.clear_due()
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)


@bot.tree.command(name="today", description="Prints today's date")
async def today(interaction: discord.Interaction):
    await send(interaction, f"{System.today()}, {System.today().timetuple().tm_yday}")


@bot.tree.command(name="anime_watched", description="Update number of watched episodes in anime")
@app_commands.describe(name="Name of anime", num="Number of episodes")
async def anime_watched(interaction: discord.Interaction, name: str, num: int):
    await send(interaction, Anime.watched(name, num))


@bot.tree.command(name="anime_add", description="Add finished anime")
@app_commands.describe(url="URL of anime", ep="Number of watched episodes", max_ep="Total number of episodes")
async def anime_add(interaction: discord.Interaction, url: str, ep: int, max_ep: int):
    await send(interaction, Anime.new_anime(url, ep, max_ep))


@bot.tree.command(name="anime_add_going", description="Add ongoing anime")
@app_commands.describe(url="URL of anime", ep="Number of watched episodes", last="Number of released episodes",
                       update_time="Update date and time")
async def anime_add_going(interaction: discord.Interaction, url: str, ep: int, last: int, update_time: str):
    await send(interaction, Anime.new_anime_going(url, ep, last, update_time))


@bot.tree.command(name="anime_add_url", description="Add anime purely by url")
@app_commands.describe(url="URL of anime")
async def anime_add_url(interaction: discord.Interaction, url: str):
    await send(interaction, Anime.new_anime_url(url))


@bot.tree.command(name="anime_finished", description="Remove anime from watchlist")
@app_commands.describe(name="Name of anime")
async def anime_finished(interaction: discord.Interaction, name: str):
    await send(interaction, Anime.finished(name))


@bot.tree.command(name="anime_status", description="Return all anime from database")
async def anime_status(interaction: discord.Interaction):
    await send(interaction, Anime.status())


@bot.tree.command(name="anime_waiting", description="Return all ongoing anime with unwatched episodes")
async def anime_waiting(interaction: discord.Interaction):
    await send(interaction, Anime.waiting())


@bot.tree.command(name="anime_update", description="Check if ongoing anime have any new episodes")
async def anime_update(interaction: discord.Interaction):
    await send(interaction, Anime.update())


@bot.tree.command(name="anime_transfer", description="Move anime from ongoing to finished")
@app_commands.describe(name="Name of anime")
async def anime_transfer(interaction: discord.Interaction, name: str):
    await send(interaction, Anime.transfer(name))


@bot.tree.command(name="anime_change_time", description="Change airing time of ongoing anime")
@app_commands.describe(name="Name of anime", hour="New airing hour")
async def anime_add_going(interaction: discord.Interaction, name: str, hour: int):
    await send(interaction, Anime.change_time(name, hour))


async def send(interaction: discord.Interaction, data):
    data = System.split_lines(data)
    if data is str:
        await interaction.response.send_message(data)
    else:
        for i in data:
            await interaction.followup.send(i)


@bot.tree.command(name="log", description="Return file")
@app_commands.describe(name="Name of file")
async def log(interaction: discord.Interaction, name: str):
    file = ""
    try:
        file = discord.File(f"./{name}")
    except FileNotFoundError:
        file = "File doesn't exist"
    finally:
        await send(interaction, file)


@bot.tree.command(name="note_add", description="Create new note")
@app_commands.describe(name="Name of note", date="Date of note", time="Time of note", text="text of note")
async def note_add(interaction: discord.Interaction, name: str, date: str, time: str, text: str):
    data = Notes.add_note(name, date, time, text)
    await send(interaction, data[0])
    bot.loop.create_task(mention(interaction, name, text, data[1]))


@bot.tree.command(name="note_delete", description="Delete existing note")
@app_commands.describe(name="Name of note")
async def note_delete(interaction: discord.Interaction, name: str):
    data = Notes.delete_note(name)
    await send(interaction, data)


@bot.tree.command(name="clear", description="Clear last N messages in channel")
@app_commands.describe(number="Number of messages to delete", order="Type \"U\" if you want to delete from beginning")
async def clear(interaction: discord.Interaction, number: int, order: str = ""):
    if order == "u" or order == "U":
        await interaction.channel.purge(limit=number, oldest_first=True)
    else:
        await interaction.channel.purge(limit=number)
    return


async def mention(interaction: discord.Interaction, name, text, sleep_time):
    Time.sleep(sleep_time)
    respond = f"{name.replace('_', ' ')}\n{text}\n{interaction.user.mention}"
    await send(interaction, respond)
    Notes.delete_note(name)


"""
@bot.event
async def on_command_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.CommandNotFound):
        await send(interaction, "Command not found")
    else:
        await send(interaction, str(error))
"""

bot.run(TOKEN)
