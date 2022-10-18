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
### backend/app/db/tasks.py :
file describing db tasks(e. g. connecting to db), with enabled logger
### backend/app/db/schemas :
folder for pydantic schemas
### backend/app/db/migrations :
folder, created for running migrations with alembic
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

# 3 Running migrations:
## 3.1 migrations
firstly, you need to start the docker containers

to run migrations you need to get ID of the server's (not db's) container
#### docker ps
then grab the server's id and execute next command
#### docker exec -it "server id here" bash
inside the bash shell, run this command
#### alembic upgrade head
## 3.2 check
to make sure that everything has been done correctly, execute this command
#### docker-compose exec db psql -h localhost -U postgres --dbname=postgres
and to get created table, type in this:
#### \d "Users"
If you see 
Table " public.Users"
then migrations have been applied successfully
# 4 Health check
If you see
{"status":"Working"}
on 
http://127.0.0.1:8000/ , then you've done everything correctly

## 4.1 Endpoints

####post, "/"  - create new user
#### get, "/user/all" - get all users (with pagination)
#### get, "/user/{user_id}" - get user by id
#### put, "user/{user_id}/edit_password" - edit user's password
#### delete, "/user/{user_id}/delete" delete user with this id
