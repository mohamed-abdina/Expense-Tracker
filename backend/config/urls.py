from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_root(request):
    return Response({
        "message": "Expense Tracker API",
        "endpoints": {
            "register": "/api/register/",
            "login": "/api/login/",
            "profile": "/api/profile/",
            "categories": "/api/categories/",
            "transactions": "/api/transactions/",
            "dashboard": "/api/dashboard/",
            "reports": "/api/reports/",
            "admin": "/admin/",
        }
    })


urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('api/', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('categories.urls')),
    path('api/', include('transactions.urls')),
    path('api/', include('reports.urls')),
]
