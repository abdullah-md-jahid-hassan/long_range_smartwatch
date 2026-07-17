from django.urls import path, include

urlpatterns = [
    path("auth/",          include("authentication.v1.urls")),
    path("otp/",           include("otp.v1.urls")),
    path("notifications/", include("notifications.v1.urls")),
]
