from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import json

AZURE_CONTAINER = settings.AZURE_CONTAINER
AZURE_RESOURCE_GROUP = settings.AZURE_RESOURCE_GROUP
AZURE_LOCATION = settings.AZURE_LOCATION
AZURE_ACCOUNT_NAME = settings.AZURE_ACCOUNT_NAME
AZURE_CONTAINER = settings.AZURE_CONTAINER

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--setup-storage", action="store_true", default=False)

    def handle(self, *args, **options):
        setup_storage = options.get("setup_storage")
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


            
        