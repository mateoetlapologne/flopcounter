import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
from datetime import datetime, timedelta

TOKEN = "token" 
JSON_FILE = "bdd.json"

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="/", intents=intents)

db = {}

def load_database():
    try:
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_database(data):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_database()

@bot.tree.command(name="flop", description="Lancer un sondage pour savoir si un mec vient de flop")
async def flop(interaction: discord.Interaction, user: discord.Member):
    poll_message = await interaction.response.send_message(f"{interaction.user.mention} veus savoir si {user.mention} a flop. Est-ce un flop ?\nFin du sondage dans 10 minutes\n✅ : Oui\n❌ : Non", ephemeral=False)
    poll_message = await interaction.original_response()
    await poll_message.add_reaction("✅")
    await poll_message.add_reaction("❌")
    await asyncio.sleep(600)
    poll_message = await interaction.channel.fetch_message(poll_message.id)
    reactions = {reaction.emoji: reaction.count - 1 for reaction in poll_message.reactions}

    yes_votes = reactions.get("✅", 0)
    no_votes = reactions.get("❌", 0)
    total_votes = yes_votes + no_votes

    if total_votes <= 2:
        await interaction.followup.send(f"Pas assez de votes pour déterminer si {user.mention} a flop.")
        return

    yes_percentage = (yes_votes / total_votes) * 100

    if yes_percentage > 50:
        await interaction.followup.send(f"la vanne de {user.mention} est un flop a (✅ {yes_percentage:.2f}% de votes) !")
        user_id = str(user.id)
        if user_id not in db:
            db[user_id] = 0
        db[user_id] += 1
        save_database(db)
    else:
        await interaction.followup.send(f"La communauté a décidé : {user.mention} n'est pas un flop (✅ {yes_percentage:.2f}% de votes).")

@bot.tree.command(name="voirlesflops", description="Consulter le nombre de flops d'un mec")
async def voirlesflops(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    user_id = str(user.id)
    flop_count = db.get(user_id, 0)
    if flop_count == 0:
        await interaction.response.send_message(f"{user.mention} n'a jamais flop, masterclass de sa part")
    elif flop_count > 30:
        await interaction.response.send_message(f"{user.mention} commence à trop flop la c'est plus possible , il a flop {flop_count} fois.")
    elif flop_count > 50:
        await interaction.response.send_message(f"{user.mention} a flop {flop_count} fois. VOUS VOUS RENDEZ COMPTE OH LE FLOPEUR ORIGINEL")
    else :
        await interaction.response.send_message(f"{user.mention} a flopé {flop_count} fois.")


@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    await bot.tree.sync()

bot.run(TOKEN)
