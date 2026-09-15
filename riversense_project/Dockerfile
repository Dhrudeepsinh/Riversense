# Use Python 3.10
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy all project files into the container
COPY . .

# Install Django and Pillow
RUN pip install --no-cache-dir -r requirements.txt

# Hugging Face runs as a non-root user. Give permission for the SQLite database.
RUN chmod -R 777 /app

# Run database migrations (creates the empty database)
RUN python manage.py migrate

# Hugging Face Spaces require web apps to run on port 7860
EXPOSE 7860

# Start the Django server on port 7860
CMD ["python", "manage.py", "runserver", "0.0.0.0:7860"]