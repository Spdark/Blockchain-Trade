from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, login_user, logout_user,login_required,current_user
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from db import get_user, join_user, save_user, update_user

import string
from werkzeug.utils import secure_filename

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import config
import uuid
import random


import time
import hashlib
import json
import time



class Block():
    def __init__(self,nonce,tstamp,transaction,prevhash = ''):
        self.nonce = nonce
        self.tstamp = tstamp
        self.transaction = transaction
        self.prevhash = prevhash
        self.hash = self.calcHash()

    def calcHash(self):
        block_string=json.dumps({"nonce":self.nonce,"tstamp":self.tstamp,"transaction":self.transaction,"prevhash":self.prevhash},sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def __str__(self):
        string  = "nonce: " + str(self.nonce) + "\n"
        string += "tstamp: " + str(self.tstamp)+ "\n"
        string += "transaction: " + str(self.transaction)+ "\n"
        string += "prevhas: " + str (self.prevhash)+ "\n"
        string += "hash: " + str (self.hash)+ "\n"
        return string

class Blockchain():
    def __init__(self):
        self.chain=[self.generateGensisBlock(),]
        self.t_block = ['Gensis Block',]
    def generateGensisBlock(self):
        return Block(1,'01/01/2017','Gensis Block')
    def getLastBlock(self):
        return self.chain[-1]
    def addBlock(self,newBlock,msg):
        newBlock.prevhash = self.getLastBlock().hash
        newBlock.hash = newBlock.calcHash()
        self.chain.append(newBlock)
        self.t_block.append(msg)


    def isChainValid(self):
        for i in range(1,len(self.chain)):
            prevb = self.chain[i-1]
            currb = self.chain[-1]
            if(currb.hash != currb.calcHash()):
                return False
            if(currb.prevhash != prevb.hash):
                return False
        return True

blockchain = Blockchain()

app = Flask(__name__)
app.secret_key = "my secret key"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('your_email')
        password = request.form.get('password')
        fname = request.form.get('first_name')
        lname = request.form.get('last_name')
        ptype = request.form.get('product_type')
        save_user(email,password,fname,lname,ptype)

        msg = MIMEMultipart()
        msg['To'] = email
        msg['subject'] = "Welcome To ShipBlocks"

        body = config.b_msg

        msg.attach(MIMEText(body,'html'))

        server = smtplib.SMTP("smtp.gmail.com",587)
        server.ehlo()
        server.starttls()
        server.login(config.E_address,config.Pass)
        server.sendmail(config.E_address,msg['To'],msg.as_string())
        server.close()
        return redirect(url_for('home'))
    return render_template('register.html')


@app.route('/login',methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return render_template('home.html')
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        password_input = request.form.get('password')
        user = get_user(email)
        if user and user.check_password(password_input):
            if user.status == True:
                login_user(user)
                return render_template('id.html',fname = user.fname)
            else:
                message = 'Please Wait Your Account is Under Review'
        else:
            message = 'Failed Login'
    return render_template('login.html',message = message)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@login_manager.user_loader
def load_user(email):
    return get_user(email)

@app.route('/create', methods=['POST'])
def create_trade():
    if request.method == 'POST':
        emailcreate = request.form.get('emailcreate')
        passcreate = request.form.get('passcreate')
        user = get_user(emailcreate)
        if user and user.check_password(passcreate):
            a = 0
            a = str(uuid.uuid1())
            a = a[0:8]
            first = str(random.randint(0,10))
            last = str(random.randint(0,10))
            id = "SHPBLK" + first + a + last
            update_user(emailcreate,id,randomString(8))
            message = 'True'
            return render_template('id.html',msg = message)
        else:
            message = 'False'
    return render_template('id.html',msg = message)

@app.route('/join', methods=['POST'])
def join_trade():
    if request.method == 'POST':
        tradeid = request.form.get('tradeid')
        pas = request.form.get('pas')
        user = join_user(tradeid,pas)
        if user == True:
            return render_template('home.html',id = tradeid)
        else:
            message = 'Failed Login'
    return render_template('id.html',msg1 = message)

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


@app.route('/exporter',methods = ['GET','POST'])
def Exporter():
    file = request.files['inputfile']
    tradeid = request.form.get('exporterTradeId')
    l = len(blockchain.chain)
    database(name = tradeid, data1 = file.read(),data2 = None,data3 = None,state= "Disapprove")
    msg = 'Exporter with Trade Id ' + tradeid + 'has Uploaded the  Documents'
    blockchain.addBlock(Block(l+1,time.time(),msg),msg)
    for i in blockchain.chain:
        print(i)
    return render_template('home.html',msg123 = "True")

@app.route('/importer',methods = ['GET','POST'])
def Importer():
    file1 = request.files['inputfile1']
    file2 = request.files['inputfile2']
    file3 = request.files['inputfile3']
    tradeid = request.form.get('importerTradeId')
    l = len(blockchain.chain)
    msg = 'Importer with Trade Id ' + tradeid + 'has Uploaded the  Documents'
    database(name = tradeid, data1 = file1.read(),data2 = file2.read(),data3 = file3.read(),state= 0)
    blockchain.addBlock(Block(l+1,time.time(),msg),msg)
    for i in blockchain.chain:
        print(i)
    return render_template('home.html',msg123 = "True")

def database(name, data1,data2,data3,state):
    import sqlite3
    conn= sqlite3.connect("YTD.db")
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS my_table (name TEXT,data1 BLOB,data2 BLOB,data3 BLOB,state INETGER) """)
    cursor.execute("""INSERT INTO my_table (name, data1,data2,data3,state) VALUES (?,?,?,?,?) """,(name,data1,data2,data3,state))

    conn.commit()
    cursor.close()
    conn.close()



if __name__ == '__main__':
    socketio.run(app,port=5000,debug=True)