from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import json

AZURE_CONTAINER = settings.AZURE_CONTAINER
AZURE_RESOURCE_GROUP = settings.AZURE_RESOURCE_GROUP
AZURE_LOCATION = settings.AZURE_LOCATION
AZURE_ACCOUNT_NAME = settings.AZURE_ACCOUNT_NAME
AZURE_CONTAINER = settings.AZURE_CONTAINER
AZURE_OPENAI_NAME = settings.AZURE_OPENAI_NAME
OPENAI_API_VERSION = settings.OPENAI_API_VERSION
OPENAI_MODEL = settings.OPENAI_MODEL
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME = settings.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME
OPENAI_MODEL_VERSION = settings.OPENAI_MODEL_VERSION

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--setup-storage", action="store_true", default=False)
        parser.add_argument("--setup-openai", action="store_true", default=False)

    def handle(self, *args, **options):
        setup_storage = options.get("setup_storage")
        setup_openai = options.get("setup_openai")
        # create resource group
        cmd = ["az", "group", "exists", "--name", AZURE_RESOURCE_GROUP ]
        resource_group_exists = subprocess.run(cmd, capture_output=True).stdout.decode().strip()
        if resource_group_exists == "false":
            cmd = [
                "az", "group", "create",
                "--location", AZURE_LOCATION,
                "--name", AZURE_RESOURCE_GROUP,
            ]
            subprocess.run(cmd, check=True)
            print(f"Resource group '{AZURE_RESOURCE_GROUP}' created in location '{AZURE_LOCATION}'.")
        else:
            print(f"Resource group '{AZURE_RESOURCE_GROUP}' already exists.")

        # setup storage
        if setup_storage:
            cmd = ["az", "storage", "account", "check-name", "--name", AZURE_ACCOUNT_NAME]
            storage_account_available = subprocess.run(cmd, capture_output=True).stdout.decode().strip()
            storage_account_available = json.loads(storage_account_available)["nameAvailable"]
            if storage_account_available:
                cmd = [
                    "az", "storage", "account", "create",
                    "--name", AZURE_ACCOUNT_NAME,
                    "--resource-group", AZURE_RESOURCE_GROUP,
                    "--location", AZURE_LOCATION,
                    "--sku", "Standard_LRS",
                ]
                subprocess.run(cmd, check=True)
                print(f"Storage account '{AZURE_ACCOUNT_NAME}' created in resource group '{AZURE_RESOURCE_GROUP}'.")
            else:
                print(f"Storage account '{AZURE_ACCOUNT_NAME}' already exists.")

            # create container
            cmd = [
                "az", "storage", "container", "create",
                "--name", AZURE_CONTAINER,
                "--account-name", AZURE_ACCOUNT_NAME,
            ]
            response = subprocess.run(cmd, capture_output=True, check=True)
            created = json.loads(response.stdout.decode())["created"]
            if created:
                print(f"Container '{AZURE_CONTAINER}' created in storage account '{AZURE_ACCOUNT_NAME}'.")
            else:
                print(f"Container '{AZURE_CONTAINER}' already exists in storage account '{AZURE_ACCOUNT_NAME}'.")

        # Azure OpenAI setup and retrieve API key and endpoint
        if setup_openai:
            cmd = [
                "az", "cognitiveservices", "account", "create",
                "--name", AZURE_OPENAI_NAME,
                "--resource-group", AZURE_RESOURCE_GROUP,
                "--location", AZURE_LOCATION,
                "--kind", "OpenAI",
                "--sku", "s0",
            ]
            response = subprocess.run(cmd, check=True, capture_output=True)
            print(f"Azure OpenAI service '{AZURE_OPENAI_NAME}' created in resource group '{AZURE_RESOURCE_GROUP}'.")
            api_endpoint = json.loads(response.stdout.decode())["properties"]["endpoint"]
            cmd = [
                "az", "cognitiveservices", "account", "keys", "list",
                "--name", AZURE_OPENAI_NAME,
                "--resource-group", AZURE_RESOURCE_GROUP,
            ]
            response = subprocess.run(cmd, check=True, capture_output=True)
            keys = json.loads(response.stdout.decode())

            # deploay the OpenAI model
            cmd = [
                "az", "cognitiveservices", "account", "deployment", "create",
                "--name", AZURE_OPENAI_NAME,
                "--resource-group", AZURE_RESOURCE_GROUP,  
                "--deployment-name", AZURE_OPENAI_MODEL_DEPLOYMENT_NAME, 
                "--model-name", OPENAI_MODEL,
                "--model-version",  OPENAI_MODEL_VERSION, 
                "--model-format", "OpenAI",
                "--sku-capacity", "1", 
                "--sku-name", "GlobalStandard",
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, check=True)
            print(f"OpenAI model '{OPENAI_MODEL}' deployed with deployment name '{AZURE_OPENAI_MODEL_DEPLOYMENT_NAME}'.")

            # Print the API key and endpoint
            print("-" * 40)
            print("Please note that the API key is sensitive information and should be kept secure.")
            print(f"Azure OpenAI API Key: {keys['key1']}")
            print(f"Azure OpenAI Endpoint: {api_endpoint}")
