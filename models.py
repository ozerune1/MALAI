import os
import json
from dotenv import load_dotenv
import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
import boto3

def groq_models():
    load_dotenv()

    headers = {
        "Authorization": f"Bearer {os.getenv("GROQ_API_KEY")}"
    }

    response = requests.get("https://api.groq.com/openai/v1/models", headers=headers).json()

    models = []

    for model in response["data"]:
        models.append(model["id"])
    
    models.sort()

    return models

def ollama_models():
    load_dotenv()

    response = requests.get(f"{os.getenv("OLLAMA_HOST")}/api/tags").json()

    models = []

    for model in response["models"]:
        models.append(model["model"])

    models.sort()

    return models

def gemini_models():
    load_dotenv()

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": os.getenv("GEMINI_API_KEY")
    }

    response = requests.get("https://generativelanguage.googleapis.com/v1beta/models", headers=headers).json()

    models = []

    for model in response["models"]:
        models.append(model["name"][7:])
    
    models.sort()

    return models

vertex_models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-pro", "gemini-1.5-flash"]
vertex_models.sort()

vertex_anthropic_models = []
vertex_anthropic_models.sort()

vertex_llama_models = []
vertex_llama_models.sort()

vertex_mistral_models = []
vertex_mistral_models.sort()

vertex_gemma_models = []
vertex_gemma_models.sort()

def azure_openai_models():
    load_dotenv()

    client = CognitiveServicesManagementClient(
        credential = DefaultAzureCredential(),
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    )

    deployment_names = []

    deployments = client.deployments.list(
        resource_group_name=os.getenv("AZURE_RESOURCE_GROUP_NAME"),
        account_name = os.getenv("AZURE_OPENAI_ACCOUNT_NAME")
    )

    models = []

    for deployment in deployments:
        models.append(deployment.name)

    models.sort()

    return models

def azure_models():
    load_dotenv()

    client = CognitiveServicesManagementClient(
        credential = DefaultAzureCredential(),
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    )

    catalogue = client.accounts.list_models(
        resource_group_name=os.getenv("AZURE_RESOURCE_GROUP_NAME"),
        account_name = os.getenv("AZURE_FOUNDRY_PROJECT_NAME")
    )

    models = []

    for model in catalogue:
        if model.name not in models:
            models.append(model.name)

    models.sort()

    return models

def aws_demand_models():
    load_dotenv()

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")

    bedrock_client = boto3.client("bedrock", region_name=AWS_REGION)
    response = bedrock_client.list_foundation_models()
    model_summaries = response.get("modelSummaries", [])

    models = []

    for model in model_summaries:
        if model.get("inferenceTypesSupported") == ['ON_DEMAND']:
            models.append(model.get("modelId"))
        
    models.sort()

    return models

def aws_inference_models():
    load_dotenv()

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")

    bedrock_client = boto3.client("bedrock", region_name=AWS_REGION)
    response = bedrock_client.list_inference_profiles()
    model_summaries = response.get("inferenceProfileSummaries", [])

    models = []

    for model in model_summaries:
        models.append(model.get("inferenceProfileId"))
        
    models.sort()

    return models

def openai_models():
    load_dotenv()

    api_uri = "https://api.openai.com/v1/models"

    headers = {
        "Authorization": f"Bearer {os.getenv("OPENAI_API_KEY")}"
    }

    response = requests.get(api_uri, headers=headers).json()

    models = []

    for model in response["data"]:
        models.append(model["id"])

    models.sort()

    return models

def anthropic_models():
    load_dotenv()

    api_uri = "https://api.anthropic.com/v1/models"

    headers = {
        "anthropic-version": "2023-06-01",
        "x-api-key": os.getenv("ANTHROPIC_API_KEY")
    }

    response = requests.get(api_uri, headers=headers).json()

    models = []

    for model in response["data"]:
        models.append(model["id"])

    models.sort()

    return models

def mistral_models():
    load_dotenv()

    api_uri = "https://api.mistral.ai/v1/models"

    headers = {
        "Authorization": f"Bearer {os.getenv("MISTRAL_API_KEY")}"
    }

    response = requests.get(api_uri, headers=headers).json()

    models = []

    for model in response["data"]:
        models.append(model["name"])

    models.sort()

    return models