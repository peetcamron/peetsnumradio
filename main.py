import readchar
from subprocess import call, check_output
import argparse
import os
from os import listdir
from os.path import isfile, join
import re

appRunning = True
seekMinSpeedSec = 6 # seconds (Create a seekMaxSpeedSec later and do a variable speed)
musicDir = None
bookmark = None

def main():
    global appRunning
    while appRunning:
        c = readchar.readchar() # Or readchar.readkey()

        if(c == 'q'): # Usefull for development! Could be a command later
            appRunning = False
        else:
            playerScreen_ProcessKey(c);
            
        #print("You used: ", c)

        # call(["ls", "-l"])


def playerScreen_ProcessKey(key):
    global bookmark
    
    if(key == '\r'):
        print('Play/Pause')
        call(['mocp', '-G']) # Next song

    elif(key == '2'):
        print('Previous song')
        call(['mocp', '-r']) # Previous song
    elif(key == '3'):
        print('Next song')
        call(['mocp', '-f']) # Next song

    elif(key == '5'):
        print('<< ' + str(seekMinSpeedSec) + ' sec')
        call(['mocp', '-k-' + str(seekMinSpeedSec)]) # Next song
    elif(key == '6'):
        print('>> ' + str(seekMinSpeedSec) + ' sec')
        call(['mocp', '-k' + str(seekMinSpeedSec)]) # Next song

    elif(key == '1'): # set bookmark
        info = getMocPlayerInfo()
        print('Set bookmark at ' + info['currentTime'])
        bookmark = info['currentTime']

    elif(key == '0'): # play bookmark
        print('Play bookmark at ' + bookmark)

    elif(key == '8'): # Previous album
        # Get the current plying song info
        info = getMocPlayerInfo()
        if(info != None):
            currentSongInfo = parseSongFilePath(info['file'])
        
            # Get the album list for the artist
            albums = getAlbums(currentSongInfo['artist'])
            
            # Find the current album index, sub 1
            albumI = albums.index(currentSongInfo['album'])
            prevAlbumI = getPrevI(albumI, len(albums))
            prevAlbum = albums[prevAlbumI]
            print('Previous album ' + prevAlbum)
            # Start the first song in it
            call(['mocp', '-c', '-a', '-p', join(musicDir, currentSongInfo['artist'], prevAlbum)])
        else:
            print('No info about the current song')
    elif(key == '9'): # Next album
        # Get the current plying song info
        info = getMocPlayerInfo()
        if(info != None):
            currentSongInfo = parseSongFilePath(info['file'])
        
            # Get the album list for the artist
            albums = getAlbums(currentSongInfo['artist'])

            # Find the current album index, sub 1
            albumI = albums.index(currentSongInfo['album'])
            nextAlbumI = getNextI(albumI, len(albums))
            nextAlbum = albums[nextAlbumI]
            print('Next album ' + nextAlbum)    
            # Start the first song in it
            call(['mocp', '-c', '-a', '-p', join(musicDir, currentSongInfo['artist'], nextAlbum)])
        else:
            print('No info about the current song')

    elif(key == '4'): # Previous artist
        # Get the current playing song info
        currentSongInfo = None
        info = getMocPlayerInfo()
        artist = ''
        if(info != None):
            currentSongInfo = parseSongFilePath(info['file'])
        if(currentSongInfo != None):
            artist = currentSongInfo['artist']
            
        nextArtist = findNextPlayableArtist(artist, True)
            
        print('Next artist ' + nextArtist)           
        albums = getAlbums(nextArtist)
        call(['mocp', '-c', '-a', '-p', join(musicDir, nextArtist, albums[0])])

    elif(key == '7'): # Next artist
        # Get the current playing song info
        currentSongInfo = None
        info = getMocPlayerInfo()
        artist = ''
        if(info != None):
            currentSongInfo = parseSongFilePath(info['file'])
        if(currentSongInfo != None):
            artist = currentSongInfo['artist']
            
        nextArtist = findNextPlayableArtist(artist, False)
            
        print('Next artist ' + nextArtist)           
        albums = getAlbums(nextArtist)
        call(['mocp', '-c', '-a', '-p', join(musicDir, nextArtist, albums[0])])
        
    elif(key == '.'):
        getMocPlayerInfo()

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
                    
def getMocPlayerInfo():
    mocpInfoStr = check_output(['mocp', '-i'])
    lines = mocpInfoStr.split('\n')
    retInfo = {}
    for line in lines:
        lineTup = splitMocpInfoLine(line)
        if(lineTup[0] == 'File'):
            retInfo['file'] = lineTup[1]
        elif(lineTup[0] == 'CurrentTime'):
            retInfo['currentTime'] = lineTup[1]                
        
    #print(retInfo)
    return retInfo

def splitMocpInfoLine(line):
    i = line.find(': ') # We do that instead of a split because we don't want trouble with potential :
    if(i == -1):
        return ('', line)
    else:
        return (line[0:i], line[i+2:])


def getArtists():
    # Get all files in the folder
    return [f for f in listdir(musicDir) if not isfile(join(musicDir, f))]

def getAlbums(artist):
    artistFolder = join(musicDir, artist)
    return [f for f in listdir(artistFolder) if not isfile(join(artistFolder, f))]

def parseSongFilePath(filePath):
    # If the file path is under our music folder
    if filePath[0:len(musicDir)] == musicDir:
        detailPart = filePath[len(musicDir)+1:]
        parts = detailPart.split('/')
        if(len(parts) == 3):
            return { 'artist': parts[0], 'album': parts[1], 'song': parts[2] }
    return None

if __name__ == '__main__':
    global musicDir

    parser = argparse.ArgumentParser()
    parser.description = "This is an interactive tool that controls Moc Player using a simple numpad."
    parser.add_argument('-d', '--dir', help='Main music directory', required=True) 
    args = parser.parse_args()

    musicDir = args.dir
    if musicDir[-1] == '/':
        musicDir = musicDir[:-1]
        
    print('Playing music from ' + musicDir)
    
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
