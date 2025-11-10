import os
import io
import numpy as np
import tensorflow as tf
from PIL import Image

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.normpath(os.path.join(_CURRENT_DIR, '..', 'cdd_model.keras'))
model = None

CLASS_NAMES = [
    "Apple_Apple_scab",
    "Apple_Black_rot",
    "Apple_Cedar_apple_rust",
    "Apple_Healthy",
    "Background_without_leaves",
    "Blueberry_Healthy",
    "Cherry_Healthy",
    "Cherry_Powdery_mildew",
    "Corn_Cercospora_leaf_spot",
    "Corn_Common_rust",
    "Corn_Healthy",
    "Corn_Northern_leaf_blight",
    "Grape_Black_rot",
    "Grape_Esca_black_measles",
    "Grape_Healthy",
    "Grape_Leaf_blight_isariopsis_leaf_spot",
    "Orange_Haunglongbing_citrus_greening",
    "Peach_Bacterial_spot",
    "Peach_Healthy",
    "Pepper_bell_Bacterial_spot",
    "Pepper_bell_Healthy",
    "Potato_Early_blight",
    "Potato_Healthy",
    "Potato_Late_blight",
    "Raspberry_Healthy",
    "Soybean_Healthy",
    "Squash_Powdery_mildew",
    "Strawberry_Healthy",
    "Strawberry_Leaf_scorch",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_Healthy",
    "Tomato_Late_blight",
    "Tomato_Leaf_mold",
    "Tomato_Mosaic_virus",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Target_spot",
    "Tomato_Two_spotted_spider_mite",
    "Tomato_Yellow_leaf_curl_virus",
]

def load_model():
    """Load the Keras model into memory."""
    global model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found at {MODEL_PATH}. "
            "Make sure the path is correct relative to where you run the script."
        )
    
    print(f"Loading model from {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully.")

def preprocess_image_from_bytes(image_bytes: bytes, target_size=(224, 224)) -> np.ndarray:
    """Preprocesses the uploaded image from bytes to be ready for the model."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize(target_size)
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_image(image_bytes: bytes):
    """Takes image bytes, preprocesses it, and returns prediction label and confidence."""
    if model is None:
        return {"error": "Model is not loaded. Please check server logs."}

    try:
        processed_image = preprocess_image_from_bytes(image_bytes)
        predictions = model.predict(processed_image)
        confidence = float(np.max(predictions))
        predicted_class_index = np.argmax(predictions)
        prediction_label = CLASS_NAMES[predicted_class_index]
        
        return {"prediction_label": prediction_label, "confidence": confidence}
    except Exception as e:
        return {"error": f"Failed to process or predict image: {str(e)}"}

