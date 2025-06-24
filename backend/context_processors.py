from django.conf import settings

def static_timestamp(request):
    return {'STATIC_TIMESTAMP': getattr(settings, 'STATIC_TIMESTAMP', '')}
