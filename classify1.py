import warnings

warnings.filterwarnings("ignore")


import cv2, numpy, base64, os
from keras.models import load_model

dirname = os.path.dirname(__file__)


class_names = ["Coccidiosis", "Healthy", "Newcastle Disease", "Salmonella"]
model = load_model(
    os.path.join(
        dirname,
        "model/poultry_disease_classification.keras",
    ),
)


def read_image_from_base64(base64_string: str) -> cv2.typing.MatLike:
    image_bytes = base64.b64decode(base64_string)
    image_array = numpy.frombuffer(image_bytes, numpy.uint8)
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


def classify1(image_string: str) -> str:
    resized_image = resize_image_with_aspect_ratio(image_string=image_string)
    resize_image = numpy.expand_dims(resized_image, axis=0)
    ccpred = model.predict(resize_image)
    pred = numpy.argmax(ccpred, axis=1)[0]

    return class_names[pred]
