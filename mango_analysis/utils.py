
from django.db import transaction
from .models import MangoItem, Image, DetectedArea, Conclusion

@transaction.atomic
def save_mango_data(payload_results):
    # Lưu MangoItem
    mango_item = MangoItem.objects.create(
        id=payload_results['current_item']['id'],
        folder_path=payload_results['current_item']['folder_path']
    )

    # Lưu Images
    for image_type in ['prediction_images', 'original_images']:
        for position, path in payload_results[image_type].items():
            Image.objects.create(
                mango_item=mango_item,
                image_type='prediction' if image_type == 'prediction_images' else 'original',
                position=position,
                image_path=path
            )

    # Lưu DetectedAreas
    for area in payload_results['conclusion']['detected_areas']:
        DetectedArea.objects.create(
            mango_item=mango_item,
            image=area['image'],
            position_x=area['position']['x'],
            position_y=area['position']['y'],
            area_size=area['area_size'],
            disease=area['disease']
        )

    # Lưu Conclusion
    Conclusion.objects.create(
        mango_item=mango_item,
        total_disease_area=payload_results['conclusion']['total_disease_area'],
        total_mango_surface_area=payload_results['conclusion']['total_mango_surface_area'],
        disease_area_percentage=payload_results['conclusion']['disease_area_percentage'],
        conclusion=payload_results['conclusion']['conclusion']
    )

    return mango_item