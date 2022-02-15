#Download Python from DockerHub and use it
FROM python:3.9

#Set the working directory in the Docker container
WORKDIR /SpillBackend

#Copy the dependencies file to the working directory
COPY requirements.txt .

#Install the dependencies
RUN pip install -r requirements.txt

#Copy the Flask app code to the working directory
COPY src/ .

#Run the container
CMD [ "python", "./app.py" ]