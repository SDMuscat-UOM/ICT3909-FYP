# Testing all models work before implementing them in web application
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw
import requests

# Create an inference client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="8cAMfdvIvnyyRJECKL1W"
)

# Inference on a local image
image_path = "sample_images/000001.png"
result = CLIENT.infer(image_path, model_id="thesis-q2hxq/1")

# Load image
image = Image.open(image_path)
draw = ImageDraw.Draw(image)

# Draw bounding boxes
for prediction in result['predictions']:
    x = prediction['x']
    y = prediction['y']
    w = prediction['width']
    h = prediction['height']
    label = prediction['class']
    confidence = prediction['confidence']

    # Convert centre-based x, y to top-left corner
    left = x - w / 2
    top = y - h / 2
    right = x + w / 2
    bottom = y + h / 2

    # Draw rectangle
    draw.rectangle([left, top, right, bottom], outline="red", width=3)
    draw.text((left, top - 10), f"{label} ({confidence:.2f})", fill="red")

# Show or save the result
image.show()
# image.save("output.png")
