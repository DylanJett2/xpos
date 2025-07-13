import discord
from discord import app_commands
import aiohttp
import os
import json
import firebase_admin
from firebase_admin import credentials, db

# Firebase credentials from ENV
firebase_config = json.loads(os.getenv("FIREBASE_JSON"))
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://xpos-whitelist-bot-default-rtdb.firebaseio.com/'
})

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

REQUIRED_ROLE_ID = 1391483639459479734

async def is_valid_roblox_user(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
            return resp.status == 200

@tree.command(name="givewhitelist", description="Give whitelist to a Roblox user")
@app_commands.describe(whitelist_type="Test-1 or Test-2", user_id="Roblox user ID")
async def givewhitelist(interaction: discord.Interaction, whitelist_type: str, user_id: str):
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("You don't have the required role.", ephemeral=True)
        return

    if whitelist_type not in ["Test-1", "Test-2"]:
        await interaction.response.send_message("Invalid whitelist type.", ephemeral=True)
        return

    if not user_id.isdigit() or not await is_valid_roblox_user(user_id):
        await interaction.response.send_message("Invalid Roblox user ID.", ephemeral=True)
        return

    ref = db.reference(f"/{whitelist_type}/whitelist")
    users = ref.get() or []
    if user_id in users:
        await interaction.response.send_message("User already whitelisted.", ephemeral=True)
    else:
        users.append(user_id)
        ref.set(users)
        await interaction.response.send_message(f"User {user_id} added to {whitelist_type}.", ephemeral=True)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

client.run(os.getenv("DISCORD_TOKEN"))
