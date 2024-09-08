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
    path('demo2/', views.demo2, name='demo2'),
    path('capture/', views.capture, name='capture'),
    path('turnoff/', views.turnoff, name='turnoff'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
