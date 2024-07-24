from pydantic import BaseModel, EmailStr
from enum import Enum

# It represents a token returned to the client
class Token(BaseModel):
    access_token: str
    token_type: str


# Represents the data encoded in a token
class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


# Represents a user's data received with data validation(pydantic)
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None


# Represents a user's hashed_password stored in the database(inherits User-class)
class UserInDB(User):
    hashed_password: str


# Create BankAccount class for details with using the BaseModel for data-validation
class BankAccount(BaseModel):
    name_customer : str  
    account_id: int
    balance: float
    pin: str

# Create amt class for increment and decrement in balance 
class amt(BaseModel):
    account_id : int
    amount : float 

# Create Role enum class for checking the role 
class Role(str, Enum):
    user = "user"
    admin = "admin"

# Create UserCreate class for details with using the BaseModel for data-validation
class UserCreate(BaseModel):
    username: EmailStr
    role: Role = Role.user
    password: str