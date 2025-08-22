from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def root_view(request):
    return HttpResponse(
        "Process Monitor API. "
        "Use /api/processes/ for process data, "
        "/api/system-info/ for system details, "
        "or /admin/ for admin interface."
    )

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/', include('processes.urls')),   # ✅ includes processes + system-info
]
