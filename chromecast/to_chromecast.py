#!/usr/bin/python3

import sys
import time
import socket
import threading
import os.path
import urllib.parse
import pychromecast

from cmd import Cmd

cast = None
my_ip = None
cc_ip = None
my_port = 5000
stopFlag = None
play_queue = []
play_thread = None

def probe_cc():
    global cc_ip
    global my_ip
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    for i in range(101,110):
        cc_ip = f'192.168.0.{i}'
        print(f'Probing {cc_ip}')
        err = sock.connect_ex((cc_ip,8009))
        if err == 0:
            my_ip = sock.getsockname()[0] 
            break
    sock.close()
    if err: cc_ip = None

class PlayThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        while play_queue and not self.stopped.isSet():
            s = play_queue.pop(0)
            print(s)
            s = urllib.parse.quote(s,safe="")
            print(f'http://{my_ip}:{my_port}/play?name={s}')
            cast.play_media(f'http://{my_ip}:{my_port}/play?name={s}', "audio/mp3")
            self.stopped.wait(3) # in case the thread is starting too fast
            while not self.stopped.wait(1) and (cast.media_controller.is_playing or cast.media_controller.is_paused):
                pass
        if not play_queue:
            print("End of playlist.")

def show_status():
    now = int(cast.media_controller.status.adjusted_current_time)
    total = int(cast.media_controller.status.duration)
    now_s = time.strftime("%H:%M:%S",time.gmtime(now))
    total_s = time.strftime("%H:%M:%S",time.gmtime(total))
    print(f'{now}/{total}({now_s}/{total_s})')

def stop_play_thread():
    global stopFlag
    if stopFlag:
        stopFlag.set()

class MyPrompt(Cmd):
    prompt = 'cc> '
    intro = "Welcome! Type ? to list commands"
     
    def do_exit(self, s):
        global play_thread
        self.do_stop(s)
        if play_thread:
            play_thread.join()
        cast.set_volume(0.95)
        cast.disconnect()
        print("Bye")
        return True
        
    def do_volume(self, s):
        cast.set_volume(float(s))

    def do_play(self, s):
        global stopFlag
        global play_queue
        global play_thread
        if len(s):
            play_queue.clear()
            play_queue.append(s)
        if play_queue and not cast.media_controller.is_paused:
            stop_play_thread()
            stopFlag = threading.Event()
            play_thread = PlayThread(stopFlag)
            play_thread.start()
        else:
            cast.media_controller.play()
            show_status()

    def help_play(self):
        print("Play a song or continue playing.")

    def do_next(self, s):
        self.do_play('')

    def do_seek(self, s):
        cast.media_controller.seek(s) # not work. don't know why.

    def do_queue(self, s):
        if len(s):
            if os.path.isfile(s) and not s.lower().endswith('mp3'):
                with open(s) as f:
                    play_queue.extend([line.strip() for line in f])
            else:
                play_queue.append(s)
        else:
            for q in play_queue:
                print(q)

    def help_queue(self):
        print("Add a song or a file containing list of songs to playing queue.")

    def do_pause(self, s):
        cast.media_controller.pause()
        show_status()

    def do_stop(self, s):
        show_status()
        #TODO: save current song and stop time to history and load it in next start.
        stop_play_thread()
        cast.media_controller.stop()

    def do_status(self, s):
        show_status()

    def default(self, s):
        if s == 'q':
           return self.do_exit(s)
        print("Unknown command: {}".format(s))
     
    do_EOF = do_exit
     
if __name__ == '__main__':
    # my_ip = socket.gethostbyname(socket.gethostname()) always returns 127.0.0.1.
    # my_ip = socket.gethostbyname(socket.gethostname()+'.local') returns 192.168.0.x. Put here for reference since getsockname also works.
    probe_cc()
    if cc_ip:
        cast = pychromecast.Chromecast(cc_ip)
    if cast is None:
        casts = pychromecast.get_chromecasts()
        if len(casts):
            cast = casts[0]
        else:
            print("No Devices Found")
            exit()
    cast.start()
    print(cast.device)
    print(cast.status)
    print(cast.media_controller.status)
    time.sleep(1)
    cast.set_volume(0.25)

    MyPrompt().cmdloop()

