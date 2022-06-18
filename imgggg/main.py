import tkinter as tk
from tkinter import *
import cv2
import csv
import os
import numpy as np
from PIL import Image,ImageTk
import pandas as pd
import datetime
import time


import webbrowser
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

from PIL import ImageTk, Image
import os
i=2
j=2
t=0
#####Window is our Main frame of system

window = tk.Tk()
window.title("Face Recognition based Attendance System")
window.geometry('1280x720')
window.configure(bg="#B96985")


#Heading Configurations
# hed = Label(window ,text = "Face Recognition based Attendance System", bg = "#AD2F5B",fg="#e9ecef",font="Times 40")
#placing the widget on the screen

hed = Label(window,text = "Face Recognition based Attendance System", bg = "#AD2F5B",fg="#e9ecef",font="Times 40")
#placing the widget on the screen

hed.pack(fill=X)

def updatewindow(imagen):
    # resize the image to fill the whole screen
    pilImage = Image.open(imagen)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    image = ImageTk.PhotoImage(pilImage.resize((w,h)))
    # update the image
    canvas.itemconfig(imgbox, image=image)
    # need to keep a reference of the image, otherwise it will be garbage collected
    canvas.image = image

# window =  tk.Tk()
# window.attributes('-fullscreen', 1)
window.bind('<Escape>', lambda _: window.destroy())

canvas = tk.Canvas(window, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=1)
imgbox = canvas.create_image(0, 0, image=None, anchor='nw')

# show the first image
updatewindow('pandu.webp')
# change the image 5 seconds later
window.after(5000, updatewindow, 'pandu.webp')

############googlesheet API########

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds =ServiceAccountCredentials.from_json_keyfile_name("creds.json",scope)

client=gspread.authorize(creds)



def view_attendenceSpread():
    webbrowser.open('https://docs.google.com/spreadsheets/d/18pH4WMz4Kiw6Sjzk3swJtFSDCYoQPwiESHnRJOSKdVI/edit#gid=0')
    webbrowser.open('https://docs.google.com/spreadsheets/d/1CNfbgu50BETgix1m5TA0laE_-KZhvOlqe8Bp8G60L1A/edit#gid=0')


