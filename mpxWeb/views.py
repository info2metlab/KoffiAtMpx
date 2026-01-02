from django.http import JsonResponse
import os


os.environ["RATING_URL"]  = 'http://localhost:5050/api/Transfo'
def health(request):
	return JsonResponse({'status': 'ok'})
