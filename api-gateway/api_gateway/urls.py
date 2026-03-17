from django.contrib import admin
from django.urls import path, re_path, include
from django.views.decorators.csrf import csrf_exempt
from .proxy import gateway_proxy


@csrf_exempt
def legacy_carts_proxy(request, rest=''):
    """Catch-all for old-style /carts/<id>/ requests — rewrite path to /api/cart/ and proxy."""
    return gateway_proxy._proxy_with_path(request, f'/api/cart/carts/{rest}')


@csrf_exempt
def legacy_shipping_proxy(request, rest=''):
    """Catch-all for old-style /shipping/<path> requests — rewrite path to /api/ship/ and proxy."""
    return gateway_proxy._proxy_with_path(request, f'/api/ship/shipping/{rest}')


urlpatterns = [
    path('admin/', admin.site.urls),
    # Forward any request starting with /api/ to the reverse proxy
    re_path(r'^api/.*$', gateway_proxy.as_view(), name='api_gateway'),
    # Catch legacy /carts/ URLs (browser cache may still use old-style URLs)
    re_path(r'^carts/(?P<rest>.*)$', legacy_carts_proxy, name='carts_legacy'),
    # Catch legacy /shipping/ URLs (browser cache may still use old-style URLs)
    re_path(r'^shipping/(?P<rest>.*)$', legacy_shipping_proxy, name='shipping_legacy'),
    # Keep the frontend views
    path('', include('app.urls')),
]
