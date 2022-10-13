# Project structure

## Redis : redis folder
## backend : main folder
### backend/app :
folder for code
### backend/app/api/server.py :
main file that sets up and launches the server
### backend/app/api/routes :
package that contains the routes
### backend/app/core/config.py :
file that loads configs
### backend/app/core/tasks.py :
file that contains core tasks (i. e. actions on starting and shutting down the app)
### backend/app/databases/tasks.py
file describing db tasks(e. g. connecting to db), with enabled logger

### backend/test :
folder for tests



# How to launch
## 1 Setup
run the following command:
#### pip install -r requirements.txt
now, you are ready to launch the server

## 2 Starting server
### 2.1 without docker
run the following command:
#### uvicorn main:app
### Or
#### uvicorn main:app --reload

("--reload" parameter is for restarting the server after code changes, 
use it only for development)

### 2.2 with Docker

run
#### docker build -t python-fastapi . 
followed by
#### docker run -p 8000:8000 python-fastapi

### 2.3 with Docker-compose
run
#### docker-compose up -d --build 
followed by
#### docker-compose up 


# 3 Health check
If you see 
{"status":"Working"}
on 
http://127.0.0.1:8000/ , then you've done everything correctly


