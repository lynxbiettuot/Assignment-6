import requests
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt


class APIGatewayProxyView:
    """
    A custom reverse proxy view that forwards requests to the appropriate
    backend microservice based on the URL prefix, using the 'requests' library.
    Exempt from CSRF to allow passthrough of POST/PUT/DELETE requests.
    """

    SERVICE_MAP = {
        'books':        'http://book-service:8000',
        'cart':         'http://cart-service:8000',
        'orders':       'http://order-service:8000',
        'auth':         'http://auth-service:8000',
        'catalog':      'http://catalog-service:8000',
        'comment-rate': 'http://comment-rate-service:8000',
        'customer':     'http://customer-service:8000',
        'manager':      'http://manager-service:8000',
        'pay':          'http://pay-service:8000',
        'recommender':  'http://recommender-ai-service:8000',
        'ship':         'http://ship-service:8000',
        'staff':        'http://staff-service:8000',
    }

    # Headers from the upstream response we should NOT forward back to client
    EXCLUDED_RESPONSE_HEADERS = {'transfer-encoding', 'connection'}

    def as_view(self):
        @csrf_exempt
        def view(request, **kwargs):
            return self._proxy(request)
        return view

    def _proxy_with_path(self, request, path_override):
        """Proxy with an explicit path override instead of using request.path."""
        original_path = request.path
        # Temporarily override using a simple attribute
        request.__dict__['path'] = path_override
        try:
            return self._proxy(request)
        finally:
            request.__dict__['path'] = original_path

    def _proxy(self, request):
        # We'll use the actual request path to avoid Django's URL argument stripping/parsing
        full_path = request.path
        if not full_path.startswith('/api/'):
            return HttpResponse("Gateway Error: Invalid proxy path.", status=400)
        
        # Strip /api/ to get service name and subpath
        # e.g. /api/cart/carts/1/ -> rel_path = cart/carts/1/
        rel_path = full_path[5:] 
        
        # Split into service name and subpath
        # e.g. cart/carts/1/ -> target_service="cart", subpath="/carts/1/"
        import re
        match = re.match(r'^([^/]+)(/(.*))?$', rel_path)
        if not match:
            return HttpResponse("Gateway Error: Could not parse service name.", status=400)
        
        target_service = match.group(1)
        # subpath should start with /
        subpath = match.group(2) if match.group(2) else '/'
        
        if target_service not in self.SERVICE_MAP:
            return HttpResponseNotFound(f"Gateway Error: Service '{target_service}' not found.")
        
        upstream_base = self.SERVICE_MAP[target_service].rstrip('/')
        upstream_url = f"{upstream_base}{subpath}"
        
        # Preserve query string
        query_params = request.META.get('QUERY_STRING', '')
        if query_params:
            upstream_url = f"{upstream_url}?{query_params}"

        # Prepare headers
        forward_headers = {}
        for header, value in request.headers.items():
            if header.lower() not in ['host', 'content-length']:
                forward_headers[header] = value

        import sys
        try:
            sys.stderr.write(f"\nGATEWAY PROXY: {request.method} {full_path} -> {upstream_url}\n")
            sys.stderr.flush()
            
            upstream_resp = requests.request(
                method=request.method,
                url=upstream_url,
                headers=forward_headers,
                data=request.body,
                timeout=15,
                allow_redirects=True,  # Follow redirects internally so browser never sees a 301
            )
            sys.stderr.write(f"GATEWAY RESPONSE: {upstream_resp.status_code}\n")
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"GATEWAY FAIL: {str(e)}\n")
            return HttpResponse(f"Gateway Error: {str(e)}", status=502)
        finally:
            sys.stderr.flush()

        # Build Django response
        response = HttpResponse(
            content=upstream_resp.content,
            status=upstream_resp.status_code,
            content_type=upstream_resp.headers.get('Content-Type', 'application/json'),
        )

        # Forward headers, rewriting Location for redirects
        for header_name, header_value in upstream_resp.headers.items():
            if header_name.lower() in self.EXCLUDED_RESPONSE_HEADERS:
                continue
            
            final_value = header_value
            if header_name.lower() == 'location':
                # Upstream might return relative path /carts/1/
                if header_value.startswith('/'):
                    final_value = f"/api/{target_service}{header_value}"
                # Upstream might return absolute but internal URL http://cart-service:8000/carts/1/
                elif upstream_base in header_value:
                    internal_path = header_value.split(upstream_base)[-1]
                    final_value = f"/api/{target_service}{internal_path}"
                
                sys.stderr.write(f"GATEWAY REDIRECT: Rewriting {header_value} -> {final_value}\n")
                sys.stderr.flush()

            try:
                response[header_name] = final_value
            except Exception:
                pass

        return response


# Singleton instance
gateway_proxy = APIGatewayProxyView()
