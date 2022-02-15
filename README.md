# Spill Backend Appointment API

A GraphQL API for querying and creating therapy appointments. Created for the Spill Backend Tech Test

Written using Flask, Graphene, Flask GraphQL, Graphene-SQLAlchemy, Unittest And SQLite

#### Written by Josh Hatfield


## Key Features

### Retrieve Appointments

* Retrieve Appointments By Date Range
* Retrieve Appointments By Type (one-off or consultation)
* Retrieve Appointments By Specialism (Addiction/ADHD/CBT/Divorce/Sexuality)

* For Each Appointment View
    * The Therapists First & Last Name
    * The Therapists Specialisms
    * The Appointments Start Time & Duration
    * The Appointments Type

### Create New Appointments

* Specify Start Time & Duration
* Specify Appointment Type
* Specify Therapist Associated With Appointment
* Idempotent Creation
    
### User Authentication

* JWT Authentication Passed In Request Header
* Generate An Access + Refresh Token For a Pre-Added User
* Refresh An Expired Access Token
* Prevent Unauthenticated User From Accessing Queries Or Mutations
    
### Monitoring + Observability

* Exception Capture By Sentry
* Python Logging Library
    
### Suite Of Integration Tests
* Integration Tests Confirming That Key API Functionality Has Been Met

## Getting Started

### Fetching + Running My Docker Container

1. Pull my docker container from my docker-hub repository

```console
docker pull joshhatfield1994/fancyorchestra:latest
```

2. Run the docker container

```console
docker run -p 80:80  joshhatfield1994/fancyorchestra:latest
```

3. Get the name of container you have created

```console
docker container list
```

4. Run our acceptance tests to confirm API is running + functioning correctly

```console
docker exec -it name-of-your-container bash run_tests.sh
```



### Interacting With The API Via GraphiQL

Flask_Graphql ships with GraphiQL a GUI Which Allows You To Interact With My API In A More Intuitive Fashion

1. Add the ModHeader extension to Chrome [here](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj?hl=en). This will let you send your access token in the request header whilst using GraphiQL

2. Navigate to http://127.0.0.1/graphql or http://localhost:80/

3. Generate your access token with the below query

```
mutation {
  auth(password: "password", username: "test_user") {
    accessToken
    refreshToken
  }
}

```

4. Add the token to your header within ModHeader (See below for an example Header)

  ```
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNjQ0OTU5NTE4LCJuYmYiOjE2NDQ5NTk1MTgsImp0aSI6IjVlMmQxNWEyLTVkM2QtNGMyYi05ODE1LTQzZDAwMjIxZDdlMSIsImlkZW50aXR5IjoidGVzdF91c2VyIiwiZXhwIjoxNjQ0OTYwMTE4fQ.M93h3IdL0UTA6OuapMSHkfXsCsfB_pL4TP4NbhGDZ4E
  ```
   
5. Query appointments with filters with the below query

```
{
  appointments(filters: {hasSpecialisms: ["ADHD"], type: "one-off", startTimeUnixSecondsRange: {begin: 1644874120, end: 1644894120}}) {
    edges {
      node {
        therapists {
          firstName
          lastName
          specialisms {
            edges {
              node {
                specialismName
              }
            }
          }
        }
        startTimeUnixSeconds
        durationSeconds
        type
      }
    }
  }
}


```

6. Create new appointment with the below query

```
mutation {
  appointment(therapistId: 1, startTimeUnixSeconds: 1644874120, durationSeconds: 3600, type: "one-off") {
    appointment {
      appointmentId
      startTimeUnixSeconds
      durationSeconds
      type
      therapists {
        therapistId
        specialisms {
          edges {
            node {
              specialismName
            }
          }
        }
      }
    }
  }
}

```
7. Refresh access token with the below query

```
mutation {
  refresh(refreshToken: "your-refresh-token") {
    newToken
  }
}

```

###Technical Reasoning

