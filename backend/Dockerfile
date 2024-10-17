FROM python:3.11.0
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt

# Copy your application files
COPY . /app


# Set the FLASK_APP environment variable
ENV FLASK_APP=main.py

# Expose the port Flask is running on
EXPOSE 5000

# Command to run Flask
CMD ["flask", "run", "--host=0.0.0.0"]

