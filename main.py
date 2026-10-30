import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import requests

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())

    async def setup_hook(self):
        await self.tree.sync()
        print("Na-sync na ang Slash Commands!")

bot = MyBot()

GROUP_ID = 1028127753
GROUP_LINK = "https://www.roblox.com/communities/1028127753/disle#!/about"
GROUP_NAME = "disle"

@bot.event
async def on_ready():
    print(f"Online na ang bot mo bilang: {bot.user}")

@bot.tree.command(name="eligible", description="I-check ang eligibility at group status ng Roblox account")
@app_commands.describe(username="Ilagay ang Roblox Username ng iche-check")
async def eligible(interaction: discord.Interaction, username: str):
    await interaction.response.defer()

    try:
        user_res = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [username], "excludeBannedUsers": True}
        ).json()

        if not user_res.get("data") or len(user_res["data"]) == 0:
            await interaction.followup.send(f"❌ Hindi mahanap ang Roblox user na `{username}`.")
            return

        user_data = user_res["data"][0]
        user_id = user_data["id"]
        display_name = user_data["name"]

        group_res = requests.get(f"https://groups.roblox.com/v1/users/{user_id}/groups/roles").json()
        
        is_eligible = False
        status_text = "Not in Group"

        if "data" in group_res:
            for group_item in group_res["data"]:
                if group_item["group"]["id"] == GROUP_ID:
                    is_eligible = True
                    status_text = "Eligible"
                    break

        avatar_res = requests.get(
            f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={user_id}&size=150x150&format=Png&isCircular=false"
        ).json()
        
        avatar_url = ""
        if "data" in avatar_res and len(avatar_res["data"]) > 0:
            avatar_url = avatar_res["data"][0]["imageUrl"]

        embed = discord.Embed(
            title=display_name,
            color=discord.Color.dark_theme()
        )
        
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)

        embed.description = f"**{GROUP_NAME}** : {status_text}"

        view = View()
        button = Button(
            label="Join our Roblox Group",
            url=GROUP_LINK,
            style=discord.ButtonStyle.link
        )
        view.add_item(button)

        await interaction.followup.send(embed=embed, view=view)

    except Exception as e:
        await interaction.followup.send(f"Nagkaroon ng error sa pag-check: {e}")

token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
