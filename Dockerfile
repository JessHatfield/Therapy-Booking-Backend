#Download Python from DockerHub and use it
FROM python:3.9

#Set the working directory in the Docker container
WORKDIR /Spill_Backend_App

#Copy the dependencies file to the working directory
COPY requirements.txt .

#Install the dependencies
RUN pip install -r requirements.txt

#Copy the Flask app code to the working directory
COPY Spill_Backend_App/ .


RUN export FLASK_APP=Spill_Backend_App/app.py
##Setup SQLlite Data
#RUN flask db init
#RUN flask db migrate -m "Creating Database"
#RUN flask db upgrade



#Run the container
CMD python -m mock_data_generation.py
CMD [ "python", "./app.py" ]
#CMD ls
#CMD python -m unittest tests/route_integration_tests.py

