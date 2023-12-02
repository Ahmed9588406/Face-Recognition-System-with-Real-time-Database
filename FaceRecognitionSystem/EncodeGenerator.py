import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "",
    "storageBucket": ""
})

# Importing images of participants

"""folder_participants_path = "images": This line defines a variable named folder_participants_path and stores the 
path to the folder containing the image files.

path_List = os.listdir(folder_participants_path): This line lists the contents of the folder_participants_path 
directory and stores the list in the path_List variable. The os.listdir() function returns a list of filenames in the 
specified directory.

print(path_List): This line prints the list of filenames in path_List. This is useful for debugging purposes.

img_List = []: This line creates an empty list named img_List to store the loaded images.

participant_IDS = []: This line creates an empty list named participant_IDS to store the corresponding participant 
IDs for each image.

for path in path_List:: This for loop iterates over the list of filenames in path_List.

img_List.append(cv2.imread(os.path.join(folder_participants_path, path))): This line reads the image file at the 
current path (os.path.join(folder_participants_path, path)) and appends it to the img_List. The cv2.imread() function 
reads the image file and returns a NumPy array representing the image data.

participant_IDS.append(participant_ID_from_filename(path)): This line extracts the participant ID from the filename 
and appends it to the participant_IDS list. The participant_ID_from_filename() function assumes that the filename has 
a specific format that encodes the participant ID.

participant_IDS.append(os.path.splitext(path)[0]): This line appends the extracted
participant ID to the participant_IDS list.
"""


folder_participants_path = "images"
path_List = os.listdir(folder_participants_path)
# Testing: print(path_List)
img_List = []
participant_IDS = []
for path in path_List:
    img_List.append(cv2.imread(os.path.join(folder_participants_path, path)))
    participant_IDS.append(os.path.splitext(path)[0])
    # Testing: print(os.path.splitext(path)[0])
    """filename = f"{folder_participants_path}/{path}": This line creates a variable named filename that stores the 
    full path to the image file.

bucket = storage.bucket(): This line retrieves the Cloud Storage bucket using the storage.bucket() function.

blob = bucket.blob(filename): This line creates a blob object representing the image file in the Cloud Storage bucket.

blob.upload_from_filename(filename): This line uploads the image file from the local file path (filename) to the 
Cloud Storage bucket."""
    filename = f"{folder_participants_path}/{path}"
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)


# Testing: print(participant_IDS)


"""
def find_encoding(imagesList):: This line defines a function named find_encoding that takes a list of images as input.

encodedList = []: This line creates an empty list named encodedList to store the encoded faces.

for img in imagesList:: This for loop iterates over the list of images in imagesList.

img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB): This line converts the image from BGR color space to RGB color space. The face recognition algorithm requires RGB images.

encode = face_recognition.face_encodings(img)[0]: This line encodes the face in the image img using the face_recognition.face_encodings() function. The result is a list of encodings, and the first encoding is taken.

encodedList.append(encode): This line appends the encoded face to the encodedList.

return encodedList: This line returns the list of encoded faces.

print("Encoding Started ..."): This line prints a message to indicate that the encoding process has started.

encodedList = find_encoding(img_List): This line calls the find_encoding() function to encode the faces in the img_List.
The result is stored in the encodedList variable.

encodedList_ids = [encodedList, participant_IDS]: This line creates a list named encodedList_ids that contains
the encoded faces and corresponding participant IDs.

print("Encoding Complete"): This line prints a message to indicate that the encoding process has completed.

file = open("Encoding File.p", "wb"): This line opens a file named "Encoding File.p" in binary write mode.

pickle.dump(encodedList_ids, file): This line pickles the encodedList_ids list and saves it to the open file.

file.close(): This line closes the open file.

print("File Saved"): This line prints a message to indicate that the encoded faces and participant IDs have been saved to the file.
"""
def find_encoding(imagesList):
    encodedList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodedList.append(encode)

    return encodedList


print("Encoding Started ...")
encodedList = find_encoding(img_List)
encodedList_ids = [encodedList, participant_IDS]
print("Encoding Complete")

file = open("Encoding File.p", "wb")
pickle.dump(encodedList_ids, file)
file.close()
print("File Saved")



