
from subprocess import call, check_output


def say(text):
    call(['espeak', text])

def formatSongID(songID):
    return ' '.join(songID).replace('.', 'dot')
