import readchar
from subprocess import call, check_output
import argparse
import os
from os import listdir
from os.path import isfile, join
import re
import hashlib
import mocpdriver as player
import tts
import sys
    
appRunning = True
seekMinSpeedSec = 6 # seconds (Create a seekMaxSpeedSec later and do a variable speed)
musicDir = None
bookmark = None

appState = 'player' # '': player, ''

def main():
    global appRunning
    global appState
    player.init()
    while appRunning:
        c = readchar.readchar() # Or readchar.readkey()

        if(c == 'q'): # Usefull for development! Could be a command later
            appRunning = False
        else:
            playerScreen_ProcessKey(c);
            
        #print("You used: ", c)

        # call(["ls", "-l"])

def directAccess_ProcessKey(key):
    global appState
        
    if key == '.':
        print('\nDone direct access.')
        appState = 'player'
    else:
        sys.stdout.write(key)

def promptNumber(prompt):
    input = ''
    print(prompt + ':')
    while True:
        c = readchar.readchar() # Or readchar.readkey()

        if(c == '\r'): # Usefull for development! Could be a command later
            sys.stdout.write('\n')
            return (0, input)
        elif c == '.':
            sys.stdout.write('\n')
            return (1, input)
        elif c == '\b' or ord(c) == 127: # Backspace or Del
            sys.stdout.write('\n')
            return (-1, '')
        elif c.isdigit():
            input = input + c
            sys.stdout.write(c)
    
    
        
