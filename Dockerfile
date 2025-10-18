FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy your application code into the container
COPY ./app /code/app

# Tell Cloud Run how to start your application
# Gunicorn is a professional-grade server for Python web apps
# The PORT environment variable is automatically supplied by Cloud Run
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "app.main:app"]