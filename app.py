
  
import imp
import sys
from flask import Flask, render_template, url_for, request
from math import *
# import file
import os,signal
import subprocess
import pymongo



myclient = pymongo.MongoClient("mongodb+srv://Anurag:Anurag@cluster0.toske.mongodb.net/dtt?retryWrites=true&w=majority")
mydb = myclient["dtt"]
# print(mydb)
mycol = mydb["users"]
name=""
name1=""



cmd = "nohup python3 -u ./file.py &"
pid="ps ax | grep file.py"
run=0

app=Flask(__name__)

def process():
     
    # Ask user for the name of process
    name = "file.py"
    try:
         
        # iterating through each instance of the process
        for line in os.popen("ps ax | grep " + name + " | grep -v grep"):
            fields = line.split()
             
            # extracting Process ID from the output
            pid = fields[0]
             
            # terminating process
            os.kill(int(pid), signal.SIGKILL)
        print("Process Successfully terminated")
         
    except:
        print("Error Encountered while running script")

@app.route('/')

@app.route('/home')
def home():
    return render_template("index.html")

@app.route('/result',methods=['POST', 'GET'])
def result():
    output = request.form.to_dict()
    print(output)
    name = output["name"]
    name1=output["name1"]
    print(name,name1)

   

    
    

    if name!="dtt" and name1=="dtt":

        

        y = mycol.find_one({"name":"dtt"})
        run=int(y["run"])
        print(run,"FIRST")


        if run==0:

           
            myquery = { "name": "dtt" }
            newvalues = { "$set": { "run": "1" } }
            mycol.update_one(myquery, newvalues)
            
            print("LoggedIn",run)

            returned_value = subprocess.call(cmd, shell=True)

            print("This process has the PID", os.getpid())
            return render_template('running.html')

        else :
            return render_template('running.html')



        
    
    else : 
        return render_template('wrongdetails.html')

    return name




@app.route('/stop',methods=['POST', 'GET'])
def stop():

    process()
    myquery = { "name": "dtt" }
    newvalues = { "$set": { "run": "0" } }
    mycol.update_one(myquery, newvalues)


    print(myquery,newvalues, "STOP")
    return render_template("index.html")
        



    


    
if __name__== "__main__":
    app.run(debug=True)

