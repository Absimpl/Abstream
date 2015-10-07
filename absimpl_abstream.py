import sys,pymongo,json,flask_cors,urllib2,re,ast,os
from pymongo import MongoClient
from flask import Flask, request, jsonify, url_for,render_template,redirect
from flask.ext.login import login_user, logout_user, login_required,LoginManager
from flask.ext.cors import CORS
from bson import BSON,json_util
from bson.json_util import dumps
import threading,time,subprocess
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
cors = CORS(app)
lm = LoginManager()
lm.init_app(app)
app.secret_key = os.urandom(24)
_name = ''

@app.route('/request_feed', methods=['POST','GET', 'OPTIONS'])
@flask_cors.cross_origin()
def request_feed():       
    organizer_id = str(request.values['organizer_id'])
    event_name = str(request.values['event_name'])     
    client = MongoClient()
    db = client.streaming_users_database   
    streaming_users = db.streaming_users
    streaming_record = streaming_users.find_one({"streaming_user_allocated": 'N'})    
    json_rec = json.dumps(streaming_record, sort_keys=True, indent=4, default=json_util.default)   
    dict_rec = json.loads(str(json_rec))    
    streaming_user_result = streaming_users.update_one({"streaming_user_feed": dict_rec["streaming_user_feed"]},
                                                    {'$set':{"streaming_user_allocated": "Y", "streaming_user_organizer_id": organizer_id, "streaming_user_event": event_name}},upsert=False)
    streaming_user_result = streaming_users.find_one({"streaming_user_feed": dict_rec["streaming_user_feed"]})    
    return json.dumps(streaming_user_result, sort_keys=True, indent=4, default=json_util.default)

@app.route('/stop_stream', methods=['POST','GET', 'OPTIONS'])
@flask_cors.cross_origin()
def stop_stream():
    
    organizer_id = str(request.values['organizer_id'])
    event_name = str(request.values['event_name'])
    stop_feed = str(request.values['stop_feed'])
    
    client = MongoClient()
    db = client.streaming_users_database   
    streaming_users = db.streaming_users
    streaming_record = streaming_users.update_one({"streaming_user_feed": stop_feed},
                                                {'$set':{"streaming_user_allocated": "N"}},upsert=False)
    return 'STOPPED OK'

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        global _name
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        print _name, _email, _password        

        # validate the received values
        if _name and _email and _password:
            
                                    
            # All Good, let's call MongoDb
            _hashed_password = generate_password_hash(_password)
            client = MongoClient()
            db = client.streaming_registered_users_database
            streaming_registered_users = db.streaming_registered_users
            streaming_registered_record = streaming_registered_users.update_one({"username": _name},
                                                    {'$set':{"password": _hashed_password, "email": _email}},upsert=True)           
            user_obj = User(_name)
            login_user(user_obj)            
            return 'ok'
        else:            
            return 'nok'

    except Exception as e:        
        return json.dumps({'error':str(e)})
    

@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')

@app.route('/signIn',methods=['POST','GET'])
def signIn():
    
    try:
        global _name
        _name = request.form['inputName']
        _password = request.form['inputPassword']               

        # validate the received values
        if _name  and _password:            
            
            # All Good, let's call MongoDb
            client = MongoClient()
            db = client.streaming_registered_users_database
            streaming_registered_users = db.streaming_registered_users
            streaming_registered_record = streaming_registered_users.find_one({"username": _name})            
            print streaming_registered_record
            global dict2
            dict2 = str(json.dumps(streaming_registered_record["password"]))            
            dict2 = re.sub('["]', '' , dict2)          
            
            if check_password_hash(dict2, _password):
                user_obj = User(_name)
                login_user(user_obj)                
                return 'ok'
            else:
                print 'nok'
                return 'nok'           
        else:            
            return 'nok'
        
    except Exception as e:        
        return json.dumps({'error':str(e)})

@app.route('/check_password',methods=['POST','GET'])
def check_password():
    
    try:        
        d_name = request.values['d_name']
        d_password = request.values['d_password']               

        # validate the received values
        if d_name  and d_password:
            
            # All Good, let's call MongoDb
            client = MongoClient()
            db = client.streaming_registered_users_database
            streaming_registered_users = db.streaming_registered_users
            streaming_registered_record = streaming_registered_users.find_one({"username": d_name})            
            global dict2
            dict2 = str(json.dumps(streaming_registered_record["password"]))            
            dict2 = re.sub('["]', '' , dict2)            
            
            if check_password_hash(dict2, d_password):               
                return 'CHECKED'
            else:                
                return 'nok'           
        else:            
            return 'nok'
        
    except Exception as e:        
        return json.dumps({'error':str(e)})
    
@app.route('/list_streams', methods=['POST','GET'])
@flask_cors.cross_origin()
@login_required
def list_streams():
    
    client = MongoClient()
    db = client.streaming_users_database   
    streaming_users = db.streaming_users
    streaming_record = streaming_users.find({"streaming_user_allocated": 'Y'},{"streaming_user_stream": 1, "streaming_user_event": 1, "_id": 0})
    
    json_docs = [json.dumps(doc, default=json_util.default) for doc in streaming_record]
    dict1 = {}    
    doc1 =[]
    for dict in json_docs:        
        
        dict2 = ast.literal_eval(dict)
        doc1.append(str(dict2["streaming_user_event"]) + 'add#on' + str(dict2["streaming_user_stream"]))
        
    dict1 = json.dumps(dict1, default=json_util.default)
    doc1 = json.dumps(doc1,default=json_util.default)
    
    json_str = str(doc1).translate(None, "[]'")
    json_str = str(json_str).translate(None, '"')    
    try:
        return render_template("viewstream7.html", streamdata = json_str, user = _name)
    except Exception as e:        
        print json.dumps({'error':str(e)})    

class User():

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)
    
@app.route('/logout')
@login_required
def logout():  
    logout_user()
    return render_template('index.html')

@lm.user_loader
def load_user(_name):
    client = MongoClient()
    db = client.streaming_registered_users_database
    streaming_registered_users = db.streaming_registered_users
    u = streaming_registered_users.find_one({"username": _name})
    if not u:
        return None
    return User(u['username'])
        
if __name__ == "__main__":

   client = MongoClient()
   db = client.streaming_users_database   
   streaming_users = db.streaming_users
   streaming_record = streaming_users.update_many({"streaming_user_allocated": "Y"},{'$set':{"streaming_user_allocated": "N"}}, upsert=False)   
   
   app.run(host='your host',debug=True)
