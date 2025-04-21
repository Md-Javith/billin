from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('core.urls')),
    path('',include('purchase.urls')),

    # path('',include('product.urls')),
    path('api/',include('core.urls')),
    path('api/',include('purchase.urls')),

    # path('api/',include('product.urls')),
    
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI view
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redoc UI view
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
