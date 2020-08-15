"""
WSGI config for RealityDjango project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""
from pathlib import Path

import os
import sys
from django.core.wsgi import get_wsgi_application

root_path = os.path.abspath(os.path.split(__file__)[0])
sys.path.append(os.path.dirname(root_path))
sys.path.append(root_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RealityDjango.settings')

application = get_wsgi_application()
