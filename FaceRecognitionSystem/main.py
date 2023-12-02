# we will retrieve the information of the participant by id because name can be duplicated
import os
import pickle

import cvzone
import face_recognition
import numpy as np

import cv2
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://faceattendance-4f974-default-rtdb.firebaseio.com/",
    "storageBucket": "faceattendance-4f974.appspot.com"
})

buket = storage.bucket()

# Here we open the camera and specify width and height
cap = cv2.VideoCapture(0)

# Note the resolution here like that because the image which we want the video to display in has this resolutions
"""
This line sets the width of the captured frames to 640 pixels. The 3 argument corresponds to the CAP_PROP_FRAME_WIDTH
property of the VideoCapture object
"""
cap.set(3, 640)
"""
This line sets the height of the captured frames to 480 pixels. The 4 argument corresponds to the CAP_PROP_FRAME_HEIGHT
property of the VideoCapture object.
"""
cap.set(4, 480)

image_background = cv2.imread("Resources/background.png")

"""folderModePath = "Resources/Modes": This line defines a variable named folder_mode_path and stores the path to 
the folder containing the image files.

modePathList = os.listdir(folder_mode_path): This line lists the contents of the folder_mode_path directory and stores 
the list in the mode_path variable. The os.listdir() function returns a list of filenames in the specified directory.

img_Mode_List = []: This line creates an empty list named img_Mode_List to store the loaded images.

for path in mode_path:: This for loop iterates over the list of filenames in mode_path.

imgModeList.append(cv2.imread(os.path.join(folderModePath, path))): This line reads the image file at the current 
path and appends it to the img_Mode_List. The cv2.imread() function reads the image file and returns a NumPy array 
representing the image data. The os.path.join() function constructs the full path to the image file.

"""
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

file = open("Encoding File.p", "rb")
# Load the file (Matrix of information)
encodedList_ids = pickle.load(file)
file.close()
encodedList, participant_IDS = encodedList_ids
# Testing: print(participant_IDS)


mode_type = 0
counter = 0
id = -1
img_participant = []

while True:
    """
    This line captures a frame from the webcam and stores it in the img variable. The success variable indicates whether
    the frame was successfully captured or not.
    """
    success, img = cap.read()
    # Make image small for Computational power and make the same change of it
    img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

    # Here we want to compare faces between encoded_faces and the faces in current_frame
    face_currunt_Frame = face_recognition.face_locations(img_small)
    # Here this is the image and this is location go and find
    # Note we want to find the encoding_faces not the total image
    encode_current_frame = face_recognition.face_encodings(img_small, face_currunt_Frame)


    """
    This line displays the captured frame in a window named "Face Attendance". The cv2.imshow() function creates
    a new window and displays the specified image in it.
    """
    image_background[162:162 + 480, 55:55 + 640] = img

    # Display the mode on the right
    image_background[44:44 + 633, 808:808 + 414] = imgModeList[mode_type]
    # Testing : cv2.imshow("web cam", img)
    """
    This line waits for a key press for 1 millisecond. The cv2.waitKey() function returns an integer representing
    the ASCII code of the key pressed, or -1 if no key was pressed.
    """
    if face_currunt_Frame:
        for encodeFace, faceLocation in zip(encode_current_frame, face_currunt_Frame):
            matches = face_recognition.compare_faces(encodedList, encodeFace)
            face_distance = face_recognition.face_distance(encodedList, encodeFace)
            # Testing: print("matches", matches)
            # Testing: print("face_distance", face_distance)
            # Expected output
            """
            Here the matches refer to the labels of the images and the distances between the current frame and the encoded
            the lower the distances the better it perform
            matches [True, False, False]
            face_distance [0.48635008 0.65844058 0.84078072]
            """
            # Know we want to make use of the distances the lower distance I mean
            match_idx = np.argmin(face_distance)
            # Testing: print("Match_index", match_idx) output : Match_index 0 (in my case this is the output because the
            # first one is my image)

            if matches[match_idx]:
                # Testing to print the sentence and the id of the participants
                # Testing: print("Known Face Detected")
                # Testing: print(participant_IDS[match_idx])
                y1, x2, y2, x1 = faceLocation
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                image_background = cvzone.cornerRect(image_background, bbox, rt=0)
                id = participant_IDS[match_idx]

                if counter == 0:
                    counter = 1
                    mode_type = 1
                    image_background[44:44 + 633, 808:808 + 414] = imgModeList[mode_type]

            if counter != 0:

                if counter == 1:
                    # Getting the data
                    participant_info = db.reference(f"Participants/{id}").get()
                    print(participant_info)
                    # Get the Image from the storage
                    blob = buket.get_blob(f'images/{id}.jpg')

                    array = np.frombuffer(blob.download_as_string(), np.uint8)

                    img_participant = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                    # Update data of attendance
                    datetimeObject = datetime.strptime(participant_info['last_attendance_time'],
                                                       "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    print(secondsElapsed)
                    if secondsElapsed > 30:
                        ref = db.reference(f"Participants/{id}")
                        participant_info["total_attendance"] += 1
                        ref.child("total_attendance").set(participant_info["total_attendance"])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        mode_type = 3
                        counter = 0
                        image_background[44:44 + 633, 808:808 + 414] = imgModeList[mode_type]

                if mode_type != 3:
                    if 10 < counter < 20:
                        mode_type = 2
                    image_background[44:44 + 633, 808:808 + 414] = imgModeList[mode_type]
                    if counter <= 10:
                        cv2.putText(image_background, str(participant_info['total_attendance']), (861, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(image_background, str(participant_info['Major']), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(image_background, str(id), (1006, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(image_background, str(participant_info['standing']), (910, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(image_background, str(participant_info['year']), (1025, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(image_background, str(participant_info['starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        (w, h), _ = cv2.getTextSize(participant_info['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(image_background, str(participant_info['name']), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                        image_background[175:175 + 216, 909:909 + 216] = img_participant

                    counter += 1

                    if counter >= 20:
                        counter = 0
                        mode_type = 0
                        participant_info = []
                        img_participant = []
                        image_background[44:44 + 633, 808:808 + 414] = imgModeList[mode_type]
    else:
        mode_type = 0
        counter = 0

    cv2.imshow("Face Attendance", image_background)
    cv2.waitKey(1)
