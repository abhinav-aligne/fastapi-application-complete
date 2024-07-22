from fastapi import APIRouter, status, Depends, HTTPException
from database_connect import SQL, connectivity, table_banking, user_banking
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from model import BankAccount, amt, Token, UserCreate
from auth import create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from user_file import fake_users_db
from datetime import timedelta

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
@router.post("/token", deprecated=False, description="Giving the access after the login", tags=["AUTHENTICATOIN"])
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

# Endpoint to create a bank account
@router.post("/create_account", status_code= status.HTTP_201_CREATED, tags=["ACCOUNT-ACCESSIBILITY"])
async def create_account(account:BankAccount, form_data: Annotated[str, Depends(oauth2_scheme)]):
    try:
        query = "INSERT INTO accounts (name_customer, account_id, balance, pin) VALUES (%s, %s, %s, %s)"
        values = (account.name_customer, account.account_id, account.balance, account.pin)
        mycursor.execute(query, values)
        mydb.commit()
        return {"Successfully Created"}
    except SQL.Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")
   

# Endpoint to deposit money into a bank account
@router.put("/deposit/{id}/{amount}",status_code=status.HTTP_204_NO_CONTENT, tags=["ACCOUNT-ACCESSIBILITY"])
async def deposit(id:int, amount:int, form_data: Annotated[str, Depends(oauth2_scheme)]):
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
            return {"Successfully deposited"}
        else:
            raise HTTPException(status_code=404, detail= "Account not Found in the database list")
    except SQL.Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")
    

# Endpoint to withdraw money into a bank account
@router.put("/withdraw", status_code=status.HTTP_204_NO_CONTENT, tags=["ACCOUNT-ACCESSIBILITY"])
async def withdraw(w: amt, form_data: Annotated[str, Depends(oauth2_scheme)]):
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
@router.get("/get_balance", status_code= status.HTTP_200_OK, tags=["ACCOUNT-ACCESSIBILITY"])
async def get_balance(account_id: int, form_data:  Annotated[str, Depends(oauth2_scheme)]):
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
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, tags=["ACCOUNT-ACCESSIBILITY"])
async def delete(account_id:int, form_data:  Annotated[str, Depends(oauth2_scheme)]):
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
        mycursor.execute("USE banking")
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        #hashed password - user.password table
        hashed_password = get_password_hash(user.password)
        user.password = hashed_password
        values = (user.username, user.password)
        mycursor.execute(query, values)
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