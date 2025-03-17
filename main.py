import tkinter as tk
from tkinter import ttk, filedialog
from song import Song
from tooltip import Tooltip
import os
import pygame.mixer as pygm
from PIL import Image, ImageTk
import io
import re
import random
import sys
from pynput import keyboard

ASSETS_DIR = None

if getattr(sys, 'frozen', False):
    ASSETS_DIR = sys._MEIPASS
else:
    ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

isplaying = False
isshuffle = False
timer = 0
directories = []
played_songs = []
playlist = []
song_index = 0
songs_counter = 0
cur_song  = None
song_lrc = []
lrc_index = -1
lrc_time = []
cur_song_cover = None 
after_id = None
num_lines = 6
lrc_displays = []

def get_cover_tk(imageData):
        if not imageData:
            imageData = ASSETS_DIR + "\\assets\\cover.png"

        if isinstance(imageData, bytes):  
            imageData = io.BytesIO(imageData) 
        image = Image.open(imageData)
        image = image.resize((100, 100))
        image = ImageTk.PhotoImage(image)
        return image

def toggle_shuffle():
    global isshuffle
    isshuffle = not isshuffle
    if isshuffle:
        toggle_shuffle_button.config(relief='sunken')
    else:
        toggle_shuffle_button.config(relief='raised')

def toggle_play():
    if isplaying:
        pause()
    else:
        play()

def pause():
    global isplaying
    if isplaying:
        pygm.music.pause()
        isplaying = False
        start_pause_button.config(text = '>',command= play)

def play():
    global isplaying
    if cur_song: 
        pygm.music.unpause()
        if after_id : 
            root.after_cancel(after_id)
        isplaying = True
        teck()
        pygm.music.set_pos(timer/10)
        start_pause_button.config(text = '||',command= pause)

def load_song():
    global timer
    pygm.music.load(cur_song.file_path)
    pygm.music.play()
    pygm.music.pause()
    timer = 0


def update_timer(timer_):
    timer_sec = (timer_ % 600) // 10
    timer_min = timer_ // 600
    cur_time.config(text=f"{int(timer_min):02}:{round(timer_sec):02}")
    prograss_bar.config(value=timer/10)

def teck():
    global timer ,after_id
    if isplaying:
        timer += 1
        update_timer(timer)
        if timer/10 > cur_song.duration:
            next_song()
            root.after_cancel(after_id)
        after_id = root.after(100,teck)
        if song_lrc:
            update_lrc()

def on_pos_change(value):
    global timer
    timer = float(value)*10
    update_timer(timer)

def on_slider_release(e):
    if isplaying:
        pygm.music.unpause()
        pygm.music.set_pos(float(timer)/10)
        teck()
    if song_lrc:
        get_cur_lrc()
        update_lrc_display()

def on_slider_press(e):
    if isplaying:
        pygm.music.pause()
        if after_id:
            root.after_cancel(after_id)

def on_volume_change(value):
    pygm.music.set_volume(float(value)/10)
    
def volume_up():
    volume = pygm.music.get_volume()
    if volume < 1:
        volume += .1
        volume = volume if volume<=1 else 1
    pygm.music.set_volume(volume)
    volume_bar.config(value=volume*10)

def volume_down():
    volume = pygm.music.get_volume()
    if volume > 0:
        volume -= .1
        volume = volume if volume>=0 else 0
    pygm.music.set_volume(volume)
    volume_bar.config(value=volume*10)

def add_folder():

    global cur_song ,song_index

    pause()

    folder_selected = filedialog.askdirectory(title="Select a Folder")
    if folder_selected:
        pygm.music.stop()
        playlist.clear()
        matching_files = [
            os.path.join(folder_selected, file)
            for file in os.listdir(folder_selected)
            if file.endswith(".mp3")
        ]

        for file in matching_files:
            playlist.append(Song(file))
        song_index = random.randrange(len(playlist)) if isshuffle else 0
        cur_song = playlist[song_index]
        played_songs.append(song_index)
        load_song()
        update_timer(timer)
        update_song()
    
def previous_song():
    global cur_song, song_index, timer, songs_counter

    if len(playlist)>1 and songs_counter != 0:
        pygm.music.stop()
        songs_counter -= 1
        song_index = played_songs[songs_counter]
        cur_song = playlist[song_index]
        load_song()
        update_song()
        update_timer(timer)
        if isplaying:
            play()
       

