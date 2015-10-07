# -*- coding: utf-8 -*-
import subprocess, os, time, signal,re
import kivy
from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '400')
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import Tkinter,httplib, urllib,json
import pymongo
from pymongo import MongoClient
import werkzeug
from werkzeug import exceptions, security,generate_password_hash, check_password_hash

username = ''
eventname = ''
feed_string = ''
user_logged_in = 'N'
choice_list = []
choice_dict = {}
dev_select = '/dev/video0'
audio_select = 'hw:1'

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
            # All Good, let's call MongoDb
            _name = user.get()
            
            client = MongoClient()
            db = client.streaming_registered_users_database
            streaming_registered_users = db.streaming_registered_users
            streaming_registered_record = streaming_registered_users.find_one({"username": _name})            
            global dict2
            dict2 = str(json.dumps(streaming_registered_record["password"]))
            
            dict2 = re.sub('["]', '' , dict2)
            
            if check_password_hash(dict2, password.get()):
                global username
                global eventname
                username = user.get()            
                eventname = event_name.get()
                if eventname.isspace() or eventname == '':
                    eventname = username + 'event'
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
    event_name = make_entry(parent, "Event Nmae:", 16)
    #button to attempt to login
    b = Tkinter.Button(parent, borderwidth=4, text="Login", width=10, pady=8, command=check_password)
    b.pack(side=Tkinter.BOTTOM)
    password.bind('<Return>', enter)
    user.focus_set()
    parent.mainloop()
    
def device_select_and_stream():    
      
    str_full = ""
    str_list = []
    for line in os.popen("v4l2-ctl --list-devices"):        
        if line.isspace():            
            str_list.append(str_full)            
            str_full = ''        
        str_full = str_full + str(line)
        str_full = re.sub('[\n\t]', '' , str_full)
        
    global choice_list
    global choice_dict    
    choice_list = []
    choice_dict = {}
    for item in str_list:
        fields = item.split("):")        
        choice_list.append(fields[0])
        choice_dict[fields[0]] = fields[1]     
    if len(choice_list) > 1 and user_logged_in == 'Y':
            device_menu()
    if user_logged_in == 'Y':
        connect_feed()
    else:        
        user_login()
        device_select_and_stream()   
     
def device_menu():
    root = Tkinter.Tk()
    frame = Tkinter.Frame(root, width=300)
    frame.pack_propagate(0) # set the flag to use the size
    frame.pack() # remember to pack it or else it will not be pack   
# to store the selection
    var = Tkinter.StringVar()

# drop down menu
    options = Tkinter.OptionMenu(root, var, *choice_list)
    options.pack(expand="yes", fill="x")

# select the first option
    var.set(choice_list[0])
    
    def handle_selection():        
        dev_select1 = var.get()
        global dev_select
        global audio_select
        dev_select = choice_dict[dev_select1]
        root.destroy()
    # button to get selection
    b = Tkinter.Button(root, text="Select", command=handle_selection, width=10)
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
    p = subprocess.Popen(["ffmpeg", "-f", "v4l2", "-s", "640x480", "-r", "25", "-i", dev_select, "-f", "alsa", "-ac", "2", "-i", audio_select, output_stream], stdout=subprocess.PIPE)     
    
def callback_Start_Stream(instance):    
    if user_logged_in == 'N':
        user_login()   
    device_select_and_stream()
        
def callback_Stop_Stream(instance):
    
    processname = 'ffmpeg'
    for line in os.popen("ps xa"):
        fields = line.split()
        pid = fields[0]
        process = fields[4]        
        if process.find(processname) >= 0:             
        # Kill the Process. Change signal.SIGHUP to signal.SIGKILL if you like
            os.kill(int(pid), signal.SIGKILL)
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

