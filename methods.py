from fastapi import APIRouter, status, Depends, HTTPException, Security
from database_connect import SQL, connectivity,table_banking, user_banking
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from model import BankAccount, amt, Token, UserCreate, User
from auth import create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from datetime import timedelta
from auth import get_admin_scope, get_user_scope


# Initializing the database variables
mydb, mycursor = connectivity()
table_banking()
user_banking()


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer authentication scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initializing the router  
router = APIRouter()


# To generate access token after successful login at the endpoint
@router.post("/token", description="Giving the access after the login", tags=["AUTHENTICATION"], response_model= Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes":  [user.role]},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")

# Endpoint to create a bank account
@router.post("/create_account", status_code= status.HTTP_201_CREATED, description="ADMIN ACCESS", tags=["ACCOUNT-ACCESSIBILITY"])
async def create_account(account:BankAccount,
                         current_user: Annotated[UserCreate, Security(get_admin_scope, scopes=["admin"])]):
    try:
        query = "INSERT INTO accounts (name_customer, account_id, balance, pin) VALUES (%s, %s, %s, %s)"
        values = (account.name_customer, account.account_id, account.balance, account.pin)
        mycursor.execute(query, values)
        mydb.commit()
        return {"Successfully Created"}
    except SQL.Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")
   

# Endpoint to deposit money into a bank account 
@router.put("/deposit/{id}/{amount}", status_code=status.HTTP_200_OK, description="USER ACCESS", tags=["ACCOUNT-ACCESSIBILITY"])
async def deposit(id: int, amount: int,
                  current_user: UserCreate = Security(get_user_scope, scopes=["user"])):
    try:
        checking_query = "SELECT * FROM accounts WHERE account_id = %s"
        value_query = (id,)
        mycursor.execute(checking_query, value_query)
        checked_id = mycursor.fetchone()
        if checked_id:
            query = "UPDATE accounts SET balance = balance + %s WHERE account_id = %s"
            values = (amount, id)
            mycursor.execute(query, values)
            mydb.commit()
            return {"message": "Successfully deposited"}
        else:
            raise HTTPException(status_code=404, detail="Account not found in the database")
    except SQL.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    

# Endpoint to withdraw money into a bank account
@router.put("/withdraw", status_code=status.HTTP_204_NO_CONTENT, description="USER ACCESS", tags=["ACCOUNT-ACCESSIBILITY"])
async def withdraw(w: amt,
                  current_user: UserCreate = Security(get_user_scope, scopes=["user"])):
    try:
        checking_query = "SELECT * FROM accounts WHERE account_id = %s"
        value_query = (w.account_id,)
        mycursor.execute(checking_query, value_query)
        checked_id = mycursor.fetchone()
        if checked_id:
            query = "UPDATE accounts SET balance = balance - %s WHERE account_id = %s"
            values = (w.amount, w.account_id)
            mycursor.execute(query, values)
            mydb.commit()
            return {"Withdrawal successful"}
        else:
            raise HTTPException(status_code=404, detail="Account not found in the database")
    except SQL as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    

# Endpoint to get the balance of a bank account
@router.get("/get_balance", status_code= status.HTTP_200_OK, description="ADMIN ACCESS", tags=["ACCOUNT-ACCESSIBILITY"])
async def get_balance(account_id: int, 
                  current_user: UserCreate = Security(get_admin_scope, scopes=["admin"])):
    try:
        query = "SELECT balance FROM accounts WHERE account_id = %s"
        values = (account_id,)
        mycursor.execute(query, values)
        result = mycursor.fetchone()
        if result:
            return {"balance": result[0]}
        else:
            return HTTPException(status_code=404, detail = "ERROR ACCOUNT NOT FOUND")
    except SQL.Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")
    

# Endpoint to delete a bank account
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, description="ADMIN ACCESS",tags=["ACCOUNT-ACCESSIBILITY"])
async def delete(account_id:int, 
                  current_user: UserCreate = Security(get_admin_scope, scopes=["admin"])):
    try:
        query = "DELETE FROM accounts WHERE account_id = %s"
        values = (account_id,)
        mycursor.execute(query, values)
        mydb.commit()
        return {"message": "Delete successful"}
    except SQL.Error as err:
        raise HTTPException(status_code= 500, detail = f"Error: {err}")

# Endpoint for creation of a new user
@router.post("/users", status_code=status.HTTP_201_CREATED, tags=["USER-CREDENTIALS"])
def create_user(user:UserCreate):
    try:
        hashed_password = get_password_hash(user.password)
        mycursor.execute("INSERT INTO users (username, role, password) VALUES (%s, %s, %s)", (user.username, user.role, hashed_password))
        mydb.commit()
        return {"Successfully Created"}
    except SQL.Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")
    
# Endpoint to fetch the user username
@router.get("/users/{username}", status_code= status.HTTP_200_OK, tags=["USER-CREDENTIALS"])
def get_user(username: str):
        mycursor.execute("USE banking")
        checking_query = "SELECT * FROM users WHERE username = %s"
        value_query = (username,)
        mycursor.execute(checking_query, value_query)
        user = mycursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="ERROR USER NOT FOUND")
        return user