from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("compliance.urls")),
    # Login/logout para la API navegable de DRF (botón en la esquina superior).
    path("api-auth/", include("rest_framework.urls")),
]
