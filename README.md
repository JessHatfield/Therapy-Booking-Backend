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
    * Logging provided by Pythons Logging Library (Easy To Extend And Send To Cloud)
    
### Tests
    * API Integration Tests Confirming That Key Functionality Has Been Met

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

3. Get Name Of Container Spawned

```console
docker container list
```

4. Run Our Acceptance Tests To Confirm API Is Running + Functioning Correctly

```console
docker exec -it name-of-your-container bash run_tests.sh
```



### Interacting With The API Via GraphiQL

Flask_Graphql ships with GraphiQL a GUI Which Allows You To Interact With My API In A More Intuitive Fashion

1. Add The ModHeader Extension To Chrome [here](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj?hl=en). This will let you send your access token in the request header whilst using GraphiQL

2. Navigate to http://127.0.0.1/graphql or http://localhost:80/

3. Generate Your Access Token With The Below Query

```
mutation {
  auth(password: "password", username: "test_user") {
    accessToken
    refreshToken
  }
}

```

4. Add The Token To Your Header Within ModHeader (See below for an example Header)

  ```
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNjQ0OTU5NTE4LCJuYmYiOjE2NDQ5NTk1MTgsImp0aSI6IjVlMmQxNWEyLTVkM2QtNGMyYi05ODE1LTQzZDAwMjIxZDdlMSIsImlkZW50aXR5IjoidGVzdF91c2VyIiwiZXhwIjoxNjQ0OTYwMTE4fQ.M93h3IdL0UTA6OuapMSHkfXsCsfB_pL4TP4NbhGDZ4E
  ```
   
5. Query Appointments With Filters With The Below Query

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

6. Create New Appointment With The Below Query

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
7. Refresh Access Token With The Below Query

```
mutation {
  refresh(refreshToken: "your-refresh-token") {
    newToken
  }
}

```

