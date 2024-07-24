#Base Image - Parent IMage
FROM python:3.12.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container 
COPY . .

# Install packages frm the requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# USING CMD COMMAND TO EXECUTE
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


#DOCKER COMMANDS:
    # 1. docker build . -t fastapi:1.0 --no-cache
    # 2. docker run --name mysql_2 -e MYSQL_ROOT_PASSWORD=user1  --network aligne -p 4001:3306 mysql:latest 
    # 3. docker run --network aligne -e USER=root -e PASSWORD=user1 -e HOST=mysql_2 -e PORT=3306 -e SECRET_KEY="$2b$12$Bnrngawzi0OWhLaBhLZJdubaKN.wSmIm5rAvxCF5DT9dgiRl0K3rC" -e ALGORITHM=HS256 -e ACCESS_TOKEN_EXPIRE_MINUTES=30 -p 8001:8000 fastapi:1.0
