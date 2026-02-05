🎬 CinemaPulse

CinemaPulse is a full-stack movie feedback and analytics platform built with Flask and AWS DynamoDB, designed to collect audience reviews, compute real-time ratings, and provide admin-level analytics dashboards.
The application supports both local development (SQLite) and cloud deployment (AWS DynamoDB) through an environment-based database abstraction layer.
🚀 Features
👤 User Management

Email-based login system

Role-based access control:

Viewer: Browse movies and submit feedback

Admin: Access analytics dashboard

Secure session handling using Flask sessions

🎥 Movie Dashboard

Dynamic movie listing fetched from backend APIs

Individual movie detail pages

Poster rendering with fallback support

Real-time average rating updates

Search and filter functionality

⭐ Feedback System

Star-based rating UI (1–5)

Comment submission linked to specific movies

Feedback stored and aggregated in DynamoDB

Automatic recalculation of movie ratings

📊 Analytics Dashboard (Admin Only)

Total movies

Total reviews

Overall average rating

Positive feedback percentage

Movie-wise performance statistics

Auto-refresh analytics (real-time insights)

🛠️ Tech Stack
Frontend

HTML5

CSS3

Vanilla JavaScript

Fetch API for backend communication

Backend

Python

Flask

Flask Blueprints

Flask Sessions

Database

SQLite (Local development)

AWS DynamoDB (Production)

Boto3 SDK

IAM Role–based authentication (no hardcoded keys)

Cloud & Deployment

AWS EC2

AWS DynamoDB

📁 Project Structure

Environment-based configurationCinemaPulse/
│
├── app.py
├── aws_app.py
├── config.py
├── requirements.txt
│
├── database/
│   ├── sqlite_db.py
│   └── dynamodb_db.py
│
├── services/
│   └── db_service.py
│
├── routes/
│   ├── auth_routes.py
│   ├── movie_routes.py
│   ├── feedback_routes.py
│   └── analytics_routes.py
│
├── static/
│   ├── css/
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── default-poster.jpg
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── movie.html
│   ├── feedback.html
│   └── analytics.html
│
└── README.md

⚙️ Environment Configuration
The application automatically switches databases based on environment:

ENV_MODE=local   # SQLite
ENV_MODE=aws     # DynamoDB

Local Mode

Uses SQLite

Ideal for development and testing

AWS Mode

Uses DynamoDB

IAM role authentication

Scalable and production-ready

🗄️ DynamoDB Schema
Movies Table
Attribute	Type
movie_id (PK)	Number
title	String
description	String
poster_url	String
avg_rating	Number
total_reviews	Number
created_at	String
Feedback Table
Attribute	Type
movie_id (PK)	Number
timestamp (SK)	String
user_email	String
rating	Number
comment	String
sentiment	String
Users Table
Attribute	Type
user_email (PK)	String
role	String
created_at	String
▶️ Running the Project
Local Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

AWS Deployment
export ENV_MODE=aws
python aws_app.py


Ensure your EC2 instance has an IAM role with:

AmazonDynamoDBFullAccess

🔐 Security Considerations

No AWS credentials stored in code

IAM roles used for DynamoDB access

Session-based authentication

Admin routes protected via role checks

📌 Key Highlights (Resume-Ready)

Designed a cloud-ready Flask application with dual database support

Implemented real-time analytics using DynamoDB aggregation

Built role-based access control for secure admin insights

Integrated AWS DynamoDB using IAM roles

Followed clean architecture with service abstraction layers

📈 Future Enhancements

Chart-based analytics (Chart.js)

Sentiment analysis using NLP

Pagination and lazy loading

CI/CD pipeline with GitHub Actions

Dockerized deployment

👩‍💻 Author

Sukriti Chadha
AI/ML & Full-Stack Enthusiast
