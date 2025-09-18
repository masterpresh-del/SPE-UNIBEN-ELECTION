import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spe_election.settings')

# --- Auto-run migrations on startup ---
import django
django.setup()
from django.core.management import call_command

try:
    call_command('migrate', interactive=False)
    print("✅ Migrations applied successfully.")
except Exception as e:
    print("⚠️ Migration failed:", e)
# --------------------------------------

application = get_wsgi_application()
