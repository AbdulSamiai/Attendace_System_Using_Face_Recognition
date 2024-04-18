import datetime
import warnings
from os import listdir
import cv2
import face_recognition
import pandas as pd
import pyodbc
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageDraw

import DatabaseQueries.db as db
import Model.Person as mp

app = FastAPI()
networkip = '192.168.0.114'
networkport = 8000
# 'rtsp://192.168.0.108:8080/h264_ulaw.sdp'
# cmaeraip = 'rtsp://192.168.0.112:8000/h264_ulaw.sdp'
# cmaeraip1 = 'rtsp://192.168.0.118:8080/h264_ulaw.sdp'
# cmaeraip2 = 'rtsp://192.168.0.105:8080/h264_ulaw.sdp'


templates = Jinja2Templates(directory="templates")

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
#---------------------------Camera-----------------------------------------

    
def gen_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            cv2.imwrite('test_images/new.jpg', frame)
            test_image =  face_recognition.load_image_file('test_images/new.jpg')
            face_locations = face_recognition.face_locations(test_image)
            face_encodings = face_recognition.face_encodings(test_image,face_locations)
            pil_image = Image.fromarray(test_image)
            draw = ImageDraw.Draw(pil_image)
            warnings.filterwarnings("ignore") 
            for(top,right,bottom,left), face_encoding in zip(face_locations,face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings,face_encoding)
                name="Unknown Person"
                
                
                if True in matches:
                    first_match_index= matches.index(True)
                    name = know_face_names[first_match_index]
                    current_time = datetime.datetime.now()
                    time = str(current_time.hour) +':'+ str(current_time.minute) +':'+ str(current_time.second)
                    day = str(current_time.day) +'/'+ str(current_time.month) +'/'+ str(current_time.year)
                    res = person_object.person_details(status=status,person= mp.Person(name=name,time=time,day=day),check=0)
                    if res==0:
                        if status =='CHECK_IN':
                            person_object.add(status=status,person= mp.Person(name=name,time=time,day=day))
                            person_object.add(status='CHECK_OUT',person= mp.Person(name=name,time='0',day=day)) 
                    else:
                        if status =='CHECK_OUT':
                            res = person_object.person_details(status=status,person= mp.Person(name=name,time=time,day=day),check=1)
                            if res=="0":
                                person_object.update(status=status,person= mp.Person(name=name,time=time,day=day))
                                
                draw.rectangle(((left,top),(right,bottom)),outline=(0,0,0))
                text_width,text_height = draw.textsize(name)
                draw.rectangle(((left,bottom - text_height-10),(right,bottom)),fill=(0,0,0),outline=(0,0,0))
                draw.text((left+6,bottom - text_height -5),name,fill=(255,255,255,255))
            del draw
            
            rgb_im = pil_image.convert('RGB')
            rgb_im.save('rgb.jpg')
            img = cv2.imread('rgb.jpg')
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get('/get_data')
def get_data():
    cursor.execute(f'''
                SELECT * FROM CHECK_IN
                    ''')
    name=[]
    time=[]
    day=[]
    for row in cursor.fetchall():
        name.append(row.CNAME)
        time.append(row.CTIMEIN)
        day.append(row.CDAY)
    conn.commit()

    cursor.execute(f'''
                    SELECT * FROM CHECK_OUT
                        ''')
    timeout=[]
    for row in cursor.fetchall():
        timeout.append(row.CTIMEOUT)
    conn.commit()
    d = {'Name': name, 'Day': day,'Time_In':time,'Time_Out':timeout}
    df = pd.DataFrame(data=d)
    current_time = datetime.datetime.now()
    time = str(current_time.hour) + str(current_time.minute) + str(current_time.second)
    day = str(current_time.day) + str(current_time.month) + str(current_time.year)
    df.to_csv(f'{time}{day}.csv')
    return "File Saved Successfully..."
    
    

if __name__=='__main__':
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-DKL7AJ3\SQLEXPRESS;'
                      'Database=FACE_RECOGNITION;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    person_object = db.Persondb(cursor,conn)
    known_face_encodings=[] 

    know_face_names=[]
    def loadImages(path):
        imagesList = listdir(path)
        for img in imagesList:
            image =  face_recognition.load_image_file(path + img)
            image_encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(image_encoding)
            know_face_names.append(img.split('.')[0])

    path = "./images/"

    loadImages(path)
    # CHECK_IN
    # CHECK_OUT
    status ='CHECK_OUT'

    uvicorn.run(app, host=networkip,port=networkport)
    
    
    
    
    
    
    
    
    
    
    
   