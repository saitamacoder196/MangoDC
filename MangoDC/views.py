from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PIL import Image
import os
from MangoDC import settings

# View cho trang Home
def home(request):
    return render(request, 'home.html')

# View cho trang Image Processing
def image_processing(request):
    return render(request, 'image_processing.html')

# View cho trang Experiment
def experiment(request):
    return render(request, 'experiment.html')

# View cho trang Demo
def demo(request):
    return render(request, 'demo.html')

# Helper function to process images
def process_image(image: Image.Image):
    image = image.convert('L')  # Convert image to grayscale (example)
    return image, None

# View to handle image upload and processing
def image_processing(request):
    context = {}
    if request.method == 'POST' and request.FILES.getlist('folder_path'):
        files = request.FILES.getlist('folder_path')
        fs = FileSystemStorage()

        image_data = {}
        processed_images = []

        for file in files:
            file_name_without_ext = os.path.splitext(file.name)[0]
            file_name_parts = file_name_without_ext.split('-')

            if len(file_name_parts) < 4:
                continue  # Ignore files that don't follow the naming convention

            item_id = '-'.join(file_name_parts[:3])  # Combine first 3 parts to form item-id
            corner_name = file_name_parts[-1]  # The last part is the corner name

            # Store original image data
            if item_id not in image_data:
                image_data[item_id] = {}

            # Only keep the first unique corner per item-id
            if corner_name not in image_data[item_id]:
                file_path = fs.save(file.name, file)
                file_url = fs.url(file_path)
                image_data[item_id][corner_name] = {
                    'url': file_url,
                    'name': corner_name
                }

                # Process image and save processed version
                image = Image.open(os.path.join(settings.MEDIA_ROOT, file.name))
                processed_image, _ = process_image(image)
                processed_image_name = f'processed_{file.name}'
                processed_image_path = os.path.join(settings.MEDIA_ROOT, processed_image_name)
                processed_image.save(processed_image_path)

                processed_images.append({
                    'url': fs.url(processed_image_name),
                    'name': corner_name
                })

        # Select the first item_id and limit to 12 unique corner images
        if image_data:
            first_item_id = next(iter(image_data))  # Get the first item_id
            image_files = list(image_data[first_item_id].values())[:12]

            # Ensure there are placeholders for missing images
            while len(image_files) < 12:
                image_files.append({'url': None, 'name': 'Placeholder'})

            context['image_files'] = image_files
            context['processed_images'] = processed_images[:12]  # Only take the first 12 processed images

    return render(request, 'image_processing.html', context)
