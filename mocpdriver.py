
from subprocess import call, check_output

def init():
    #pState = getState()
    call(['mocp', '-o', 'REPEAT']) # Set REPEAT, very important so the player doesn't stop when we go out of list

def togglePlayPause():
    call(['mocp', '-G']) # toggle play pause

def play():
    call(['mocp', '-U'])

def pause():
    call(['mocp', '-P'])

    
def setVolume(integerPercentage):
    call(['mocp', '-v' + str(integerPercentage) + '%'])

def previousSong():
    call(['mocp', '-r']) # Previous song

def nextSong():
    call(['mocp', '-f']) # Next song

def ff(sec):
    call(['mocp', '-k' + str(sec)]) # seek

def rr(sec):
    call(['mocp', '-k-' + str(sec)]) # seek
        
def jumpAt(sec):

    # We would normally do the following call. But currently, moc player as a Segmentation
    # fault on this command and on all versions on all OS...
    # In the meantime, I do it by hand
    # call(['mocp', '-j' + str(sec)]) # Jump

    # Ge thte current position
    info = getState()
    if info and info['state'] == 'PLAYING':
        ct = info['currentTime']
        step = sec - ct
        call(['mocp', '-k' + str(step)])
    
    
def playDir(dirPath):
    # Start the first song in it
    call(['mocp', '-c', '-a', '-p', dirPath])

def playSong(num):
    # Start the first song in it
    # call(['mpc', 'play', str(num)])

# { state: 'DOWN|STOPPED|PLAYING', file: '', currentTime: ''}
def getState():
    mocpInfoStr = check_output(['mocp', '-i'])
    lines = mocpInfoStr.split('\n')
    retInfo = { 'state': 'DOWN', 'file': '', 'currentTime': 0 }
    for line in lines:
        lineTup = splitMocpInfoLine(line)
        if(lineTup[0] == 'File'):
            retInfo['file'] = lineTup[1]
        elif(lineTup[0] == 'CurrentTime'):
            retInfo['currentTime'] = timeInSec(lineTup[1])
        elif(lineTup[0] == 'FATAL_ERROR'):
            retInfo['state'] = 'DOWN'
        elif(lineTup[0] == 'State'):
            retInfo['state'] = 'PLAYING' if lineTup[1] == 'PLAY' else 'STOPPED'
        
    return retInfo


def timeInSec(timeStr):
    t = timeStr.split(':')
    return (int(t[0]) * 60) + int(t[1])


def splitMocpInfoLine(line):
    i = line.find(': ') # We do that instead of a split because we don't want trouble with potential :
    if(i == -1):
        return ('', line)
    else:
        return (line[0:i], line[i+2:])




