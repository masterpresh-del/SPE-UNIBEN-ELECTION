import os
import sys
import logging

from django.core.wsgi import get_wsgi_application

# --- Settings ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spe_election.settings')

# --- Setup Django ---
import django
django.setup()

# --- Logger for startup issues ---
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# --- Run migrations safely ---
from django.core.management import call_command

try:
    call_command('migrate', interactive=False)
    logger.info("✅ Database migrations applied successfully.")
except Exception as e:
    logger.error("⚠️ Migration failed: %s", e)

# --- Serve static files using WhiteNoise ---
try:
    from whitenoise import WhiteNoise
    application = get_wsgi_application()
    application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), '../staticfiles'))
    logger.info("✅ WhiteNoise static files enabled.")
except Exception as e:
    logger.error("⚠️ WhiteNoise failed: %s", e)
    application = get_wsgi_application()  # fallback

logger.info("🚀 WSGI application ready.")
