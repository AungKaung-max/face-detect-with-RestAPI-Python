import cv2
import requests
import numpy as np
import face_recognition
import base64

def recognize_faces():
    # Get a reference to webcam
    video_capture = cv2.VideoCapture(0)

    # URL of your Node.js API endpoint
    api_url = 'http://localhost:5000/known-faces'

    try:
        # Get known faces data from your Node.js API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        known_faces_data = response.json()
    except Exception as e:
        print("Error fetching known faces data from API:", e)
        return

    if not known_faces_data:
        print("No known faces data received from API")
        return

    known_face_encodings = []
    known_face_names = []

    for face_data in known_faces_data:
        name = face_data.get('name')
        image_data = face_data.get('data')

        if not name or not image_data:
            print("Invalid known face data received from API")
            continue

        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        face_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        face_encodings = face_recognition.face_encodings(face_image)

        if not face_encodings:
            print("No face detected in the image")
            continue

        face_encoding = face_encodings[0]  # Assuming only one face per image
        known_face_encodings.append(face_encoding)
        known_face_names.append(name)

    while True:
        ret, frame = video_capture.read()

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            if not known_face_encodings:
                break

            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            
            # Only show the percentage if the face is recognized (not "Unknown")
            if name != "Unknown":
                match_percentage = 100 - int(face_distances[best_match_index] * 100)
                cv2.putText(frame, f"{name} - {match_percentage}%", (left + 6, bottom - 6),
                            font, 0.5, (255, 255, 255), 1)
            else:
                cv2.putText(frame, name, (left + 6, bottom - 6),
                            font, 0.5, (255, 255, 255), 1)
            
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# Call the function to start face recognition
recognize_faces()
