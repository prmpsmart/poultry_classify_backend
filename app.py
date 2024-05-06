from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from classify1 import classify1, os
from classify2 import classify2

dirname = os.path.dirname(__file__)
db = os.path.join(dirname, "db")

if not os.path.isfile(db):
    f = open(db, "w")
    f.write("{}")
    f.close()

users = json.load(open(db))


def save():
    json.dump(users, open(db, "w"))


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
            save()
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


@app.post("/classify1")
def classify(req: ClassRequest):
    try:
        return dict(
            detail="Success",
            disease=classify1(req.image),
        )
    except Exception as error:
        raise HTTPException(
            400,
            detail=f"Invalid base64 image string.\n{error}",
        )


@app.post("/classify2")
def classify(req: ClassRequest):
    try:
        return dict(
            detail="Success",
            disease_image=classify2(req.image),
        )
    except Exception as error:
        raise HTTPException(
            400,
            detail=f"Invalid base64 image string.\n{error}",
        )
