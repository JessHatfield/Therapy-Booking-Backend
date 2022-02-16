#Download Python from DockerHub and use it
FROM python:3.9

#Set the working directory in the Docker container
WORKDIR /Spill_Backend_App

#Copy the dependencies file to the working directory
COPY requirements.txt .
COPY .env .

#Install the dependencies
RUN pip install -r requirements.txt

#Copy the Flask app code to the working directory
COPY Spill_Backend_App/ .

RUN export FLASK_APP=Spill_Backend_App/app.py

#Run the container
CMD [ "python", "./app.py" ]


