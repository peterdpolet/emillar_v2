# backend/inventory/print_views.py
"""
Django view that proxies a label-print request to the local print service.
The print service (print_service.py) runs on the host machine outside Docker,
reachable at host.docker.internal:5100 from inside a container, or
localhost:5100 when called from the host directly.
"""
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Item

PRINT_SERVICE_URL = getattr(settings, 'PRINT_SERVICE_URL', 'http://localhost:5100/print')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def print_label(request):
    item_id   = request.data.get('item_id')
    so_number = request.data.get('so_number')

    if not item_id or not so_number:
        return Response({'error': 'item_id and so_number are required'}, status=400)

    try:
        item = Item.objects.select_related('gem_detail').get(pk=item_id)
    except Item.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)

    base_url = getattr(settings, 'FRONTEND_URL', 'https://ewanmillarltd.co.uk')
    item_url  = f'{base_url}/inventory/{item.id}'

    payload = {
        'sku':       item.sku or str(item.id),
        'so_number': so_number,
        'item_url':  item_url,
    }

    try:
        resp = requests.post(PRINT_SERVICE_URL, json=payload, timeout=10)
        resp.raise_for_status()
        return Response({'status': 'printed'})
    except requests.exceptions.ConnectionError:
        return Response(
            {'error': 'Print service not reachable — is print_service.py running?'},
            status=503,
        )
    except requests.exceptions.HTTPError as e:
        return Response({'error': str(e)}, status=502)