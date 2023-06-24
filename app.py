from flask import Flask, render_template, Response, request, redirect
from flask_mail import * 
import cv2
import datetime
import os, sys
import numpy as np
from threading import Thread
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from decouple import config


import os.path

EMAIL     = config("EMAIL")
PASSWORD = config("PASSWORD")


BASE_DIR        = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER   = os.path.join(BASE_DIR, "static", "shots")

global capture 
capture=0

try:
    os.mkdir('./static/shots')
except OSError as error:
    pass

app = Flask(__name__, template_folder='./templates')

camera = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('info.html')

def gen_frames():  # generate frame by frame from camera
    import time
    global out, capture,rec_frame
    while True:
        timeCheck = time.time()
        future = 10*60 # delay

        if time.time() >= timeCheck:
            success, frame = camera.read()

            timeCheck = time.time()+future 
        
            if success:
                
                if(capture):
                    capture=0
                    now = datetime.datetime.now()
                    p = os.path.sep.join(['static/shots', "me.jpg"])
                    cv2.imwrite(p, frame)
                
                    
                try:
                    ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                except Exception as e:
                    pass
                    
            else:
                pass
        else:
        # Read from buffer, but skip it
            ret = camera.grab()

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/requests',methods=['GET','POST'])
def tasks():
    import time
    global switch,camera
    if request.method == 'POST':
        name = request.values.get('name')
        t_email = request.values.get('t_email') 

        print('name',name,type(name))
        print('t_email',t_email,type(t_email))
        if request.form.get('click') == 'Capture':
                global capture
                capture=1
                # camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                print('name',name,type(name))
                print('email',t_email,type(t_email))

    

    elif request.method=='GET':
        name = request.values.get('name')
        t_email = request.values.get('t_email')
        print(name,t_email)
        return render_template('capture.html',name=name,t_email=t_email)
    time.sleep(10)
    send_email(name,t_email)
    # delete_uploaded_file(UPLOAD_FOLDER+"/me.jpg")
    return render_template('success.html')

def send_email(name,t_email):
    
    email = EMAIL
    password = PASSWORD

    send_to_email = t_email
    subject = 'You can find your face here'
    message = 'your photo is here. Mr/Ms.'+name
    file_location = 'shots/me.jpg'

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = send_to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))


    img_data = open(UPLOAD_FOLDER+"/me.jpg", 'rb').read()
    msg.attach(MIMEImage(img_data, 
                        name=os.path.basename("shots/me.jpg")))
    
    
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    text = msg.as_string()
    # print('info',email,send_to_email,text)
    server.sendmail(email, send_to_email, text)
    server.quit()
    return True

def delete_uploaded_file(filepath):

    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    
    return False

if __name__ == '__main__':
    app.run()
    
 