def next_song():
    global cur_song, song_index, timer, songs_counter
    if len(playlist)>1:
        pygm.music.stop()
        if songs_counter < len(playlist) - 1:
            songs_counter += 1
            if songs_counter<=len(played_songs)-1:
                    song_index = played_songs[songs_counter]
            else:
                if isshuffle:
                    song_index = random.choice([
                        i
                        for i in range(len(playlist))
                        if i not in played_songs
                    ])
                    played_songs.append(song_index)
                elif song_index<len(playlist)-1:
                    song_index += 1
                    played_songs.append(song_index)
                else:
                    new_playlist()
        else:
            new_playlist()
        cur_song = playlist[song_index]
        load_song()
        update_song()
        update_timer(timer)
    if isplaying:
        play()
        
def new_playlist():
    global songs_counter,song_index
    played_songs.clear()
    songs_counter = 0
    song_index = random.choice([
            i
            for i in range(len(playlist))
            if i not in played_songs
        ]) if isshuffle else 0
    played_songs.append(song_index)

def update_song():
    global cur_song_cover
    max_title_length = 18
    max_artist_length = 13
    song_title_tooltip.text = cur_song.title
    song_artist_tooltip.text = cur_song.artist
    title = (cur_song.title + ' ' * (max_title_length - len(cur_song.title)))\
        if max_title_length >= len(cur_song.title) else\
        cur_song.title[:max_title_length-3]+'...'
    artist = (cur_song.artist + ' ' * (max_artist_length - len(cur_song.artist)))\
        if max_artist_length >= len(cur_song.artist) else\
        cur_song.artist[:max_artist_length-3]+'...'
    song_title.config(text=title)
    song_artist.config(text=artist)
    song_duration.config(text = f"{int(cur_song.duration//60):02}:{round(cur_song.duration % 60):02}")
    cur_song_cover = get_cover_tk(cur_song.cover_data)
    song_cover.config(image=cur_song_cover)
    prograss_bar.config(to=round(cur_song.duration))
    get_lrc()

def get_lrc():
    global song_lrc, lrc_time, lrc_index
    lrc_index = -1
    song_lrc = []
    lrc_time = []
    if cur_song and os.path.isfile(cur_song.lrc):
        with open(cur_song.lrc) as file:
            lines = file.readlines()
        for line in lines:
            match = re.match(r"\[(\d{2}):(\d{2}.\d{2})\]\s(.*)", line)
            if match:
                min = match.group(1)
                sec = match.group(2)
                lyrics = match.group(3)
                time = (int(min) * 60 + float(sec)) * 10
                song_lrc.append(lyrics)
                lrc_time.append(time)
    for i in range(num_lines):
        lrc_displays[i].config(text='')
    if song_lrc:
        update_lrc_display()

def get_cur_lrc():
    global lrc_index
    for i in range(len(lrc_time)):
        if timer < lrc_time[i]:
            lrc_index = max(-1,i-1)
            return
    lrc_index = len(lrc_time) - 1


def update_lrc():
    global lrc_index
    if lrc_index+1<len(lrc_time):
        if timer >= lrc_time[lrc_index+1]:
            lrc_index += 1
            update_lrc_display()

def update_lrc_display():
    for i in range(num_lines):
        lrc_displays[i].config(text=(song_lrc[lrc_index-2+i])if lrc_index-2+i>=0 and lrc_index-2+i<len(song_lrc) else '')

def on_media_press(key):
    try:
        if key == keyboard.Key.media_play_pause:
            toggle_play()
        elif key == keyboard.Key.media_previous:
            previous_song()
        elif key == keyboard.Key.media_next:
            next_song()
    except AttributeError:
        pass


#root
root = tk.Tk()
root.title('Thousand Suns')
root.state("zoomed")
root.resizable(False, False)
root.bind('<space>',lambda event:toggle_play())
root.bind('<Left>',lambda event:previous_song())
root.bind('<Right>',lambda event:next_song())
root.bind('<Up>',lambda event:volume_up())
root.bind('<Down>',lambda event:volume_down())
root.bind('s',lambda event:toggle_shuffle())

#Top Bar
top_bar = tk.Frame(root,bg='black',height=100)
top_bar.pack_propagate(False)
top_bar.pack(side='top',fill='x')

