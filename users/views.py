from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_view(request):
    return JsonResponse({"message": "login endpoint"})

def search_view(request):
    return JsonResponse({"message": "search endpoint"})

def normal_view(request):
    return JsonResponse({"message": "normal endpoint"})