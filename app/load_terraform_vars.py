import boto3
import json
import random
import string


# Create a session using the specific profile
session = boto3.Session(profile_name='madhu_prakash_1')

# Initialize the AWS Secrets Manager client
client = session.client('secretsmanager', region_name='us-east-1')  # Change the region as needed

# Define the secret name
secret_name = "my_terraform_variables"

# Generate random Terraform variables
def generate_random_terraform_vars(num_vars=5):
    terraform_vars = {}
    for _ in range(num_vars):
        key = 'var_' + ''.join(random.choices(string.ascii_lowercase, k=8))
        value = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        terraform_vars[key] = value
    return terraform_vars

# Store variables in AWS Secrets Manager
def store_terraform_vars_in_secrets_manager(secret_name, terraform_vars):
    try:
        # Check if the secret already exists
        client.get_secret_value(SecretId=secret_name)
        # If it exists, update the secret
        client.put_secret_value(
            SecretId=secret_name,
            SecretString=json.dumps(terraform_vars)
        )
        print(f"Updated secret: {secret_name}")
    except client.exceptions.ResourceNotFoundException:
        # If it does not exist, create the secret
        client.create_secret(
            Name=secret_name,
            SecretString=json.dumps(terraform_vars)
        )
        print(f"Created secret: {secret_name}")

if __name__ == "__main__":
    terraform_vars = generate_random_terraform_vars()
    store_terraform_vars_in_secrets_manager(secret_name, terraform_vars)
    print(f"Stored the following variables in {secret_name}:")
    print(json.dumps(terraform_vars, indent=4))
