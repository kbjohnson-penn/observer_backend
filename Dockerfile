# Use the official Python image from the Docker Hub
FROM python:3.10.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Copy wait-for-it script
COPY wait-for-it.sh .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the migrations and start the application
CMD ["./wait-for-it.sh", "mariadb:3306", "--", "sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
