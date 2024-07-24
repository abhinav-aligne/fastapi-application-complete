import os
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from model import TokenData, UserCreate, Role
from user_database import user_database_connect
from database_connect import connectivity
from pydantic import ValidationError

mydb, mycursor = connectivity()
user_db = user_database_connect()

# Load the secret key for encoding/decoding the tokens from environment variables
security_key = os.getenv("SECRET_KEY")

# Load the algorithm used for encoding the tokens from environment variables
algorithm = os.getenv("ALGORITHM")

# the expiration time (in minutes) for accessing the tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30 


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer authentication scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"admin": "All Access.", "user": "Limited Access."})

# Function to verify a plaintext password against a hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Function to hashed_password a plaintext password
def get_password_hash(password):
    return pwd_context.hash(password)


# Function to retrieve a user from a database (or fake database (user_file.py) in this case)
def get_user(username: str):
    mycursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user_db = mycursor.fetchone()
    if user_db:
        user_data = {
            'username': user_db[0],  
            'role': user_db[1],
            'password': user_db[2]
        }
        return UserCreate(**user_data)

# Function to authenticate a user based on username and password
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# Function to create an access token
def create_access_token(data:dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, security_key, algorithm=algorithm)
    return encoded_jwt


# Function to get the current user based on the provided token
async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value})

    try:
        payload = jwt.decode(token, security_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes")
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value})
    return user


# DEFINING THE SCOPE FOR THE ADMIN permissions
def get_admin_scope(
    current_user: Annotated[UserCreate, Security(get_current_user, scopes=["admin"])]):
    if current_user.role != Role.admin:
        raise HTTPException(status_code=400, detail="No role to access")
    return current_user

# DEFINING THE SCOPE FOR THE USER permissions
def get_user_scope(
    current_user: Annotated[UserCreate, Security(get_current_user, scopes=["user"])]):
    if current_user.role != Role.user:
        raise HTTPException(status_code=400, detail="No role to access")
    return current_user