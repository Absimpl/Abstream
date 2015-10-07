# -*- coding: utf-8 -*-
import subprocess, os, time, signal,re,json
import kivy
from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '400')
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import Tkinter,httplib, urllib,json,werkzeug
from werkzeug import exceptions, security,generate_password_hash, check_password_hash
from subprocess import check_output, STDOUT, CalledProcessError

username = ''
eventname = ''
feed_string = ''
user_logged_in = 'N'
dev_select = ''
audio_select = ''
audiolist = []
videolist = []
dictionary = {}

def user_login():
    passwords = [('organizer1', 'password')]    
    def make_entry(parent, caption, width=None, **options):
        Tkinter.Label(parent, text=caption).pack(side=Tkinter.TOP)
        entry = Tkinter.Entry(parent, **options)
        if width:
            entry.config(width=width)
            entry.pack(side=Tkinter.TOP, padx=10, fill=Tkinter.BOTH)
            return entry
    def enter(event):
        check_password()
    
    def check_password():        
        if (user.get() and  password.get()):            
            # All Good
            params = urllib.urlencode({'d_name': user.get(), 'd_password':   password.get()})
            headers = {"Content-type": "application/x-www-form-urlencoded",
                       "Accept": "text/plain"}
            conn = httplib.HTTPConnection("your host", your port)    
            conn.request("POST", "check_password", params, headers)
            response = conn.getresponse()            
            data = str(response.read())            
            if data == 'CHECKED':
                global username
                global eventname
                username = user.get()            
                eventname = event_name.get()                
                if eventname.isspace() or eventname == '':                    
                    eventname = username + ' event'                
                root.destroy()                
                global user_logged_in
                user_logged_in = 'Y'
                return
        
    root = Tkinter.Tk()
    root.geometry('300x160')
    root.title('Enter your information')
    #frame for window margin
    parent = Tkinter.Frame(root, padx=10, pady=10)
    parent.pack(fill=Tkinter.BOTH, expand=True)
    #entrys with not shown text    
    user = make_entry(parent, "User name:", 16)
    password = make_entry(parent, "Password:", 16, show="*")    
    event_name = make_entry(parent, "Event Name:", 16)
    #button to attempt to login
    b = Tkinter.Button(parent, borderwidth=4, text="Login", width=10, pady=8, command=check_password)
    b.pack(side=Tkinter.BOTTOM)
    password.bind('<Return>', enter)
    user.focus_set()
    parent.mainloop()
    
def device_select_and_stream():        
    stream1 = os.popen('ffmpeg -list_devices true -f dshow -i dummy 2> devices.txt')
    stream1.close()
    device_list() 
    if len(videolist) > 1 and user_logged_in == 'Y':    
        device_menu()
    if user_logged_in == 'Y':
        connect_feed()
    else:        
        user_login()
        device_select_and_stream()

def device_list():
    file1 = open("devices.txt", "r")
    read1 = file1.read()
    pos = read1.find("DirectShow video devices (some may be both video and audio devices)")
    pos1 = pos + 67
    read2 = read1[pos1:]
    pos2 = read2.find("DirectShow audio devices")
    pos3 = pos2 + 24
    read3 = read2[pos3:]
    pos4 = read3.find("dummy")
    read3 = read3[:pos4]
    read2 = read2[:pos2]
    global audiolist
    global videolist
    global dictionary
    audiolist = read3.splitlines()
    videolist = read2.splitlines()      
    
    for item in videolist:    
        if item.find("dshow") >= 0 and item.find("Alternative") >= 0:
            videolist.remove(item)

    for item in audiolist:        
        if item.find("dshow") >= 0 and item.find("Alternative") >= 0:
            audiolist.remove(item)
                
    for idx, item in enumerate(audiolist):        
        pos = item.find("[dshow")
        pos = pos + 28
        item = item[pos:]
        item = item.translate(None, '"')        
        audiolist[idx] = item

    for idx, item in enumerate(videolist):        
        pos = item.find("[dshow")
        pos = pos + 28
        item = item[pos:]
        item = item.translate(None, '"')       
        videolist[idx] = item
    
    for item in audiolist:
        if item == '':
            audiolist.remove(item)

    for item in videolist:
        if item == '':
            videolist.remove(item)   
    
    if len(videolist) > len(audiolist):
        diff = len(videolist) - len(audiolist)
        default_audio = audiolist[0]
        for i in range(0,diff):
            audiolist.append(default_audio)       
                                    
    dictionary = dict(zip(videolist, audiolist))    
    file1.close
                      
def device_menu():
    root = Tkinter.Tk()
    frame = Tkinter.Frame(root, width=300)
    frame.pack_propagate(0) # set the flag to use the size
    frame.pack() # remember to pack it or else it will not be pack   
# to store the selection
    var = Tkinter.StringVar()

# drop down menu
    options = Tkinter.OptionMenu(root, var, *videolist)
    options.pack(expand="yes", fill="x")

# select the first option
    var.set(videolist[0])    
    def handle_selection():            
        global dev_select
        global audio_select
        for key, value in dictionary.iteritems():
            if str(key) == var.get():
                dev_select = 'video=' + str(key)
                audio_select = 'audio=' + str(value)                
        root.destroy()
    # button to get selection
    b = Tkinter.Button(root, text="Select Streaming device", command=handle_selection, width=10)
    b.pack(expand="yes", fill="x")

    root.mainloop()      

def connect_feed():    
    params = urllib.urlencode({'organizer_id': username, 'event_name':   eventname})
    headers = {"Content-type": "application/x-www-form-urlencoded",
                  "Accept": "text/plain"}
    conn = httplib.HTTPConnection("your host", your port)    
    conn.request("POST", "request_feed", params, headers)
    response = conn.getresponse()    
    data = str(response.read())
    dict1 = json.loads(data)
    dict2 = json.dumps(dict1["streaming_user_feed"])
    global feed_string
    feed_string1 = str(dict2)    
    feed_string = re.sub('["]', '' , feed_string1)    
    output_stream = "http://your host:your port/" + feed_string    
    p = subprocess.Popen(["ffmpeg", "-f", "dshow", "-video_size", "640x480", "-framerate", "30", "-rtbufsize", "500M", "-i" , dev_select, "-f", "dshow", "-i", audio_select, output_stream], stdout=subprocess.PIPE) 
    
def callback_Start_Stream(instance):
    if user_logged_in == 'N':
        user_login()    
    device_select_and_stream()
        
def callback_Stop_Stream(instance):    
    os.popen("Taskkill /IM ffmpeg.exe /F")
    params = urllib.urlencode({'organizer_id':username, 'event_name':   eventname, 'stop_feed': feed_string})
    headers = {"Content-type": "application/x-www-form-urlencoded",
                  "Accept": "text/plain"}    
    conn = httplib.HTTPConnection("your host", your port)
    conn.request("POST", "stop_stream", params, headers)
    response = conn.getresponse()           
                   
class Abstream(App):
    def build(self):        
        layout = BoxLayout(orientation='vertical')
        btn1 = Button(text='Start Stream',pos=(100, 100))
        btn1.bind(on_press=callback_Start_Stream)                             
        btn2 = Button(text='Stop Stream',pos=(200, 200))
        btn2.bind(on_press=callback_Stop_Stream)
        layout.add_widget(btn1)
        layout.add_widget(btn2)        
        return layout

Abstream().run()

