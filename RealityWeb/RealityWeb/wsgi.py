"""
WSGI config for RealityWeb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RealityWeb.settings')

sys.path.append('F:/OneDrive - Politechnika Warszawska/PyCharmProjects/analityka/RealityWeb')
sys.path.append('F:/OneDrive - Politechnika Warszawska/PyCharmProjects/analityka/RealityWeb/RealityWeb')

application = get_wsgi_application()