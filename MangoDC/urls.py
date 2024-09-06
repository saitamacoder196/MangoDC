from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Trang Home
    path('image-processing/', views.image_processing, name='image_processing'),
    path('experiment/', views.experiment, name='experiment'),
    path('demo/', views.demo, name='demo'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
