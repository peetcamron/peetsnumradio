
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
    call(['mocp', '-j' + str(sec)]) # Jump

def playDir(dirPath):
    # Start the first song in it
    call(['mocp', '-c', '-a', '-p', dirPath])
        
# { state: 'DOWN|STOPPED|PLAYING', file: '', currentTimeSec: ''}
def getState():
    mocpInfoStr = check_output(['mocp', '-i'])
    lines = mocpInfoStr.split('\n')
    retInfo = { 'state': 'DOWN', 'file': '', 'currentTimeSec': 0 }
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




