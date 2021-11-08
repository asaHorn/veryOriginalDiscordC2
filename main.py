###

###
import os

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')


@bot.command()
async def run(ctx, *args):
    os.system("echo hi there")


f = open('secrets.txt')
secret = f.read()
bot.run(secret)
