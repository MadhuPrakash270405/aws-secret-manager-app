python3 -m venv env

source env/bin/activate

pip install fastapi uvicorn boto3 jinja2 python-multipart

To start the APP(Local): uvicorn main:app --reload

To start the app in server: uvicorn main:app --host 0.0.0.0 --port 8000

FOR SWAGGER UI: http://localhost:8000/docs#/
