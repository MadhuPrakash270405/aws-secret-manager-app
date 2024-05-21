import time
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import boto3
from botocore.exceptions import ClientError
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Create a session using the specific profile
session = boto3.Session(profile_name='madhu_prakash_1')

# Initialize the AWS Secrets Manager client
client = session.client('secretsmanager', region_name='us-east-1')  # Change the region as needed

def list_secrets():
    try:
        paginator = client.get_paginator('list_secrets')
        response_iterator = paginator.paginate()
        secrets = []
        for response in response_iterator:
            for secret in response['SecretList']:
                secrets.append(secret['Name'])
        return secrets
    except client.exceptions.ClientError as e:
        print(f"Error: {e}")
        return []

def get_secret(secret_name):
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret
    except client.exceptions.ResourceNotFoundException:
        return {}
    except client.exceptions.ClientError as e:
        print(f"Error: {e}")
        return {}

def create_secret(new_secret_name):
    try:
        client.create_secret(Name=new_secret_name)
        return True
    except client.exceptions.ClientError as e:
        print(f"Error: {e}")
        return False

def delete_secret(secret_name):
    try:
        client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
        return True
    except client.exceptions.ClientError as e:
        print(f"Error: {e}")
        return False


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    secrets = list_secrets()
    selected_secret = secrets[0] if secrets else None
    secret = get_secret(selected_secret) if selected_secret else {}
    return templates.TemplateResponse("index.html", {"request": request, "secrets": secrets, "secret": secret, "selected_secret": selected_secret})

@app.post("/", response_class=HTMLResponse)
async def select_secret(request: Request, secret_name: str = Form(...)):
    secrets = list_secrets()
    secret = get_secret(secret_name)
    return templates.TemplateResponse("index.html", {"request": request, "secrets": secrets, "secret": secret, "selected_secret": secret_name})

@app.post("/create_secret", response_class=RedirectResponse)
async def create_secret_name(request: Request, new_secret_name: str = Form(...)):
    if create_secret(new_secret_name):
        time.sleep(3)
        return RedirectResponse("/", status_code=303)
    else:
        error_message = "Failed to create the new secret. Please try again."
        secrets = list_secrets()
        return templates.TemplateResponse("index.html", {"request": request, "secrets": secrets, "error_message": error_message, "selected_secret": None})

@app.post("/delete_secret", response_class=RedirectResponse)
async def delete_secret_name(request: Request, secret_name: str = Form(...)):
    if delete_secret(secret_name):
        time.sleep(3)
        return RedirectResponse("/", status_code=303)
    else:
        error_message = "Failed to delete the secret. Please try again."
        secrets = list_secrets()
        return templates.TemplateResponse("index.html", {"request": request, "secrets": secrets, "error_message": error_message, "selected_secret": None})

@app.post("/update", response_class=RedirectResponse)
async def update_variable(request: Request, secret_name: str = Form(...), key: str = Form(...), value: str = Form(...)):
    secret = get_secret(secret_name)
    secret[key] = value
    client.put_secret_value(SecretId=secret_name, SecretString=json.dumps(secret))
    return RedirectResponse(f"/?secret_name={secret_name}", status_code=303)

@app.post("/add", response_class=RedirectResponse)
async def add_variable(request: Request, secret_name: str = Form(...), new_key: str = Form(...), new_value: str = Form(...)):
    secret = get_secret(secret_name)
    secret[new_key] = new_value
    client.put_secret_value(SecretId=secret_name, SecretString=json.dumps(secret))
    return RedirectResponse(f"/?secret_name={secret_name}", status_code=303)