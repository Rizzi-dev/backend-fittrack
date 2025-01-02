from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import firebase_admin
import jwt
from jwt.exceptions import InvalidTokenError
from firebase_admin import credentials, firestore


SECRET_KEY = "7bc1dafe8f68b0d64111c8f4b66e1e8abea715524a9b0c67ec8e1034e1db9f7e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize Firebase
cred = credentials.Certificate(r"C:\Users\gabri\backend-fittrack\keys\trackfit-8e01e-firebase-adminsdk-dnu12-4ecaa272d9.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

# Models
class User(BaseModel):
    id: str
    name: str
    email: str
    password: str
    cpf: str
    sex: str
    user_type: str 
    gym_ids: List[str]  

class Training(BaseModel):
    id: str
    title: str
    description: str
    instructor_id: str
    student_ids: List[str]

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Endpoints
@app.post("/users/")
def create_user(user: User):
    user_ref = db.collection("users").document(user.id)
    if user_ref.get().exists:
        raise HTTPException(status_code=400, detail="User already exists")
    user_ref.set(user.dict())
    return {"message": "User created successfully"}


@app.get("/auth/login/")
def authenticate_User(name: str, password: str):
    user_ref = db.collection("users").where("name", "==", name).where("password", "==", password).limit(1).stream()
    user = user_ref.get()
    if not user.exists:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.name})
    return {"access_token": access_token, "token_type": "bearer"}
    

@app.get("/users/{user_id}")
def get_user(user_id: str):
    user_ref = db.collection("users").document(user_id)
    user = user_ref.get()
    if not user.exists:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()

@app.put("/users/{user_id}")
def update_user(user_id: str, user: User):
    user_ref = db.collection("users").document(user_id)
    if not user_ref.get().exists:
        raise HTTPException(status_code=404, detail="User not found")
    user_ref.update(user.dict())
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    user_ref = db.collection("users").document(user_id)
    if not user_ref.get().exists:
        raise HTTPException(status_code=404, detail="User not found")
    user_ref.delete()
    return {"message": "User deleted successfully"}

@app.post("/trainings/")
def create_training(training: Training):
    training_ref = db.collection("trainings").document(training.id)
    if training_ref.get().exists:
        raise HTTPException(status_code=400, detail="Training already exists")
    training_ref.set(training.dict())
    return {"message": "Training created successfully"}

@app.get("/trainings/{training_id}")
def get_training(training_id: str):
    training_ref = db.collection("trainings").document(training_id)
    training = training_ref.get()
    if not training.exists:
        raise HTTPException(status_code=404, detail="Training not found")
    return training.to_dict()

@app.put("/trainings/{training_id}")
def update_training(training_id: str, training: Training):
    training_ref = db.collection("trainings").document(training_id)
    if not training_ref.get().exists:
        raise HTTPException(status_code=404, detail="Training not found")
    training_ref.update(training.dict())
    return {"message": "Training updated successfully"}

@app.delete("/trainings/{training_id}")
def delete_training(training_id: str):
    training_ref = db.collection("trainings").document(training_id)
    if not training_ref.get().exists:
        raise HTTPException(status_code=404, detail="Training not found")
    training_ref.delete()
    return {"message": "Training deleted successfully"}

@app.get("/gyms/")
def list_gyms():
    gyms_ref = db.collection("gyms")
    gyms = [gym.to_dict() for gym in gyms_ref.stream()]
    return gyms
