# Base Python image
FROM python:3.12.3

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory into the container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Make the wait-for-it.sh script executable
RUN chmod +x /app/wait-for-it.sh

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