def playerScreen_ProcessKey(key):
    global bookmark
    global appState
    
    if(key == '\r' or key == ' '):
        print('Play/Pause')
        player.togglePlayPause()

    elif(key == '2'):
        print('Previous song')
        player.previousSong()
    elif(key == '3'):
        print('Next song')
        player.nextSong()

    elif(key == '5'):
        print('<< ' + str(seekMinSpeedSec) + ' sec')
        player.rr(seekMinSpeedSec)
    elif(key == '6'):
        print('>> ' + str(seekMinSpeedSec) + ' sec')
        player.ff(seekMinSpeedSec)

    elif(key == '1'): # set bookmark
        info = player.getState()
        print('Set bookmark at ' + str(info['currentTime']) + 'sec')
        bookmark = info['currentTime']

    elif(key == '0'): # play bookmark
        print('Play bookmark at ' + str(bookmark) + 'sec')
        player.jumpAt(bookmark)

    elif(key == '8'): # Previous album
        # Get the current plying song info
        info = player.getState()
        if(info != None):
            currentSongInfo = parseSongFilePath(info['file'])
            if currentSongInfo != None:
                # Get the album list for the artist
                albums = getAlbums(currentSongInfo['artist'])
                
                # Find the current album index, sub 1
                albumI = albums.index(currentSongInfo['album'])
                prevAlbumI = getPrevI(albumI, len(albums))
                prevAlbum = albums[prevAlbumI]
                print('Previous album (' + numHash(prevAlbum) + ') ' + prevAlbum)

                # Start the first song in it
                player.playDir(join(musicDir, currentSongInfo['artist'], prevAlbum))
            else:
                print('no file, starting somewhere!')
                playFirstSongOfAll()
        else:
            print('No info about the current song')
    elif(key == '9'): # Next album
        # Get the current plying song info
        info = player.getState()
        if(info != None):
            currentSongInfo = parseSongFilePath(info['file'])

            if currentSongInfo != None:
                # Get the album list for the artist
                albums = getAlbums(currentSongInfo['artist'])

                # Find the current album index, sub 1
                albumI = albums.index(currentSongInfo['album'])
                nextAlbumI = getNextI(albumI, len(albums))
                nextAlbum = albums[nextAlbumI]
                print('Next album  (' + numHash(nextAlbum) + ') ' + nextAlbum)    

                # Start the first song in it
                player.playDir(join(musicDir, currentSongInfo['artist'], nextAlbum))
            else:
                print('no file, starting somewhere!')
                playFirstSongOfAll()
        else:
            print('No info about the current song')

    elif(key == '4'): # Previous artist
        # Get the current playing song info
        currentSongInfo = None
        info = player.getState()
        artist = ''
        if(info != None):
            currentSongInfo = parseSongFilePath(info['file'])
        if(currentSongInfo != None):
            artist = currentSongInfo['artist']
            
        nextArtist = findNextPlayableArtist(artist, True)
            
        print('Previous artist (' + numHash(nextArtist) + ') ' + nextArtist)           
        albums = getAlbums(nextArtist)
        player.playDir(join(musicDir, nextArtist, albums[0]))

    elif(key == '7'): # Next artist
        # Get the current playing song info
        currentSongInfo = None
        info = player.getState()
        artist = ''
        if(info != None):
            currentSongInfo = parseSongFilePath(info['file'])
        if(currentSongInfo != None):
            artist = currentSongInfo['artist']
            
        nextArtist = findNextPlayableArtist(artist, False)
            
        print('Next artist (' + numHash(nextArtist) + ') ' + nextArtist)           
        albums = getAlbums(nextArtist)
        player.playDir(join(musicDir, nextArtist, albums[0]))
        
    elif(key == '.'):
        artistNumSel = promptNumber('Artist #')

        if artistNumSel[0] == -1:
            return

        # The user can enter no artist in order to chose an other album in the current artist
        artist = ''
        if len(artistNumSel[1]) == 0: # If no artist specified
            if artistNumSel[0] == 1: # If user want to selectthe album
                info = player.getState()
                if info != None:
                    currentSongInfo = parseSongFilePath(info['file'])
                    if currentSongInfo != None:
                        artist = currentSongInfo['artist']
        else:
            artist = findArtistByNumber(artistNumSel[1]) # Try to find our artist
        
        if len(artist) == 0:
            return

        albums = getAlbums(artist)
        if len(albums) == 0:
            return
            
        if artistNumSel[0] == 0: # The user wants to play this artist
            album = albums[0]
            player.playDir(join(musicDir, artist, album)) # Play first album
            print('Playing ' + artist + ' - ' + album)
        elif artistNumSel[0] == 1: # User want to select the album for this artist
            for album in albums:
                print(numHash(album) + ' ' + album) # Print choices
                
            albumNumSel = promptNumber('Album #')
            if albumNumSel[0] == 0 or albumNumSel[0] == 1: # The user wants to play this artist
                album = findAlbumByNumber(artist, albumNumSel[1])
                if len(album) == 0:
                    return
                
                player.playDir(join(musicDir, artist, album))                
                print('Playing ' + artist + ' - ' + album)

        #print('Looking artist #' + str(num))

    elif(key == '/'):
        cmdSel = promptNumber('Cmd #')
        if cmdSel[0] == 0 or cmdSel[0] == 1:
            cmd = cmdSel[1]
            
            if cmd == '1': # Identify song
                sayCurrentSong()
            elif cmd == '701':
                call(['git', 'pull'])
            elif cmd == '999':
                call(['reboot'])
            elif cmd == '991':
                sys.exit(0)


        
def findNextPlayableArtist(currentArtist, reverse):
    # Try to find the current artists index.
    artists = getArtists()

    # Find the current album index, sub 1
    currentArtistI = indexOf(artists, currentArtist)
    
    # If the artist is not found in the list, let's set default values
    if(currentArtistI == -1):
        print('Current playing artist not found. Playing default stuff.')
        if(reverse):
            currentArtistI = 0
        else:
            currentArtistI = len(artists) - 1
            
    # Loop through artists until it makes sense
    nextArtistI = getPrevI(currentArtistI, len(artists)) if reverse else getNextI(currentArtistI, len(artists))
    
    while nextArtistI != currentArtistI:
        nextArtist = artists[nextArtistI]
        albums = getAlbums(nextArtist)
        if(len(albums) > 0):
            return nextArtist
        else:
            print(nextArtist + ' has no albums')
        nextArtistI = getPrevI(nextArtistI, len(artists)) if reverse else getNextI(nextArtistI, len(artists))