#The Body
body = tk.Frame(root,bg = 'blue')
body.pack(side='top',fill='both',expand=True)

#lrc Display
tk.Frame(body,bg='blue').pack(side="top", expand=True)

for i in range(num_lines):
    lrc_display = tk.Label(body,text=f'{i}',font=("Arial", 24 if i == 2 else  16, "bold"),bg = 'blue', fg = 'white' if i == 2 else  'gray')
    lrc_display.pack(side="top", expand=True)
    lrc_displays.append(lrc_display)
    
    if i < num_lines - 1:
        tk.Frame(body,bg='blue').pack(side="top", expand=True)

tk.Frame(body,bg='blue').pack(side="top", expand=True)

#Select Folder Button
folder_icon = tk.PhotoImage(file=ASSETS_DIR +"\\assets\\folder_icon.png").subsample(2,2)
select_folder_button = tk.Button(top_bar,image = folder_icon,text='Folder',command= add_folder)
select_folder_button.pack(side='left')

#Bottom Bar
bottom_bar = tk.Frame(root, bg = 'black')
bottom_bar.pack(side='bottom',fill='x')

#Cover Image
cur_song_cover = get_cover_tk(cur_song.cover_data) if cur_song else get_cover_tk(ASSETS_DIR +"\\assets\\cover.png")
song_cover = tk.Label(bottom_bar, image=cur_song_cover)
song_cover.pack(side="left")

#Song Title And Artist
song_details = tk.Frame(bottom_bar, bg = 'black')
song_details.pack(side='left',padx=5,pady=20)
song_title = tk.Label(song_details,text=cur_song.title if cur_song else "None",font=("Arial", 12, "bold"), bg = 'black', fg = 'white',width=15,anchor='w')
song_title.pack(side='top')
song_title_tooltip = Tooltip(song_title,'Song Title!')

song_artist = tk.Label(song_details,text=cur_song.artist if cur_song else "None",font=("Arial", 8), bg = 'black', fg = 'gray',anchor='w')
song_artist.pack(side='left')
song_artist_tooltip = Tooltip(song_artist,'Song Artist!')

#Control Frame
control_frame = tk.Frame(bottom_bar,bg='black')
control_frame.pack(side='left',fill='x',expand=True)

#Control Panal
control_panal = tk.Frame(control_frame,bg='black')
control_panal.pack(side='top',pady=10)

#Prograss Panal
prograss_panal = tk.Frame(control_frame,bg = 'black')
prograss_panal.pack(side='top',fill='x',expand=True,padx=20)

#Previous Song Button
prv_song_button = tk.Button(control_panal,text = '|<',command = previous_song)
prv_song_button.pack(side='left',padx=10)

#Start/Pause Button
start_pause_button = tk.Button(control_panal,text = '>',command= play)
start_pause_button.pack(side='left',padx=20)

#Next Song Button
nxt_song_button = tk.Button(control_panal,text = '>|' , command = next_song )
nxt_song_button.pack(side='left',padx=10)

#Toggle Shuffle Button
toggle_shuffle_button = tk.Button(control_panal,text = 'S' , command= toggle_shuffle)
toggle_shuffle_button.pack(side='left',padx=20)

#Timer
cur_time = tk.Label(prograss_panal,text='00:00',font=('Arial',7),fg='lightgray',bg='black')
cur_time.pack(side='left',padx=5)

cur_song_duration = cur_song.duration if cur_song else 0

#Progress Bar
prograss_bar = ttk.Scale(prograss_panal,to=round(cur_song_duration),command=on_pos_change)
prograss_bar.pack(side='left',expand=True,fill='x')
prograss_bar.bind("<ButtonRelease-1>", on_slider_release)
prograss_bar.bind("<ButtonPress-1>", on_slider_press)

#Song Duration
song_duration = tk.Label(prograss_panal,text=f"{int((cur_song_duration // 60)):02}:{round(cur_song_duration % 60):02}",font=('Arial',7),fg='lightgray',bg='black')
song_duration.pack(side='left',padx=5)

#Volume Bar
volume_bar = ttk.Scale(bottom_bar,from_=10,to = 0,orient = 'vertical',command = on_volume_change,value=8,length=80)
volume_bar.pack(side='right',padx=20)


pygm.init()
listener = keyboard.Listener(on_press=on_media_press)
listener.start()
root.mainloop()
