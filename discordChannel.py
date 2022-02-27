class discordChannel:
    currentDir = ''
    ID = ''
    IP = ''
    humanName = ''
    heartBeatResponse = True
    alive = True

    def __init__(self, chanID=''):
        self.ID = chanID
        self.currentDir = '/'
