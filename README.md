# DRS Reddit Forum Application

This project implements a forum system where users can create topics, post comments, and vote on comments. The application consists of three main components:

1. **User Interface (UI)**: A Flask web application that serves as the front-end.
2. **Engine**: A Flask API service that handles requests and interacts with the database.
3. **Database (DB)**: Stores essential data for the application.

## Features

- User registration and login
- Profile management
- Create and manage topics
- Comment on topics
- Upvote/downvote comments
- Email notifications for subscribed users (powered by SendGrid)
- Topic search and sorting by number of comments or votes
- Close topics for further commenting

## Technologies Used

- **Backend**: Flask, Python 3.11
- **Frontend**: Angular (not Dockerized)
- **Database**: SQLite (can be changed to other SQL/NoSQL databases)
- **Email Service**: SendGrid
- **Containerization**: Docker, Docker Compose

## Participants

- **Luka Vidaković PR137/2020** - [LukaVidakovic]
- **Nemanja Mijonić PR138/2020** - [nemanjamijonic]
- **Srdjan Bogićević PR139/2020** - [blackhood10]
- **Olivera Čakan PR 71/2020** [oli167]
