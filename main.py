import tkinter as tk
from tkinter import ttk, filedialog
from song import Song
from tooltip import Tooltip
import os
import pygame.mixer as pygm
from PIL import Image, ImageTk
import io
import re


isplaying = False
timer = 0
playlist = []
song_index = 0
cur_song  = None
song_lrc = []
lrc_index = -1
lrc_time = []
cur_song_cover = None 
after_id = None

def get_cover_tk(imageData):
        if not imageData:
            imageData = "assets/cover.png"

        if isinstance(imageData, bytes):  
            imageData = io.BytesIO(imageData) 
        image = Image.open(imageData)
        image = image.resize((100, 100))
        image = ImageTk.PhotoImage(image)
        return image

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
    print(cur_song.title + ' Loaded!')
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

def add_folder():

    global cur_song ,song_index

    pause()

    folder_selected = filedialog.askdirectory(title="Select a Folder")
    if folder_selected:
        pygm.music.stop()
        playlist.clear()
        song_index = 0
        matching_files = [
            os.path.join(folder_selected, file)
            for file in os.listdir(folder_selected)
            if file.endswith(".mp3")
        ]

        for file in matching_files:
            playlist.append(Song(file))

        cur_song = playlist[0]
        load_song()
        update_timer(timer)
        update_song()
    
def previse_song():
    global cur_song, song_index, timer

    if len(playlist)>1:
        pygm.music.stop()
        song_index = song_index - 1 if song_index > 0 else len(playlist)-1
        cur_song = playlist[song_index]
        load_song()
        update_song()
        update_timer(timer)
        if isplaying:
            play()
       

def next_song():
    global cur_song, song_index, timer

    if len(playlist)>1:
        pygm.music.stop()
        song_index = song_index + 1 if song_index < len(playlist) - 1 else 0
        cur_song = playlist[song_index]
        load_song()
        update_song()
        update_timer(timer)
        if isplaying:
            play()

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
    if song_lrc:
        update_lrc_display()

def get_cur_lrc():
    global lrc_index
    for i in range(len(lrc_time)):
        if timer < lrc_time[i]:
            lrc_index = max(-1,i-1)
            break


def update_lrc():
    global lrc_index
    if lrc_index+1<len(lrc_time):
        if timer >= lrc_time[lrc_index+1]:
            lrc_index += 1
            update_lrc_display()

def update_lrc_display():
    lrc_display_1.config(text=(song_lrc[lrc_index-2])if lrc_index-2>=0 else '')
    lrc_display_2.config(text=(song_lrc[lrc_index-1])if lrc_index-1>=0 else '')
    lrc_display_3.config(text=(song_lrc[lrc_index])  if lrc_index>=0 else '')
    lrc_display_4.config(text=(song_lrc[lrc_index+1])if lrc_index+1<len(song_lrc) else '')
    lrc_display_5.config(text=(song_lrc[lrc_index+2])if lrc_index+2<len(song_lrc) else '')
    lrc_display_6.config(text=(song_lrc[lrc_index+3])if lrc_index+3<len(song_lrc) else '')


#root
root = tk.Tk()
root.title('Thousand Suns')
root.geometry("1200x900")

#Top Bar
top_bar = tk.Frame(root,bg='black',height=100)
top_bar.pack_propagate(False)
top_bar.pack(side='top',fill='x')

#The Body
body = tk.Frame(root,bg = 'blue')
body.pack(side='top',fill='both',expand=True)

#Lrc Display
lrc_display_1 = tk.Label(body,text='lrc Display',font=("Arial", 16, "bold"),bg = 'blue', fg = 'gray')
lrc_display_1.pack(side='top',pady=20)

lrc_display_2 = tk.Label(body,text='lrc Display',font=("Arial", 16, "bold"),bg = 'blue', fg = 'gray')
lrc_display_2.pack(side='top',pady=20)

lrc_display_3 = tk.Label(body,text='lrc Display',font=("Arial", 18, "bold"),bg = 'blue', fg = 'white')
lrc_display_3.pack(side='top',pady=20)

lrc_display_4 = tk.Label(body,text='lrc Display',font=("Arial", 16, "bold"),bg = 'blue', fg = 'gray')
lrc_display_4.pack(side='top',pady=20)

lrc_display_5 = tk.Label(body,text='lrc Display',font=("Arial", 16, "bold"),bg = 'blue', fg = 'gray')
lrc_display_5.pack(side='top',pady=20)

lrc_display_6 = tk.Label(body,text='lrc Display',font=("Arial", 16, "bold"),bg = 'blue', fg = 'gray')
lrc_display_6.pack(side='top',pady=20)

#Select Folder Button
folder_icon = tk.PhotoImage(file="assets/folder_icon.png").subsample(2,2)
select_folder_button = tk.Button(top_bar,image = folder_icon,text='Folder',command= add_folder)
select_folder_button.pack(side='left')

#Bottom Bar
bottom_bar = tk.Frame(root, bg = 'black')
bottom_bar.pack(side='bottom',fill='x')

#Cover Image
cur_song_cover = get_cover_tk(cur_song.cover_data) if cur_song else get_cover_tk("assets/cover.png")
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
prv_song_button = tk.Button(control_panal,text = '|<',command = previse_song)
prv_song_button.pack(side='left',padx=10)

#Start/Pause Button
start_pause_button = tk.Button(control_panal,text = '>',command= play)
start_pause_button.pack(side='left',padx=20)

#Next Song Button
nxt_song_button = tk.Button(control_panal,text = '>|' , command = next_song )
nxt_song_button.pack(side='left',padx=10)

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
root.mainloop()
