from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login


@csrf_exempt
def api_login_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "POST required"}, status=405)

    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({"detail": "Invalid credentials"}, status=401)

    login(request, user)
    return JsonResponse({"detail": "Logged in"})


def login_test_view(request):
    return JsonResponse({
        "authenticated": request.user.is_authenticated,
        "user": str(request.user),
    })


def search_view(request):
    return JsonResponse({"message": "search endpoint"})


def normal_view(request):
    return JsonResponse({"message": "normal endpoint"})