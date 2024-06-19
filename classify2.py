import base64, tempfile, os
from ultralytics import YOLO

dirname = os.path.dirname(__file__)
model = YOLO(
    os.path.join(
        dirname,
        "model/best.pt",
    )
)


def arrayToString(image) -> str:
    t = tempfile.mktemp(".png")
    image.save(t)
    data = open(t, "rb").read()
    os.remove(t)
    base64_image = base64.b64encode(data).decode("utf-8")
    return base64_image


class_names = {
    0: "Coccidiosis",
    1: "Healthy",
    2: "Newcastle Disease",
    3: "Salmonella",
}


def make_inference_from_image(path_to_img: str) -> str:
    results = model.predict(
        path_to_img,
        conf=0.5,
    )
    result = results[0]

    classes = [int(i) for i in result.boxes.cls.numpy()]
    classes = list(map(class_names.get, classes))

    base64_image = arrayToString(result)

    return classes[0], base64_image


def classify2(image_string: str) -> str:
    decoded = base64.b64decode(image_string)
    t = tempfile.mktemp(".png")
    f = open(t, "wb")
    f.write(decoded)
    f.close()

    return make_inference_from_image(t)
