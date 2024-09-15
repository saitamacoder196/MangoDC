from django.urls import path
from .views import MangoItemDetailView, FolderPathListView, MangoItemByFolderView

urlpatterns = [
    path('mango-item/<str:mango_id>/', MangoItemDetailView.as_view(), name='mango-item-detail'),
    path('folder-paths/', FolderPathListView.as_view(), name='folder-path-list'),
    path('mango-item-by-folder/', MangoItemByFolderView.as_view(), name='mango-item-by-folder'),
]