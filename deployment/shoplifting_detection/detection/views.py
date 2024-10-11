import os
import cv2
import numpy as np
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from tensorflow.keras.models import load_model

# Load your model
model_path = os.path.join(os.path.dirname(__file__), 'shoplifting_detection_model.h5')
model = load_model(model_path)

# Function to process video frames
def extract_frames(video_path):
    video = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = video.read()
        if not ret:
            break
        # Optionally resize frame for the model
        frame_resized = cv2.resize(frame, (224, 224))  # Assumes model takes 224x224 input
        frames.append(frame_resized)
        # If we have 25 frames, stop collecting
        if len(frames) == 25:
            break
    video.release()
    return np.array(frames)

# Function to predict video classification
def predict_video_classification(frames):
    # Ensure frames have the correct shape (1, 25, 224, 224, 3)
    frames = np.expand_dims(frames, axis=0)  # Add batch dimension
    predictions = model.predict(frames)  # This should match the model input shape
    return predictions  # Averaging predictions for all frames

# Video upload view
def video_upload(request):
    if request.method == 'POST' and request.FILES['video']:
        video = request.FILES['video']
        fs = FileSystemStorage()
        filename = fs.save(video.name, video)
        video_path = fs.path(filename)

        # Extract frames and make predictions
        frames = extract_frames(video_path)
        if len(frames) < 25:
            return render(request, 'upload.html', {'error': 'Video must contain at least 25 frames.'})

        prediction = predict_video_classification(frames)
        
        # Process prediction
        # Assuming prediction is a 2D array: shape (1, num_classes)
        if prediction.shape[1] == 1:  # Binary classification
            predicted_class = 1 if prediction[0, 0] > 0.5 else 0  # 1 for shoplifter, 0 for non-shoplifter
            result = "Shoplifter Detected" if predicted_class == 1 else "Non-Shoplifter"
        else:  
            class_index = np.argmax(prediction, axis=1)[0]
            if class_index == 0:
                class_index = "No Shoplifting Detected"
                result = f"Everything is good ,{class_index}"
            elif class_index == 1:
                class_index = "Shoplifter Detected"
                result = f"Alert: {class_index}!!"
            

        return render(request, 'result.html', {'result': result})

    return render(request, 'upload.html')



def home(request):
    return render(request, 'home.html')