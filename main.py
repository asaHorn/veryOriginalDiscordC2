###

###
import os

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')


@bot.command()
async def run(ctx, *args):
    os.system('powershell [console]::beep(500,300)')


f = open('secrets.txt')
secret = f.read()
bot.run(secret)
