from django.urls import path
from .views import api_login_view, login_test_view, search_view, normal_view

urlpatterns = [
    path("api-login/", api_login_view),      # AUTH ONLY
    path("login/", login_test_view),         # RATE-LIMIT TEST
    path("search/", search_view),
    path("normal/", normal_view),
]