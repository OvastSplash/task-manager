from django.http import JsonResponse
from django.conf import settings
from .models import Token

class TokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.path.startswith('/api/v1/task/'):
            token = request.headers.get('TOKEN')
            
            is_token = Token.objects.filter(token=token).exists()
            if not is_token:
                print(f"Token: {token}")
                return JsonResponse({'error': 'Forbidden'}, status=403)

        response = self.get_response(request)
        return response