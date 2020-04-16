#!/usr/bin/python3

import sys
import json
import time
import socket
import logging
import threading
import os.path
import urllib.parse
import pychromecast

from cmd import Cmd
from flask import Flask, send_file, request, make_response

STATE_PLAYING = 1
STATE_STOPPED = 2
STATE_PAUSED = 3

cast = None
my_ip = None
cc_ip = None
my_port = 63915
stopFlag = None
loop = None
volume = 0.25
now_playing = None
user_state = STATE_STOPPED 
play_queue = []
play_thread = None
stream_server = None
conf_dir = os.path.join(os.getenv('HOME'),'.gcastctl')
history = os.path.join(conf_dir,'history')
resume = 0

def probe_cc():
    global cc_ip
    global my_ip
    for i in range(100,110):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        ip = f'192.168.0.{i}'
        print(f'Probing {ip}')
        err = sock.connect_ex((ip,8009))
        if err == 0:
            cc_ip = ip
            my_ip = sock.getsockname()[0] 
        sock.close()
        if cc_ip:
            break

class StreamServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        app = Flask(__name__)

        @app.route('/play')
        def serve_chromecast():
            try:
                filename = urllib.parse.unquote(request.args.get("name"))
                response = make_response(send_file(filename))
                response.headers['Accept-Ranges'] = 'bytes'    # This is important to let Chromecast support seek method.
                return response
            except Exception as e:
                return str(e)
             
        app.run(host='0.0.0.0',port=my_port)

class PlayThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        global resume
        global now_playing
        global user_state
        while play_queue and not self.stopped.isSet():
            now_playing = s = play_queue.pop(0)
            print(s)
            s = urllib.parse.quote(s,safe="")
            print(f'http://{my_ip}:{my_port}/play?name={s}')
            cast.play_media(f'http://{my_ip}:{my_port}/play?name={s}', "audio/mp3", current_time = resume)
            if resume: # true when restoring last playing session
               resume = 0
            self.stopped.wait(3) # in case the thread is starting too fast
            try:
              '''
              Monitor playing status. Break when
               1. stop command is issued
               2. current song finished
               3. Chromecast aborts the playing (e.g. being paused too long or another device takes the control) 
              Known issue: 2 and 3 have the same condition. I can't distinguish them.
              '''
              while not self.stopped.wait(1) and (cast.media_controller.is_playing or cast.media_controller.is_paused):
                now = int(cast.media_controller.status.adjusted_current_time or 0)
                if loop:
                    if now > loop[1]: cast.media_controller.seek(loop[0])
                elif now % 30 == 0:
                    save_session()
            except Exception as e:
                print(f'Got Exception: {e}')
                # don't save session because current_time may not be available now.
                break
            if not cast.media_controller.is_paused and user_state is STATE_PAUSED:
                '''
                Chromecast seems to stop the playing after pausing for more than
                about 20 minutes. Break since we've lost the control of Chromecast.

                By restoring the last saved session user can continue with play command.
                However this still cannot solve the problem when user does not pause before
                this happened.
                '''
                restore_session()
                print("Chromecast stopped the playing.")
                break
            else:
                save_session()
        if not play_queue:
            print("End of playlist.")

def save_session(filename=history):
    global now_playing
    global play_queue
    global history
    global resume
    global user_state
    save_queue = []
    save_queue.extend(play_queue)
    #print(f'save_session: is_playing {cast.media_controller.is_playing}, is_paused {cast.media_controller.is_paused}')
    if user_state in (STATE_PLAYING, STATE_PAUSED):
        save_queue.insert(0,now_playing)
        resume = int(cast.media_controller.status.adjusted_current_time or 0)
    with open(filename,'w') as f:
        json.dump({'timestamp': resume, 'queue': save_queue},f)
    resume = 0

def restore_session(filename=history):
    global resume
    global play_queue
    global conf_dir
    try:
        with open(filename,'r') as f:
            try:
                d = json.load(f)
                resume = d['timestamp']
                play_queue = d['queue']
            except:
                pass
    except FileNotFoundError:
        if not os.path.isdir(conf_dir):
            os.mkdir(conf_dir)

def show_device_info():
    print(f'{cast.device}\n')
    print(f'{cast.status}\n')
    print(cast.media_controller.status)

