from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import MangoItem
from .serializers import MangoItemSerializer

class MangoItemDetailView(APIView):
    def get(self, request, mango_id):
        try:
            mango_item = MangoItem.objects.get(mango_id=mango_id)
        except MangoItem.DoesNotExist:
            return Response({"error": "MangoItem not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MangoItemSerializer(mango_item)
        return Response(serializer.data)

class FolderPathListView(APIView):
    def get(self, request):
        folder_paths = MangoItem.objects.values('folder_path').distinct()
        return Response({"folder_paths": [item['folder_path'] for item in folder_paths]})

class MangoItemByFolderView(APIView):
    def get(self, request):
        folder_path = request.query_params.get('folder_path')
        index = request.query_params.get('index')

        try:
            # Lấy tất cả các MangoItem trong folder_path, sắp xếp theo mango_id
            items = MangoItem.objects.filter(folder_path=folder_path).order_by('mango_id')

            # Kiểm tra số lượng items
            item_count = items.count()
            if item_count == 0:
                return Response({"error": "No items found in the specified folder"}, status=status.HTTP_404_NOT_FOUND)

            # Kiểm tra index hợp lệ
            index = int(index)
            if index < 0 or index >= item_count:
                return Response({"error": f"Invalid index. Must be between 0 and {item_count - 1}"}, status=status.HTTP_400_BAD_REQUEST)

            # Lấy item tại index chỉ định
            mango_item = items[index]
            
            serializer = MangoItemSerializer(mango_item)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LatestMangoItemView(APIView):
    def get(self, request):
        try:
            # Lấy mango item mới nhất dựa trên trường id (giả sử id là tự động tăng)
            latest_mango = MangoItem.objects.latest('id')
            serializer = MangoItemSerializer(latest_mango)
            return Response(serializer.data)
        except MangoItem.DoesNotExist:
            return Response({"error": "No mango items found"}, status=status.HTTP_404_NOT_FOUND)
