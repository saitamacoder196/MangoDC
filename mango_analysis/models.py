from django.db import models

class MangoItem(models.Model):
    id = models.AutoField(primary_key=True)  # Tự động tăng
    mango_id = models.CharField(max_length=50)  # Mã xoài ở dạng text, đảm bảo duy nhất
    folder_path = models.CharField(max_length=255)

    def __str__(self):
        return self.mango_id


class Image(models.Model):
    mango_item = models.ForeignKey(MangoItem, on_delete=models.CASCADE, related_name='images')
    IMAGE_TYPES = [
        ('original', 'Original'),
        ('prediction', 'Prediction'),
    ]
    image_type = models.CharField(max_length=10, choices=IMAGE_TYPES)
    position = models.CharField(max_length=10)  # e.g., 'Left_1', 'Center_2', etc.
    image_path = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.mango_item.id} - {self.image_type} - {self.position}"

class DetectedArea(models.Model):
    mango_item = models.ForeignKey(MangoItem, on_delete=models.CASCADE, related_name='detected_areas')
    image = models.CharField(max_length=50)
    position_x = models.IntegerField()
    position_y = models.IntegerField()
    area_size = models.FloatField()
    disease = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.mango_item.id} - {self.disease} at ({self.position_x}, {self.position_y})"

class Conclusion(models.Model):
    mango_item = models.OneToOneField(MangoItem, on_delete=models.CASCADE, related_name='conclusion')
    total_disease_area = models.FloatField()
    total_mango_surface_area = models.FloatField()
    disease_area_percentage = models.FloatField()
    conclusion = models.TextField()

    def __str__(self):
        return f"Conclusion for {self.mango_item.id}"