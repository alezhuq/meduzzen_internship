# How to launch
##1 Setup
run the following command:
#### pip install -r requirements.txt
now, you are ready to launch the server

##2 Starting server
run the following command:
####uvicorn main:app
###Or
####uvicorn main:app --reload

("--reload" parameter is for restarting the server after code changes, 
use it only for development)


#3 Health check
If you see 
{"status":"Working"}
on 
http://127.0.0.1:8000/ , then you've done everything correctly