import cv2
import tensorflow as tf
import keras
from keras.models import load_model
import keras_cv
import numpy as np

import warnings
warnings.filterwarnings("ignore")

class_names = ['Coccidiosis', 'Healthy', 'Newcastle Disease', 'Salmonella']
model = load_model("model/poultry_disease_classification.keras")

def resize_image_with_aspect_ratio(image_path, target_size):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image/255.0
    height, width = image.shape[:2]
    
    # Calculate the aspect ratio
    aspect_ratio = width / height
    
    if aspect_ratio > 1:
        new_width = int(target_size[0] * aspect_ratio)
        resized_image = cv2.resize(image, (new_width, target_size[1]))
        crop_start = (new_width - target_size[0]) // 2
        cropped_image = resized_image[:, crop_start:crop_start + target_size[0]]
    else:
        new_height = int(target_size[1] / aspect_ratio)
        resized_image = cv2.resize(image, (target_size[0], new_height))
        crop_start = (new_height - target_size[1]) // 2
        cropped_image = resized_image[crop_start:crop_start + target_size[1], :]

    return cropped_image

# Example usage
image_path_ = ""
target_size = (360, 360)
resized_image = resize_image_with_aspect_ratio(image_path_, target_size)
resize_image = np.expand_dims(resized_image, axis = 0)
ccpred = model.predict(resize_image)
pred = np.argmax(ccpred, axis = 1)[0]

print(f"Detected disease is: {class_names[pred]}")