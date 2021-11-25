# veryOriginalDiscordC2
My 100% own idea please don't steal attempt to make a discord based C2.

Command.py is the commmand server, it accepts incoming beacons on port 22704 and sets up channels in a discord server 
to send remote input to the machine and download files from it. It then uses discord.py to interfece with those channels.

Payload.py is my implementation of a reverse shell working on port 22507 which uses python's pipen to execute arbatrary commands on the target system
This theoretically could be replaced with a better reverse shell program to be more stealthy, have more features, and generally be
better.
