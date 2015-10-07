import sys,pymongo,json
from pymongo import MongoClient
from bson import BSON,json_util
from bson.json_util import dumps
import schedule,time,subprocess,signal,os

def probe_active_streams():
    client = MongoClient()
    db = client.streaming_users_database   
    streaming_users = db.streaming_users
    streaming_count = streaming_users.find({"streaming_user_allocated": 'Y'}).count()
    print 'streaming count:' , streaming_count
    if streaming_count == 0:
        return
    streaming_record = streaming_users.find({"streaming_user_allocated": 'Y'},{"streaming_user_stream": 1, "_id":0 })
    print streaming_record
    json_read = [json.dumps(doc, default=json_util.default) for doc in streaming_record]
    
    json_list = []
    stream_list = []
    stream_str = ''
    for doc in json_read:        
        dict_1 = json.loads(doc)        
        json_list.append(dict_1["streaming_user_stream"])
    
    stream_str = json.dumps(json_list)    
    stream_str1 = str(stream_str).translate(None, '[],"')
    stream_list = stream_str1.split()
    
    for stream in stream_list:
        activestreams = ' '        
        source_filename = "http://your host:your port/" +  stream
        p = subprocess.Popen(["ffprobe", "-show_entries", "format=filename", source_filename], stdout=subprocess.PIPE)
        time.sleep(20)
        if p.poll() is None:
            p.kill()            
        else:
            activestreams = p.communicate()
            rc = p.returncode                     
        if activestreams == ' ' or rc != 0 :            
            streaming_user_result = streaming_users.update_one({"streaming_user_stream": stream},
                                {'$set':{"streaming_user_allocated": "N"}},upsert=False)
           
schedule.every(2).minutes.do(probe_active_streams)

while True:
    schedule.run_pending()
    time.sleep(1)
