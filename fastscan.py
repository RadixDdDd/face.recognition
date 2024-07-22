import requests
import sys,json
import face_recognition
import cv2
import glob,os
from pathlib import Path
import numpy as np
from time import gmtime, strftime


home = str(os.path.dirname(os.path.abspath(__file__))) + "/" # "/../../"
file_names = glob.glob(home + "/known_people/*.jp*g")



def read_in():
    lines = sys.stdin.readline()
    return lines



def authorised(name):
    return not "Unknown" in name

r = requests.get('http://192.168.8.102:8080/video', auth=('user', 'password'), stream=True)

def get_frame_from_stream(r):
    if(r.status_code == 200):
        bytes_buffer = bytes()
        for chunk in r.iter_content(chunk_size=1024):
            bytes_buffer += chunk
            a = bytes_buffer.find(b'\xff\xd8')
            b = bytes_buffer.find(b'\xff\xd9')
            #print("run")
            if a != -1 and b != -1:
                jpg = bytes_buffer[a:b + 2]
                bytes_buffer = bytes_buffer[b + 2:]
                i = cv2.imdecode(np.fromstring(
                    jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                yield i

    else:
        print("Received unexpected status code {}".format(r.status_code))
        return None



def main():

    home = str(os.path.dirname(os.path.abspath(__file__))) + "/"  # "/../../"

    known_encodings_file_path = home + "/data/known_encodings_file.csv"
    people_file_path = home + "/data/people_file.csv"
    known_encodings_file = Path(known_encodings_file_path)
    if known_encodings_file.is_file():
        known_encodings = np.genfromtxt(known_encodings_file, delimiter=',')
    else:
        known_encodings = []

    people_file = Path(people_file_path)
    if people_file.is_file():
        people = np.genfromtxt(people_file, dtype='U', delimiter=',')
    else:
        people = []
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    for frame in get_frame_from_stream(r):

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        if process_this_frame:
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)

            face_names=[]
            other = 0 
            for face_encoding in face_encodings:
                match = face_recognition.compare_faces(known_encodings, face_encoding,0.5)
                name = "Unknown"

                for i in range(len(match)):
                    if match[i]:
                        name = people[i]
                        print(name+ "\n")
                        showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        file = open("testname.txt", "a")
                        file.write(showtime + "  " + name + "\n")

                        file.close()
                        break
                if "Unknown" in name:
                    other += 1
                    name += str(other)
                face_names.append(name)
            print(face_names, flush=True)
        process_this_frame = not process_this_frame

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            color = (0, 255, 0) 
            if not authorised(name):
                color = (0, 0, 255)  



            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)


            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2.imshow('imafast', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break



      #  if cv2.waitKey(1) == 27:
       #     cv2.destroyAllWindows()
            #exit(0)
        #print("fram")

    """
for frame in get_frame_from_stream(r):
    print (frame)


   # img = r
    print("int   " + str(r) )
    cv2.imshow('imafes', frame)
    if cv2.waitKey(1) == 27:
        exit(0)
    print("fram")"""

#start process
if __name__ == '__main__':
    main()


#recog.append(people[i])
"""      print("List :" + str(recog))
                        mySet = set(recog)
                        print("Set :" + str(mySet))

                        if people[i] in mySet:
                             name = str(people[i]) + " (Already)"
                        else:
                            name = people[i]


                            print(name+ "\n")
                            file = open("testname.txt", "a")
                            file.write(name + "\n")

                            file.close()
                        break"""""
