# Setup
1. Fill out sample_dot_env and rename to .env
2. In home/settings.py
    1. Add ADMINS
    2. For production: add you domain to `ALLOWED_HOSTS` (e.g. 'www.domain.io')
    3. Add your Railway and/our your production domain to `CSRF_TRUSTED_ORIGINS` (e.g. 'https://www.domain.io')
3. Create and activate venv: `python3 -m venv venv`, `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Inside the src directory
    1. Run migrations: `python manage.py makemigrations`, `python manage.py migrate`
    2. Pull and collect static files: `python manage.py vendor_pull`, `python manage.py collectstatic`
    3. Run server: `python manage.py runserver`
6. To run the GitHub Actions, add these to the Repository secrets: `DJANGO_DEBUG`, `NEON_API_KEY`, `NEON_DATABASE_URL`, `NEON_PROJECT_ID`, `STRIPE_SECRET_KEY`
7. In Railway
    1. Click on + New to add a new project
    2. In the project click + Create to create a new service
    3. Choose the desired Github repo and branch
    4. After the service is deployed, add the environment variables under Variables
    5. In the settings, go to networking and generate a new domain with port = 8080
8. Azure
    1. Create Azure account & subscription
    2. Install the Azure CLI
    3. Run `az login` to athenticate
    4. Select a location and add it to the env variable `AZURE_LOCATION` and define a resource group name `AZURE_RESOURCE_GROUP`


# Known issues
## Mac
1. When python can't find weasyprint, run this before running the server: `export DYLD_LIBRARY_PATH="/opt/homebrew/lib"`