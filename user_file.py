# Create a fake users database for the authorization 
fake_users_db = {
    "abhinav": {
        "username": "abhinav",
        "full_name": "Abhinav Gera",
        "email": "abhinav@example.com",
        "hashed_password": "$2b$12$Oy6ykXZrbZ7.CoDBtwdMn.ttiL3wu49ruYQa80H8ElNceMAh7rL/a",
    },
    "abc": {
        "username":"abc",
        "full_name":"abc def",
        "email":"abc@example.com",
        "hashed_password" : "$2b$12$eChdCeZZ7bZfqcvALrayrOUUUNIuIBrkwdwQ8vrvU883a/iz5udJG"
    }
}

# from passlib.context import CryptContext

# def get_password_hash(password):
#     return pwd_context.hash(password)

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# print(get_password_hash("abc123"))