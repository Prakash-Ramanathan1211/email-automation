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

import os.path

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER   = os.path.join(BASE_DIR, "static", "shots")
global capture,rec_frame, grey, switch, neg, face, rec, out 
capture=0
grey=0
neg=0
face=0
switch=1
rec=0

#make shots directory to save pics
try:
    os.mkdir('./static/shots')
except OSError as error:
    pass

#Load pretrained face detection model    


#instatiate flask app  
app = Flask(__name__, template_folder='./templates')

# app.config["MAIL_SERVER"]='smtp.gmail.com'  
# app.config["MAIL_PORT"] = 465  
# app.config["MAIL_USERNAME"] = 'roughitsrinivasan17@gmail.com'  
# app.config['MAIL_PASSWORD'] = 'hnftqszsmeaeylen'  
# app.config['MAIL_USE_TLS'] = False  
# app.config['MAIL_USE_SSL'] = True 

# mail = Mail(app)  


camera = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('index.html')

def gen_frames():  # generate frame by frame from camera
    global out, capture,rec_frame
    while True:
        success, frame = camera.read() 
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


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera
    if request.method == 'POST':
        name = request.form.get('name')
        t_email = request.form.get('t_email')
        

        if request.form.get('click') == 'Capture':
            global capture
            capture=1
            print('name',name,type(name))
            print('email',t_email,type(t_email))

            wha(name,t_email)

            # return True
            # msg = Message(subject = "hello", body = "hello", sender = name , recipients = [t_email])  
            # with app.open_resource("shots/me.jpg") as fp:  
            #     msg.attach("me.jpg","image/jpg",fp.read())  
            #     mail.send(msg)  
            
        
                          
                 
    elif request.method=='GET':
        return render_template('capture.html')
    return render_template('success.html')






@app.route('/info',methods=['GET'])
def inf():
    


    return render_template('info.html')
    



 



# @app.route('/what',methods=['POST'])
def wha(name,t_email):
    # name = request.form.get('name')
    # t_email = request.form.get('t_email')
    email = 'yuvibro1211@gmail.com'
    password = 'tiecqtzjasbhectc'
    # send_to_email = "roughitsrinivasan@gmail.com"
    send_to_email = t_email
    subject = ' Sending Email with an attachment'
    message = 'Please find the attachment to email, thanks '
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
    print('info',email,send_to_email,text)
    server.sendmail(email, send_to_email, text)
    server.quit()
    return render_template('success.html')





if __name__ == '__main__':
    app.run()
    
 




