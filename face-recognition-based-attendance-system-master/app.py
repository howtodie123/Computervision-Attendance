import cv2
import os
from flask import Flask, request, render_template
from datetime import date
from datetime import datetime
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib
import shutil 
import requests
import json

# Defining Flask App
app = Flask(__name__)

nimgs = 10

# Saving Date today in 2 different formats
datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")
datetoday0 = datetime.now().strftime("%m_%d_%y %H:%M:%S")

# Initializing VideoCapture object to access WebCam
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


# If these directories don't exist, create them
if not os.path.isdir('Attendance'):
    os.makedirs('Attendance')
if not os.path.isdir('static'):
    os.makedirs('static')
if not os.path.isdir('static/faces'):
    os.makedirs('static/faces')
if f'Attendance-{datetoday}.csv' not in os.listdir('Attendance'):
    with open(f'Attendance/Attendance-{datetoday}.csv', 'w') as f:
        f.write('Name,Roll,Time')


# get a number of total registered users
def totalreg():
    return len(os.listdir('static/faces'))


# extract the face from an image
def extract_faces(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_points = face_detector.detectMultiScale(gray, 1.2, 5, minSize=(20, 20))
        return face_points
    except:
        return []


# Identify face using ML model
def identify_face(facearray):
    model = joblib.load('static/face_recognition_model.pkl')
    return model.predict(facearray)


# A function which trains the model on all the faces available in faces folder
def train_model():
    faces = []
    labels = []
    userlist = os.listdir('static/faces')
    for user in userlist:
        for imgname in os.listdir(f'static/faces/{user}'):
            img = cv2.imread(f'static/faces/{user}/{imgname}')
            resized_face = cv2.resize(img, (50, 50))
            faces.append(resized_face.ravel())
            labels.append(user)
    faces = np.array(faces)
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(faces, labels)
    joblib.dump(knn, 'static/face_recognition_model.pkl')


# Extract info from today's attendance file in attendance folder
def extract_attendance():
    df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
    names = df['Name']
    rolls = df['Roll']
    times = df['Time']
    l = len(df)
    return names, rolls, times, l
# Extract info from today's attendance file in attendance folder
def extract_attendance1(datetoday1):
    df = pd.read_csv(f'Attendance/Attendance-{datetoday1}.csv')
    names = df['Name']
    rolls = df['Roll']
    times = df['Time']
    l = len(df)
    return names, rolls, times, l

# Add Attendance of a specific user
def add_attendance(name):
    username = name.split('_')[0]
    userid = name.split('_')[1]
    current_time = datetime.now().strftime("%H:%M:%S")

    df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
    if int(userid) not in list(df['Roll']):
        with open(f'Attendance/Attendance-{datetoday}.csv', 'a') as f:
            f.write(f'\n{username},{userid},{current_time}')


## A function to get names and rol numbers of all users
def getallusers():
    userlist = os.listdir('static/faces')
    names = []
    rolls = []
    l = len(userlist)

    for i in userlist:
        name, roll = i.split('_')
        names.append(name)
        rolls.append(roll)

    return userlist, names, rolls, l


## A function to delete a user folder 
def deletefolder(duser):
    pics = os.listdir(duser)
    for i in pics:
        os.remove(duser+'/'+i)
    os.rmdir(duser)

## API for add user
    
def call_add_user(iduser, nameuser, datejoin, dateout):
    url = 'https://serverweather.azurewebsites.net/api/adduser'

    headers = {
        'accept': '*/*',
        'Content-Type': 'application/json'
    }

    data = {
        "iduser":iduser ,
        "nameuser": nameuser,
        "datejoin": datejoin,
        "dateout": dateout
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)

    if response.status_code == 200:
        print("Gọi API thành công!")
        print("Response:", response.json())
    else:
        print("Gọi API không thành công. Mã trạng thái:", response.status_code)
        print("Lỗi:", response.text)

## API for delete user
    
def call_delete_user(iduser, nameuser, datejoin, dateout):
    url = 'https://serverweather.azurewebsites.net/api/deleteuser'

    headers = {
        'accept': '*/*',
        'Content-Type': 'application/json'
    }

    data = {
        "iduser":iduser ,
        "nameuser": nameuser,
        "datejoin": datejoin,
        "dateout": dateout
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)

    if response.status_code == 200:
        print("Gọi API thành công!")
        print("Response:", response.json())
    else:
        print("Gọi API không thành công. Mã trạng thái:", response.status_code)
        print("Lỗi:", response.text)

    
def call_attendance_user(iduser, logatt,daycheck):
    url = 'https://serverweather.azurewebsites.net/api/attendance'

    headers = {
        'accept': '*/*',
        'Content-Type': 'application/json'
    }

    data = {
        "iduser": iduser,
        "logatt": logatt,
        "daycheck": daycheck
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)

    if response.status_code == 200:
        print("Gọi API thành công!")
        print("Response:", response.json())
    else:
        print("Gọi API không thành công. Mã trạng thái:", response.status_code)
        print("Lỗi:", response.text)

################## ROUTING FUNCTIONS #########################

# Our main page
@app.route('/')
def home():
    names, rolls, times, l = extract_attendance()
    return render_template('home.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg(), datetoday2=datetoday2)


## List users page
@app.route('/listusers')
def listusers():
    userlist, names, rolls, l = getallusers()
    return render_template('listusers.html', userlist=userlist, names=names, rolls=rolls, l=l, totalreg=totalreg(), datetoday2=datetoday2)


## Delete functionality
@app.route('/deleteuser', methods=['GET'])
def deleteuser():
    duser = request.args.get('user')
    deletefolder('static/faces/'+duser)

    ## if all the face are deleted, delete the trained file...
    if os.listdir('static/faces/')==[]:
        os.remove('static/face_recognition_model.pkl')
    
    try:
        train_model()
    except:
        pass

    userlist, names, rolls, l = getallusers()
    return render_template('listusers.html', userlist=userlist, names=names, rolls=rolls, l=l, totalreg=totalreg(), datetoday2=datetoday2)


# Our main Face Recognition functionality. 
# This function will run when we click on Take Attendance Button.
@app.route('/start', methods=['GET'])
def start():
    names, rolls, times, l = extract_attendance()

    if 'face_recognition_model.pkl' not in os.listdir('static'):
        return render_template('home.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg(), datetoday2=datetoday2, mess='There is no trained model in the static folder. Please add a new face to continue.')
    
    ret = True
    cap = cv2.VideoCapture(0)
    while ret:
        ret, frame = cap.read()
        if len(extract_faces(frame)) > 0:
            (x, y, w, h) = extract_faces(frame)[0]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (86, 32, 251), 1)
            cv2.rectangle(frame, (x, y), (x+w, y-40), (86, 32, 251), -1)
            face = cv2.resize(frame[y:y+h, x:x+w], (50, 50))
            identified_person = identify_face(face.reshape(1, -1))[0]
            add_attendance(identified_person)
            cv2.putText(frame, f'{identified_person}', (x+5, y-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow('Attendance', frame)
        if cv2.waitKey(1) == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
    names, rolls, times, l = extract_attendance()
    return render_template('home.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg(), datetoday2=datetoday2)


# A function to add a new user.
# This function will run when we add a new user.
@app.route('/add', methods=['GET', 'POST'])
def add():
    newusername = request.form['newusername']
    newuserid = request.form['newuserid']
    userimagefolder = 'static/faces/'+newusername+'_'+str(newuserid)
    if not os.path.isdir(userimagefolder):
        os.makedirs(userimagefolder)
    i, j = 0, 0
    cap = cv2.VideoCapture(0)
    while 1:
        _, frame = cap.read()
        faces = extract_faces(frame)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 20), 2)
            cv2.putText(frame, f'Images Captured: {i}/{nimgs}', (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 20), 2, cv2.LINE_AA)
            if j % 5 == 0:
                name = newusername+'_'+str(i)+'.jpg'
                cv2.imwrite(userimagefolder+'/'+name, frame[y:y+h, x:x+w])
                i += 1
            j += 1
        if j == nimgs*5:
            break
        cv2.imshow('Adding new User', frame)
        if cv2.waitKey(1) == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
    print('Training Model')
    train_model()
    names, rolls, times, l = extract_attendance()
    # add time then add user
    formatted_time = datetime.now().strftime("%m_%d_%y %H:%M:%S")
    call_add_user(newuserid, newusername, formatted_time, "")

    return render_template('home.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg(), datetoday2=datetoday2)
#
@app.route('/det', methods=['GET', 'POST'])
def det():
    newusername = request.form['newusername1']
    newuserid = request.form['newuserid1']
    userimagefolder = 'static/faces/'+newusername+'_'+str(newuserid)
    deletefolder(userimagefolder)

    ## if all the face are deleted, delete the trained file...
    
    try:
        train_model()
    except:
        pass

    names, rolls, times, l = extract_attendance()
     # add time then delete user
    formatted_time = datetime.now().strftime("%m_%d_%y %H:%M:%S")
    call_delete_user(newuserid, newusername, "", formatted_time)
    return render_template('home.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg(), datetoday2=datetoday2)


## List users page
@app.route('/list1', methods=['GET', 'POST'])
def list1():
    userlist, names, rolls, l = getallusers()
    times = []
    return render_template('home.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg(), datetoday2=datetoday2)

## Show attendance 
@app.route('/att', methods=['GET', 'POST'])
def Att():
    dayy = request.form['datepicker']
    datetoday3 = datetime.now().strftime("%m_%d_%y %H:%M:%S")
    try:
        names, rolls, times, l = extract_attendance1(dayy)
    except:
        names, rolls, times, l = extract_attendance1(datetoday3)

    for i in range(l):
        username = names[i]
        userid = rolls[i]
        logatt = f"{username} has checked at {times[i]}"
        call_attendance_user(str(userid),str(logatt),datetoday)
    return render_template('home.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg(), datetoday2=datetoday2)


# Our main function which runs the Flask App
if __name__ == '__main__':
    app.run(debug=True)
