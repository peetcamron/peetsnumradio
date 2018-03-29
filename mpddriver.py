# MPD / MPC driver
from subprocess import call, check_output
import re

def init():
    None
    
def togglePlayPause():
    call(['mpc', 'toggle']) # toggle play pause

def play():
    call(['mpc', 'play'])

def pause():
    call(['mpc', 'pause'])

    
def setVolume(integerPercentage):
    call(['mpc', 'volume', str(integerPercentage)])

def previousSong():
    call(['mpc', 'cdprev']) # cdprev is like previous on a CD, it restarts the current song first

def nextSong():
    call(['mpc', 'next']) # Next song

def ff(sec):
    call(['mpc', 'seek', '+' + str(sec)]) # seek

def rr(sec):
    call(['mpc', 'seek', '-' + str(sec)]) # seek
        
def jumpAt(sec):
    call(['mpc', 'seek', str(sec)])
        
def playDir(dirPath):
    # Start the first song in it
    call(['mpc', 'clear'])
    call(['mpc', 'add', dirPath])
    call(['mpc', 'play'])

def playSong(num):
    # Start the first song in it
    call(['mpc', 'play', str(num)])
    
# { state: 'DOWN|STOPPED|PLAYING', file: '', currentTimeSec: ''}
def getState():
    retInfo = { 'state': 'DOWN', 'file': '', 'currentTime': 0 }
    infoStr = ''
    try:
        infoStr = check_output(['mpc', 'status'])
    except:
        return retInfo
    lines = infoStr.split('\n')
    

    # Artist - Song
    # [playing] #5/13   0:59/3:31  (27%)           (Possible values: [playing], [paused])
    # volume:100%   repeat: on   random: off   single: off    consume: off

    # If the first line is the volume, then it's stopped...
    if not lines[0].startswith('volume:'): # If playng or paused
        retInfo['file'] = lines[0]
        
        if lines[1].startswith('[playing]'):
            retInfo['state'] = 'PLAYING'
        else:
            retInfo['state'] = 'STOPPED'

        m = re.search('(\d?\d:\d\d)/\d?\d:\d\d', lines[1])
        if m != None:
            retInfo['currentTime'] = timeInSec(m.group(1))
                      
    return retInfo


def timeInSec(timeStr):
    t = timeStr.split(':')
    return (int(t[0]) * 60) + int(t[1])



