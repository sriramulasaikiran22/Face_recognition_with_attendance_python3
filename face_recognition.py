import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

path = 'imageBasic'
images = []
classNames = []
mylist = os.listdir(path)
print(mylist)

# getting the images from the path folder into the images list.
for cl in mylist:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

print(classNames)

# finding the encodings images and saving it as list.
def findEncodings(images):
    encodings = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodings.append(encode)

    return encodings


# marking the attendance with name, data and time
def markAttendance(name):

    with open('AttendanceList.csv', 'r+') as f:
        myDataList = f.readlines()
        names = []
        for list in myDataList:
            entry = list.split(',')
            names.append(entry[0])
        if name not in names:
            now = datetime.now()
            dtstr = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name}, {dtstr}')


encodingsListKnown = findEncodings(images)
print('encoding complete.')

cam = cv2.VideoCapture(0)

while True:
    success, frame = cam.read()
    if cv2.waitKey(40) == 27:
        break
    imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurLoc = face_recognition.face_locations(imgS)  # there could be no. of face so we are finding all
    encode = face_recognition.face_encodings(imgS, faceCurLoc)

    for encodes, faceCurLoc in zip(encode, faceCurLoc):
        matches = face_recognition.compare_faces(encodingsListKnown, encodes)
        faceDis = face_recognition.face_distance(encodingsListKnown, encodes)
        matchIndex = np.argmin(faceDis)  # numpy's 'argmin' gives the index of minimum face distance value

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            print(name)
            y1, x2, y2, x1 = faceCurLoc
            # when wee converting bgr to rgb we are resizing it by 1/4 th time. so we need to multiply with 4 to locs.
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cv2.rectangle(frame, (x1, y2-36), (x2, y2), (0, 255, 0), -1)
            cv2.putText(frame, name, (x1+6, y2-6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            markAttendance(name)

    cv2.imshow('image', frame)

cam.release()
cv2.destroyAllWindows()
