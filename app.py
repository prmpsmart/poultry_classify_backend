from typing import Optional
import warnings

warnings.filterwarnings("ignore")


import cv2, numpy, base64, os, json
from keras.models import load_model

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

dirname = os.path.dirname(__file__)
db = os.path.join(dirname, "db")

if not os.path.isfile(db):
    f = open(db, "w")
    f.write("{}")
    f.close()

users = json.load(open(db))


def save():
    json.dump(users, open(db, "w"))


class_names = ["Coccidiosis", "Healthy", "Newcastle Disease", "Salmonella"]
model = load_model(
    os.path.join(
        dirname,
        "model/poultry_disease_classification.keras",
    ),
)


def read_image_from_base64(base64_string: str) -> cv2.typing.MatLike:
    # Decode the base64 string to bytes
    image_bytes = base64.b64decode(base64_string)

    # Convert the bytes to numpy array
    image_array = numpy.frombuffer(image_bytes, numpy.uint8)

    # Decode the image array using OpenCV
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    return image


def resize_image_with_aspect_ratio(
    *,
    image_string: str = "",
    image_path: str = "",
    target_size: tuple = (360, 360),
):
    assert image_string or image_path

    if image_path:
        image = cv2.imread(image_path)
    else:
        image = read_image_from_base64(image_string)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]

    # Calculate the aspect ratio
    aspect_ratio = width / height

    if aspect_ratio > 1:
        new_width = int(target_size[0] * aspect_ratio)
        resized_image = cv2.resize(image, (new_width, target_size[1]))
        crop_start = (new_width - target_size[0]) // 2
        cropped_image = resized_image[:, crop_start : crop_start + target_size[0]]
    else:
        new_height = int(target_size[1] / aspect_ratio)
        resized_image = cv2.resize(image, (target_size[0], new_height))
        crop_start = (new_height - target_size[1]) // 2
        cropped_image = resized_image[crop_start : crop_start + target_size[1], :]

    return cropped_image


class ClassRequest(BaseModel):
    image: str


class LoginRequest(BaseModel):
    email: str
    password: str
    new: Optional[bool]


app = FastAPI(title="Poultry Birds Disease Classification Backend")


@app.post("/login")
def login(req: LoginRequest):
    email = req.email.lower()
    password = req.password
    new = req.new

    if new:
        if email in users:
            raise HTTPException(
                409,
                detail="User with email already exists.",
            )
        else:
            users[email] = password
            return dict(detail="User created successfully.")
    else:
        if email not in users:
            raise HTTPException(
                409,
                detail="User with email does not exists.",
            )
        elif users[email] != password:
            raise HTTPException(
                401,
                detail="Invalid password.",
            )
        else:
            return dict(detail="User logged in successfully.")


@app.post("/classify")
def classify(req: ClassRequest):
    try:
        resized_image = resize_image_with_aspect_ratio(image_string=req.image)
        resize_image = numpy.expand_dims(resized_image, axis=0)
        ccpred = model.predict(resize_image)
        pred = numpy.argmax(ccpred, axis=1)[0]

        return dict(
            detail="Success",
            disease=class_names[pred],
        )
    except Exception as error:
        raise HTTPException(
            400,
            detail=f"Invalid base64 image string.\n{error}",
        )
