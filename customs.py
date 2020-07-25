from flask_socketio import SocketIO
from flask import Flask, redirect, render_template, request, url_for
import sqlite3
from flask.helpers import send_file
from db import get_user, join_user, save_user, update_user
from _io import BytesIO
from flask_wtf.file import FileField
from wtforms import SubmitField
from flask_wtf import Form

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
conn= sqlite3.connect("YTD.db")
cursor = conn.cursor()

app = Flask(__name__)
app.secret_key = "my secret key"
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('id_customs.html')
@app.route('/join', methods=['POST'])
def join_trade():
    if request.method == 'POST':
        tradeid = request.form.get('tradeid')
        pas = request.form.get('pas')
        user = join_user(tradeid,pas)
        if user == True:
            return download(tradeid)
        else:
            message = 'Failed Login'
    return render_template('id_customs.html',msg1 = message)

@app.route('/make',methods=['POST',"GET"])
def make():
    if request.method == 'POST':
        tradeid = request.form.get('tradeid')
        option = request.form['options']
        l = len(blockchain.chain)
        if(option == 'Approve'):
            msg = 'Port Authorithies has Approved the Documents of Trade Id '+ tradeid
            msg1 = 'True'
        elif(option == 'DisApprove'):
            msg = 'Customs has Disapproved the Documents of Trade Id '+ tradeid
            msg1 = 'False'
        blockchain.addBlock(Block(l+1,time.time(),msg),msg)
        for i in blockchain.chain:
            print(i)
    return redirect(url_for('index'))


def download(tradeid):

    form = UploadForm()

    if request.method == "POST":

        conn= sqlite3.connect("YTD.db")
        cursor = conn.cursor()
        print("IN DATABASE FUNCTION ")
        c = cursor.execute(""" SELECT * FROM  my_table """)

        for x in c.fetchall():
            name_v=x[0]
            data_v=x[1]
            break

        conn.commit()
        cursor.close()
        conn.close()

        return send_file(BytesIO(data_v), attachment_filename= tradeid +'.pdf', as_attachment=True)


    return render_template("custome.html", form=form,id=tradeid)

class UploadForm(Form):
    file = FileField()
    download = SubmitField("download")

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    socketio.run(app,port=5002,debug=True)