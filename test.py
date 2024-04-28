import requests, base64


url = "http://localhost:8000"
url = "https://holy-tightly-snail.ngrok-free.app"


def post(path: str, json: dict):
    return requests.post(
        f"{url}/{path}",
        json=json,
        headers={
            "ngrok-skip-browser-warning": "1",
            "User-Agent": "prmpsmart/1.0",
        },
    )


def login(new: bool = False):
    res = post(
        "login",
        json=dict(email="prmpsmart@gmail.com", password="prmp", new=new),
    )
    print(res.json())


def classify(file: str):
    image = base64.b64encode(open(file, "rb").read()).decode()
    res = post(
        "classify",
        json=dict(image=image),
    )
    print(res.json())


login(True)
login()

file = r"C:\Users\USER\Desktop\Workspace\PoultryClass\poultry_disease_classification\images\cocci.png"
file = r"C:\Users\USER\Desktop\Workspace\PoultryClass\poultry_disease_classification\images\cocci.0.jpg"

classify(file)


# git filter-repo --path-glob '!model/poultry_disease_classification.keras'
# git filter-branch --tree-filter 'rm -f model/poultry_disease_classification.keras' HEAD
