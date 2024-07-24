# Import necessary libraries
from fastapi import FastAPI
import methods
from auth import oauth2_scheme


# Initialize FastAPI
app = FastAPI()

app.include_router(methods.router)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="localhost", port=8000, reload=True)