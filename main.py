###

###
import os

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')


@bot.command()
async def run(ctx, *args):
    command = ""
    for word in args:
        command += word + ' '
    os.system(command)


f = open('secrets.txt')
secret = f.read()
bot.run(secret)