###For take images for datasets
def take_img():
    global i
    i=i+1

    cam = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    Id = txt.get()
    name = txt2.get()
    sampleNum = 0
    while (True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        faces = detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # incrementing sample number
            sampleNum = sampleNum + 1
            # saving the captured face in the dataset folder
            cv2.imwrite("dataset/ " + name + "." + Id + '.' + str(sampleNum) + ".jpg",
                                gray[y:y + h, x:x + w])
            cv2.imshow('Frame', img)
                # wait for 100 miliseconds
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
                # break if the sample number is morethan 100
        elif sampleNum > 200:
            break
    cam.release()
    cv2.destroyAllWindows()
        
    res = "Images Saved  : " + Id + " Name : " + name
    row = [Id , name]


    sheet=client.open("StudentDetails").sheet1

    row = [Id , name]
    sheet.insert_row(row,i)


    with open('StudentDetails\StudentDetails.csv','a+') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
    csvFile.close()
    Notification.configure(text=res, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
    Notification.place(x=250, y=400)
      


###For train the model
def trainimg():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    global detector
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    try:
        global faces,Id
        faces, Id = getImagesAndLabels("dataset")
    except Exception as e:
        l='please make "dataset" folder & put Images'
        Notification.configure(text=l, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
        Notification.place(x=350, y=400)

    recognizer.train(faces, np.array(Id)) 
    try:
        recognizer.save("model/trained_model2.yml")
    except Exception as e:
        q='Please make "model" folder'
        Notification.configure(text=q, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
        Notification.place(x=350, y=400)

    res = "Model Trained"  
    Notification.configure(text=res, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
    Notification.place(x=250, y=400)

	
	
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # create empth face list
    faceSamples = []
    # create empty ID list
    Ids = []
    # now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        # loading the image and converting it to gray scale
        pilImage = Image.open(imagePath).convert('L')
        # Now we are converting the PIL image into numpy array
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image

        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces = detector.detectMultiScale(imageNp)
        # If a face is there then append that in the list as well as Id of it
        for (x, y, w, h) in faces:
            faceSamples.append(imageNp[y:y + h, x:x + w])
            Ids.append(Id)
    return faceSamples, Ids



sheet_attend=client.open("Attendance").sheet1


def TrackImages():
    global j
    j=j+1
    global t
    recognizer = cv2.face.LBPHFaceRecognizer_create()              #cv2.createLBPHFaceRecognizer()
    recognizer.read("model/trained_model2.yml")
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);    
    df=pd.read_csv("StudentDetails\StudentDetails.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX        
    col_names =  ['Id','Name','Date','Time']
    attendance = pd.DataFrame(columns = col_names)
    while True:
        ret, im =cam.read()
        gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        faces=faceCascade.detectMultiScale(gray, 1.2,5)    
        for(x,y,w,h) in faces:
            cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
            Id, conf = recognizer.predict(gray[y:y+h,x:x+w])                        
            if(conf < 50):
                ts = time.time()                 
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa=df.loc[df['Id'] == Id]['Name'].values
                t=Id
                tt=str(Id)+"-"+aa
                attendance.loc[len(attendance)] = [Id,aa,date,timeStamp]
                confidence = "  {0}%".format(round(100 - conf))
                
            else:
                Id='Unknown'             
                tt=str(Id)   
            if(conf > 75):
                noOfFile=len(os.listdir("ImagesUnknown"))+1
                confidence = "  {0}%".format(round(100 - conf))
                cv2.imwrite("ImagesUnknown\Image"+str(noOfFile) + ".jpg", im[y:y+h,x:x+w])            
            cv2.putText(im,str(tt),(x+5,y-5), font, 1,(255,255,255),2)        
            cv2.putText(im,str(confidence),(x+5,y+h-5), font, 1,(255,255,255),2)        
        attendance=attendance.drop_duplicates(subset=['Id'],keep='first')    
        cv2.imshow('im',im) 
        if (cv2.waitKey(1)==ord('q')):
            break
    ts = time.time()      
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour,Minute,Second=timeStamp.split(":")
    fileName="Attendance/Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
    attendance.to_csv(fileName,index=False)
    cam.release()
    cv2.destroyAllWindows()
    res = attendance
    Notification.configure(text=res, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
    Notification.place(x=250, y=400)
    print(attendance)



    pandu=[t,aa[0],date,timeStamp]
    sheet_attend.insert_row(pandu,j)



window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)


def on_closing():
    from tkinter import messagebox
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()
window.protocol("WM_DELETE_WINDOW", on_closing)



Notification = tk.Label(window, text="All things good", bg="Green", fg="white", width=15, height=3)

def testVal(inStr,acttyp):
    if acttyp == '1': #insert
        if not inStr.isdigit():
            return False
    return True
	
	
lbl = tk.Label(window, text="Enter id", width=20, height=2, fg="black", bg="lightblue", font=('times', 20, 'italic bold '))
lbl.place(x=200, y=200)

txt = tk.Entry(window, validate="key", width=20,  fg="red", font=('times', 20, 'italic bold '))
txt['validatecommand'] = (txt.register(testVal),'%P','%d')	
txt.place(x=550, y=210)

lbl2 = tk.Label(window, text="Enter Name", width=20, fg="black", bg="lightblue",  height=2, font=('times', 20, 'italic bold '))
lbl2.place(x=200, y=300)

txt2 = tk.Entry(window, width=20, fg="red", font=('times', 20, 'italic bold '))
txt2.place(x=550, y=310)

takeImg = tk.Button(window, text="Capture Images",command=take_img,fg="black", bg="#DDA0DD"  ,width=20  ,height=2, activebackground = "Red" ,font=('times', 20, 'italic bold '))
takeImg.place(x=165, y=500)

trainImg = tk.Button(window, text="Train Model",fg="black",command=trainimg ,bg="#DDA0DD"  ,width=20  ,height=2, activebackground = "Red",font=('times', 20, 'italic bold '))
trainImg.place(x=510, y=500)

trackImg = tk.Button(window, text="Detect Images",fg="black",command=TrackImages ,bg="#DDA0DD"  ,width=20  ,height=2, activebackground = "Red",font=('times', 20, 'italic bold '))
trackImg.place(x=855, y=500)

viewAttendSpread_sheet = tk.Button(window, text="View Attendance",fg="black",command=view_attendenceSpread ,bg="#DDA0DD"  ,width=20  ,height=2, activebackground = "Red",font=('times', 20, 'italic bold '))
viewAttendSpread_sheet.place(x=510, y=610)
window.mainloop()