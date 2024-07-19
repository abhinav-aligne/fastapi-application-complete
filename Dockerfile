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
CMD ["uvicorn", "banking:app", "--host", "0.0.0.0", "--port", "8000"]
