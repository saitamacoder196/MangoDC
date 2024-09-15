from rest_framework import serializers
from .models import MangoItem, Image, DetectedArea, Conclusion

class DetectedAreaSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()

    class Meta:
        model = DetectedArea
        fields = ['image', 'position', 'area_size', 'disease']

    def get_position(self, obj):
        return {"x": obj.position_x, "y": obj.position_y}

class ConclusionSerializer(serializers.ModelSerializer):
    detected_areas = DetectedAreaSerializer(many=True, read_only=True)

    class Meta:
        model = Conclusion
        fields = ['detected_areas', 'total_disease_area', 'total_mango_surface_area', 'disease_area_percentage', 'conclusion']

class MangoItemSerializer(serializers.ModelSerializer):
    prediction_images = serializers.SerializerMethodField()
    original_images = serializers.SerializerMethodField()
    conclusion = ConclusionSerializer()

    class Meta:
        model = MangoItem
        fields = ['mango_id', 'folder_path', 'prediction_images', 'original_images', 'conclusion']

    def get_prediction_images(self, obj):
        return {img.position: img.image_path for img in obj.images.filter(image_type='prediction')}

    def get_original_images(self, obj):
        return {img.position: img.image_path for img in obj.images.filter(image_type='original')}

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return {
            "current_item": {
                "id": ret['mango_id'],
                "folder_path": ret['folder_path']
            },
            "prediction_images": ret['prediction_images'],
            "original_images": ret['original_images'],
            "conclusion": ret['conclusion']
        }