def findArtistByNumber(artistNum):
    return findHashNum(getArtists(), artistNum)

def findAlbumByNumber(artist, albumNum):
    # Try to find the current artists index.
    return findHashNum(getAlbums(artist), albumNum)

def sayCurrentSong():
    info = player.getState()
    if(info != None):
        if info['state'] == 'PLAYING':
            currentSongInfo = parseSongFilePath(info['file'])
            if currentSongInfo != None:
                str = tts.formatSongID(getSongID(currentSongInfo['artist'], currentSongInfo['album'])) + '. ' + currentSongInfo['artist'] + '. ' + currentSongInfo['album'] + '. ' + currentSongInfo['song']
                print(str)                                       
                player.pause()
                tts.say(str)
                player.play()

def getSongID(artist, album):
    return numHash(artist)[0:4] + '.' + numHash(album)[0:4]


def findHashNum(list, num):
    for item in list:
        hash = numHash(item)
        if hash.startswith(num):
            return item
    return ''

    
def indexOf(list, item):
    try:
        return list.index(item)
    except:
        return -1
        
def getNextI(curI, itemCount):
    if(curI == itemCount - 1):
        return 0
    else:
        return curI + 1

def getPrevI(curI, itemCount):
    if(curI == 0):
        return itemCount - 1
    else:
        return curI - 1

def playFirstSongOfAll():
    artists = getArtists()
    for artist in artists:
        albums = getAlbums(artist)
        if(len(albums) > 0):
            call(['mocp', '-c', '-a', '-p', join(musicDir, artist, albums[0])])
            break;


def getArtists():
    # Get all files in the folder
    return sorted([f for f in listdir(musicDir) if not isfile(join(musicDir, f))])

def getAlbums(artist):
    artistFolder = join(musicDir, artist)
    return sorted([f for f in listdir(artistFolder) if not isfile(join(artistFolder, f))])

def parseSongFilePath(filePath):
    # If the file path is under our music folder
    if filePath[0:len(musicDir)] == musicDir:
        detailPart = filePath[len(musicDir)+1:]
        parts = detailPart.split('/')
        if(len(parts) == 3):
            return { 'artist': parts[0], 'album': parts[1], 'song': parts[2] }
    return None

def numHash(name):
    hash = hashlib.sha224(name).hexdigest()
    return filter(lambda c: c.isdigit(), hash)[0:6]

if __name__ == '__main__':
    

    parser = argparse.ArgumentParser()
    parser.description = "This is an interactive tool that controls Moc Player using a simple numpad."
    parser.add_argument('-d', '--dir', help='Main music directory', required=True) 
    args = parser.parse_args()

    musicDir = args.dir
    if musicDir[-1] == '/':
        musicDir = musicDir[:-1]
        
    print('Playing music from ' + musicDir)

    for artist in getArtists():
        print(numHash(artist) + ' ' + artist)
    
    main()








# Loop and do the job
#regex = re.compile(r'\d{' + str(args.digit_count) + '}')

# Copy to temp files so we don't override our source list!
# for file in sorted(files):
#     if regex.search(file) != None: # Don't process the files that don't fit the regex
#         intermedFile = regex.sub(('_{:0' + str(args.digit_count)  + 'd}_').format(newI), file)
#         endFile = regex.sub(('{:0' + str(args.digit_count)  + 'd}').format(newI), file)
#         intermedFiles.append((intermedFile, endFile))
#         newI += 1

#         if args.rename:
#             os.rename(file, intermedFile)
#         else:
#             print("mv " + file + " " + intermedFile )

# # Reconvert tmp files to new files
# for fileT in intermedFiles:
#     if args.rename:
#         os.rename(fileT[0], fileT[1])
#     else:
#         print("mv " + fileT[0] + " " + fileT[1] )