def show_status():
    now = int(cast.media_controller.status.adjusted_current_time or 0)
    total = int(cast.media_controller.status.duration or 0)
    now_s = time.strftime("%H:%M:%S",time.gmtime(now))
    total_s = time.strftime("%H:%M:%S",time.gmtime(total))
    print(f'{now}/{total}({now_s}/{total_s})')

def stop_play_thread():
    global stopFlag
    global play_thread
    if stopFlag:
        stopFlag.set()
    if play_thread:
        play_thread.join()

def to_seconds(s):
    t = s.split(':')
    t.reverse()
    ts = 0
    for i in range(len(t)):
        ts += int(t[i])*60**i
    return ts

class MyPrompt(Cmd):
    prompt = 'cc> '
    intro = "Welcome! Type ? to list commands"
     
    def do_exit(self, s):
        global play_thread
        global stream_server
        global now_playing
        '''
        Unlike do_stop, need to terminate thread before telling controller to stop
        so as to save current playing status.
        '''
        stop_play_thread()
        cast.media_controller.stop()
        self.do_volume(0.95)
        cast.disconnect()
        print("Bye")
        return True
        
    def do_volume(self, s):
        global volume
        if s:
            volume = float(s)
            cast.set_volume(volume)
        else:
            print(f'Volume = {volume}')

    def do_play(self, s):
        global stopFlag
        global play_queue
        global play_thread
        global user_state
        user_state = STATE_PLAYING
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

    def do_pause(self, s):
        global user_state
        user_state = STATE_PAUSED
        cast.media_controller.pause()
        time.sleep(.25)
        save_session()
        show_status()

    def do_stop(self, s):
        global user_state
        user_state = STATE_STOPPED
        show_status()
        cast.media_controller.stop()
        time.sleep(.25)
        stop_play_thread()

    def do_repeat(self, s):
        global loop
        if s == 'stop':
            loop = None
            return
        try:
            loop = [ to_seconds(i.strip()) for i in s.split(',') ]
            if len(loop) != 2 or loop[0] >= loop[1]:
                raise
        except:
            self.help_repeat()
        return

    def help_repeat(self):
        print("Usage: repeat 1:20,1:40 or repeat stop.")

    def do_next(self, s):
        self.do_play('')

    def do_seek(self, s):
        ts = to_seconds(s)
        cast.media_controller.seek(ts)

    def do_queue(self, s):
        if len(s):
            if os.path.isfile(s):
                if s.lower().endswith('mp3'):
                    play_queue.append(s)
                else:
                    with open(s) as f:
                        play_queue.extend([line.strip() for line in f])
            elif s == 'clear':
                play_queue.clear()
                resume = 0
            else:
                pass
        else:
            for q in play_queue:
                print(q)

    def help_queue(self):
        print("Add a song or a file containing list of songs to playing queue.")

    def do_save(self, s):
        global config_dir
        if -1 == s.find('/'):
            s = os.path.join(conf_dir,s)
        save_session(s)
        pass

    def do_load(self, s):
        global config_dir
        if -1 == s.find('/'):
            s = os.path.join(conf_dir,s)
        restore_session(s)
        pass

    def do_debug(self, s):
        #TODO
        pass

    def do_show(self, s):
        show_device_info()

    def do_status(self, s):
        show_status()

    def default(self, s):
        if s == 'q':
           return self.do_exit(s)
        elif s == 'c':
           return self.do_play('')
        print("Unknown command: {}".format(s))
     
    do_EOF = do_exit
     
if __name__ == '__main__':
    '''
    start, exit
    start, play, exit
    start, play, pause, exit
    start, play, stop, exit
    start, play, pause, stop, play, exit 

    Whenever stop is issued, now_playing should not be saved.
    '''
    # my_ip = socket.gethostbyname(socket.gethostname()) always returns 127.0.0.1.
    probe_cc()
    if cc_ip:
        cast = pychromecast.Chromecast(cc_ip)
    if not my_ip:
       my_ip = socket.gethostbyname(socket.gethostname()+'.local')
    if cast is None:
        casts = pychromecast.get_chromecasts()
        if len(casts):
            cast = casts[0]
        else:
            print("No Devices Found")
            exit()
    cast.start()
    show_device_info()
    time.sleep(1)
    cast.set_volume(volume)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    stream_server = StreamServer()
    stream_server.setDaemon(True)
    stream_server.start()

    restore_session()
    MyPrompt().cmdloop()