#### Why Flask?
* Flask when deployed via gunicorn and several workers offers similar response times to node.js. As seen [here](https://www.travisluong.com/fastapi-vs-express-js-vs-flask-vs-nest-js-benchmark/)
* Flask is easy to extend and has a wide range of extensions available for common tasks.
* Short term I'm most productive using Flask as I have experience using it
* Where this deployed to production. The flask app would be served using Gunicorn (an actual web server!) allowing us to run instances of the API concurrently per container

### Why GraphQL Over REST?
* I'm most familar with building REST APIs. That said given that Spill use GraphQL this seemed like a good opportunity to learn!
* Using the GraphQL paradigm offers more benefits for spill vs REST where this API put into production
   * It allows for quicker iteration vs REST. Schema is auto-generated from SQLAlchemy Models and added to the Graph in a few lines of code
   * It can be queried using existing frontend code written to interact with GraphQL.
   * Developers don't have to change their mode of thought to work with the API

### Why SQLlite 
* SQLlite is a simple file based database with support for concurrent reads (but not writes). It's not fully featured or suitable for production
* Where this API put into production our SQLlite database would be replaced with a cloud based alternative (for example Cloud SQL for PostgresSQL)
* SQLlite offers a quick way of getting a database running for a small app hence why it was chosen here

### Observability + Monitoring
* I've used the Python Logging Library to log messages. This library allows for extension via config files and easily integrates with cloud logging services
* As a general approach I try to log succesfull events. A human readable message is generated at the info level. Easily parseable JSON messages are logged at the debug level. 
* Sentry Exception monitoring is also installed to allow for easy capture + monitoring of exceptions and to support debugging by capturing stack traces + the contents of API requests. I use it in all my projects as it's super useful and only takes minutes to setup
   
   
### Security

I'll admit this is not my speciality. That said the following decisions where made to enhance it

* Passwords are salted and hashed using Flasks own cryptography library
* Endpoint is protected using JWT auth
* We use SQLAlchemy an ORM which contains built-in logic to santize SQL before querying the database, preventing SQL injections
* Had I more time I would have also implemented Role Based Access Control. This way we could prevent regular users from being able to create appointments
  

###How Might We Handle Scale

Again another rather large subject!

These are my top-level thoughts for how scale could be approached given the limited scope of the API (e.g. retrieve and create appointments)

Spill currently handles 10,000s of users with the potential to grow to 100,000s over time. At the same time user volumes are not evenly distributed across the day

Scaleability + Elasticity are therefore two characteristics of importance

There are two bottlenecks that come to mind which pose issues when scaling

   * Capacity of API to respond to requests
   * Capacity of the Database to serve queries

Handling API Requests Volume

* Our Dockerized API could be deploy via a managed service like Googles Cloud Run
* This would provide a single endpoint for the frontend to query and abstracts away the complexity of distributing loads internally + managing containers. 
* The service is both highly scaleable and elastic (Google will automatically increase or reduce container volumes as traffic loads require)
* Cloud logging + log mesages containing a process id, container id and user ids could be used to stich together user journeys

Handling Database Queries

* Our Database would need be located seperately from these containers. Docker containers within Cloud run are temporary and destroyed after use
* Likely hosted within Googles or AWS cloud using one of their cloud based DBs
* Cloud SQL for PostgresQL might be a good option. It's not as elastic but does scale potentially allowing for up to 96 CPUs and 624gb of RAM per instance.
* Our API is read heavy (we have way more users looking for appointments vs therapists creating them) a master-servant replication strategy could be used to  increase our capacity of handle reads. Writes are made to a master DB which are then synced to several servant DBs which are read from


### Finally - The list of things I'd change about my implementation with more time

* Our appointment mutation is Ideponment but not in the way you would like (e.g. unique ranges in time, one appointment per range). Appointments can be created even if they overlap with each other!
* Cloud based logging using Watchtower and AWS cloudwatch
* Anyone who can authenticate can create new appointments even if they are not therapists! - Needs role based access control
* Flakeyness when running unit tests via pycharm - can lead to db not being deleted before the next test starts and failing unittests
* Every failed auth attempt will trigger an event in sentry. We need a graphql middleware to handle expected exceptions and return them to the user
* Further testing to establish the capacity of the libraries I've used to support pagination and sorting


