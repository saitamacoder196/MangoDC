from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PIL import Image
import os
from MangoDC import settings

# View cho trang Home
def home(request):
    return render(request, 'home.html')

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

    # Initialize processed_images as an empty list
    processed_images = []

    # Check if the request is POST and contains uploaded files
    if request.method == 'POST' and request.FILES.getlist('folder_path'):
        files = request.FILES.getlist('folder_path')
        fs = FileSystemStorage()

        image_data = {}
        item_ids = []  # List to store unique item-ids
        processed_data = {}  # To store processed images by item_id

        # Save files and process images
        for file in files:
            file_name_without_ext = os.path.splitext(file.name)[0]
            file_name_parts = file_name_without_ext.split('-')

            if len(file_name_parts) < 4:
                continue  # Ignore files that don't follow the naming convention

            item_id = '-'.join(file_name_parts[:3])  # Combine first 3 parts to form item-id
            corner_name = file_name_parts[-1]  # The last part is the corner name

            # Add item_id to the list of item ids
            if item_id not in item_ids:
                item_ids.append(item_id)

            # Store original image data
            if item_id not in image_data:
                image_data[item_id] = {}

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

                # Store processed images
                if item_id not in processed_data:
                    processed_data[item_id] = {}

                processed_data[item_id][corner_name] = {
                    'url': fs.url(processed_image_name),
                    'name': corner_name
                }

        # Store the image data, item_ids, and processed data in the session
        request.session['image_data'] = image_data
        request.session['item_ids'] = item_ids
        request.session['processed_data'] = processed_data

    # If the request is GET (navigation through items)
    else:
        # Retrieve image data, item_ids, and processed_data from session
        image_data = request.session.get('image_data', {})
        item_ids = request.session.get('item_ids', [])
        processed_data = request.session.get('processed_data', {})

    # Get the current item-id from request or default to the first one
    current_item_index = int(request.GET.get('item_index', 0))
    current_item_id = item_ids[current_item_index] if item_ids else None

    # Check if it's the first or last item
    context['is_first_item'] = current_item_index == 0
    context['is_last_item'] = current_item_index == len(item_ids) - 1
    context['current_item_id'] = current_item_id

    # Define the full list of expected corner names
    expected_corners = ['Right_1', 'Right_2', 'Right_3', 'Right_4', 
                        'Left_1', 'Left_2', 'Left_3', 'Left_4', 
                        'Center_1', 'Center_2', 'Center_3', 'Center_4']

    # Get images for the current item
    if current_item_id:
        # Original images
        image_files = list(image_data[current_item_id].values())  # Get existing original images

        # Processed images
        processed_images = list(processed_data[current_item_id].values()) if current_item_id in processed_data else []

        # Find which corners are missing for both original and processed images
        existing_corners = {img['name'] for img in image_files}
        missing_corners = [corner for corner in expected_corners if corner not in existing_corners]

        # Add placeholders for missing corners in original images
        for missing_corner in missing_corners:
            image_files.append({'url': None, 'name': missing_corner})

        # Add placeholders for missing corners in processed images
        existing_processed_corners = {img['name'] for img in processed_images}
        missing_processed_corners = [corner for corner in expected_corners if corner not in existing_processed_corners]
        for missing_corner in missing_processed_corners:
            processed_images.append({'url': None, 'name': missing_corner})

        # Ensure we only return 12 images for both original and processed
        image_files = image_files[:12]
        processed_images = processed_images[:12]

        context['image_files'] = image_files
        context['processed_images'] = processed_images

    return render(request, 'image_processing.html', context)
