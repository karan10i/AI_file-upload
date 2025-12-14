import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    # Use SQLite for quick testing instead of PostgreSQL
    from config import settings
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': backend_dir / 'db.sqlite3',
        }
    }
    
    execute_from_command_line(['manage.py', 'runserver', '8000'])