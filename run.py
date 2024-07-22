import sys,json,numpy as np
import face_recognition
import cv2
import glob,os
from pathlib import Path
import numpy as np

home = str(os.path.dirname(os.path.abspath(__file__))) + "/" # "/../../"
file_names = glob.glob(home + "/known_people/*.jp*g")

def read_in():
    lines = sys.stdin.readline()
    return lines



def authorised(name):
    return not "Unknown" in name


def main():
    print("in the main Fucntion")
    home = str(os.path.dirname(os.path.abspath(__file__))) +  "/" # "/../../"
    print("home : "+ home)

    known_encodings_file_path = home + "/data/known_encodings_file.csv"
    people_file_path = home + "/data/people_file.csv"
    known_encodings_file = Path(known_encodings_file_path)
    if known_encodings_file.is_file():
        known_encodings = np.genfromtxt(known_encodings_file, delimiter=',')
    else:
        known_encodings = []

    people_file = Path(people_file_path)
    if people_file.is_file():
        people = np.genfromtxt(people_file, dtype='U',delimiter=',')
    else:
        people = []




    video_capture = cv2.VideoCapture(0)

    original_width = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    original_height = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)


    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    while True:


        if video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)!=original_width or video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)!= original_height:
            video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, original_width)
            video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, original_height)
        ret, frame = video_capture.read()


        if not ret:
            continue
        small_frame = cv2.resize(frame, (0,0), fx=.25, fy=.25)

        if process_this_frame:
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)

            face_names=[]
            other = 0 
            for face_encoding in face_encodings:
                match = face_recognition.compare_faces(known_encodings, face_encoding)
                name = "Unknown"

                for i in range(len(match)):
                    if match[i]:
                        name = people[i]
                        print(name+ "\n")

                if "Unknown" in name:
                    other += 1
                    name += str(other)
                face_names.append(name)
            print(face_names, flush=True)
        process_this_frame = not process_this_frame

        for (top, right, bottom, left),name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            color =  (0,255,0)  
            if not authorised(name):
                color = (0,0,255) 

            cv2.rectangle(frame, (left,top), (right,bottom), color, 2)

            cv2.rectangle(frame, (left,bottom-35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name,(left+6, bottom-6), font, 1.0, (255,255,255), 1)

        cv2.imshow('Video', frame)

        if cv2.waitKey(100) == 27:
            break
            
    video_capture.release()
    cv2.closeAllWindows()


if __name__ == '__main__':
    main()
