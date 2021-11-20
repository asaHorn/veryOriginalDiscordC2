###

###
import shlex
from subprocess import Popen, PIPE

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')


@bot.command()
async def run(ctx, *args):
    cmd = ''
    for bit in args:
        cmd += bit + ' '
    print('USR CMD: ' + cmd)
    command = shlex.split(cmd)
    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    stdout = stdout.decode("utf-8")

    print('----returns----')
    print(stdout)
    await ctx.send('```' + str(stdout) + '```')

f = open('secrets.txt')
secret = f.read()
bot.run(secret)
