from django.urls import path
from .views import login_view, search_view, normal_view

urlpatterns = [
    path("login/", login_view),
    path("search/", search_view),
    path("normal/", normal_view),
]