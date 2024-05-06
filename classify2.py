import base64, tempfile, os
from ultralytics import YOLO

dirname = os.path.dirname(__file__)


def arrayToString(image) -> str:
    t = tempfile.mktemp(".png")
    image.save(t)
    data = open(t, "rb").read()
    os.remove(t)
    base64_image = base64.b64encode(data).decode("utf-8")
    return base64_image


def make_inference_from_image(path_to_img: str) -> str:
    model = YOLO(
        os.path.join(
            dirname,
            "model/best.pt",
        ),
    )
    result = model.predict(
        path_to_img,
        conf=0.5,
    )[0]
    base64_image = arrayToString(result)

    # print(len(base64_image))
    return str(result.names.get(0)), base64_image


def classify2(image_string: str) -> str:
    decoded = base64.b64decode(image_string)
    t = tempfile.mktemp(".png")
    f = open(t, "wb")
    f.write(decoded)
    f.close()

    return make_inference_from_image(t)
