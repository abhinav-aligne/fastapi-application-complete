import os
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from user_file import fake_users_db
from model import TokenData, UserInDB


# Load the secret key for encoding/decoding the tokens from environment variables
security_key = os.getenv("SECRET_KEY")

# Load the algorithm used for encoding the tokens from environment variables
algorithm = os.getenv("ALGORITHM")

# the expiration time (in minutes) for accessing the tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30 


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer authentication scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Function to verify a plaintext password against a hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Function to hashed_password a plaintext password
def get_password_hash(password):
    return pwd_context.hash(password)


# Function to retrieve a user from a database (or fake database (user_file.py) in this case)
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


# Function to authenticate a user based on username and password
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# Function to create an access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, security_key, algorithm=algorithm)
    return encoded_jwt


# Function to get the current user based on the provided token
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user