import time
import curses
import sys
import numpy as np
from pathlib import Path
from ffpyplayer.player import MediaPlayer
from ffpyplayer.pic import Image, SWScale

parent_dir = Path(__file__).parent
videos_dir = parent_dir.joinpath('videos')

files = [file for file in videos_dir.iterdir() if not file.name.startswith('.')]


def transform(img, asciiToNum):
	transformedAscii = []
	for i in img:
		temp = []
		for j in i:
			temp.append(asciiToNum[j])
		transformedAscii.append(temp)
	return transformedAscii


def setupAsciiMapping():
	asciiToNum = {}
	characterSet = list('  ..,,::;;ii11ttffLL;;::00ii11ttL')
	for i in range(26):
		for j in range(10):
			asciiToNum[i*10+j] = characterSet[i]
	return asciiToNum


def arrayToString(arr):
	ascii = ''
	for i in arr:
		ascii += ' '.join(i)
		ascii += '\n'
	return ascii


def play(screen, asciiToNum, videoPath):
    player = MediaPlayer(videoPath)
    screen.nodelay(True)
    while 1:
        frame, val = player.get_frame()

        if val == 'eof':
            break
        elif frame is None:
            time.sleep(0.01)
        else:
            time_bf = time.time()
            c = screen.getch()
            if c == ord('q'):
                break
            img, t = frame
            w,h = img.get_size()
            sws = SWScale(w, h, img.get_pixel_format(), ofmt='yuv420p', ow=w//8, oh=h//8)
            img_scaled = sws.scale(img)
            frame_scaled = np.uint8(np.array(list(img_scaled.to_bytearray()[0]))).reshape(h//8,w//8)
            transformedAscii = transform(frame_scaled, asciiToNum)
            s =arrayToString(transformedAscii)
            time_af = time.time()
            screen.erase()
            screen.addstr(s)
            screen.addstr(str(t))
            screen.refresh()
            time.sleep( 0 if 0 > val-(time_af-time_bf) else val-(time_af-time_bf))
           
    player.close_player()

def _initPlay(screen):
	
	screen.addstr('\nPress ENTER to play video')
	c= screen.getch()
	if c == ord('q'):
		sys.exit(0)
	

def selectFile(screen):
	screen.addstr('Please choose the video: \n')
	for f in enumerate(files):
		screen.addstr('{}. {}\n'.format(*f))
	curses.echo()
	
	user_in = screen.getstr()

	try:
		alfa = int(user_in)
		name = files[alfa]
		video_path = name
	except:
		selectFile(screen)

	screen.refresh()
	video_relative = video_path.relative_to(videos_dir.parent)


	return str(video_relative)

def _main(screen):
	mapASCII = setupAsciiMapping()
	selected = selectFile(screen)
	_initPlay(screen)
	play(screen, mapASCII, selected)

if __name__ == "__main__":
	curses.wrapper(_main)
	curses.endwin()
