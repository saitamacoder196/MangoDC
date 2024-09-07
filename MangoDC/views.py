import cv2
from django.http import JsonResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PIL import Image
import os

import numpy as np
from MangoDC import settings
from .helper import invert_black_and_white, process_image, remove_background, convert_to_grayscale, resize_image, threshold_image
from PIL import ImageEnhance
# View cho trang Home
def home(request):
    return render(request, 'home.html')

# View cho trang Experiment
def experiment(request):
    return render(request, 'experiment.html')

# View cho trang Demo
def demo(request):
    return render(request, 'demo.html')

# View to handle image upload and processing
import concurrent.futures

# View to handle image upload and processing
def image_processing(request):
    context = {}

    if request.method == 'POST' and request.FILES.getlist('folder_path'):
        files = request.FILES.getlist('folder_path')
        fs = FileSystemStorage()
        image_data = {}
        item_ids = []

        for file in files:
            file_name_parts = os.path.splitext(file.name)[0].split('-')

            # Ensure correct naming convention
            if len(file_name_parts) < 4:
                continue

            item_id = '-'.join(file_name_parts[:3])
            corner_name = file_name_parts[-1]

            # Store image data for unique item_id
            if item_id not in image_data:
                image_data[item_id] = {}
                item_ids.append(item_id)

            if corner_name not in image_data[item_id]:
                # Save file and update image data
                file_path = fs.save(file.name, file)
                file_url = fs.url(file_path)
                image_data[item_id][corner_name] = {'url': file_url, 'name': corner_name}

        # Store data in session only once
        request.session['image_data'] = image_data
        request.session['item_ids'] = item_ids

    else:
        # Retrieve session data if not a POST request
        image_data = request.session.get('image_data', {})
        item_ids = request.session.get('item_ids', [])

    # Set the current item based on index
    current_item_index = int(request.GET.get('item_index', 0))
    current_item_id = item_ids[current_item_index] if item_ids else None

    # Load session settings into context
    context.update({
        'toggle_bg': request.session.get('toggle_bg', False),
        'grayscale': request.session.get('grayscale', False),
        'threshold': request.session.get('threshold', 128),
        'brightness': request.session.get('brightness', 0),
        'apply_morphology': request.session.get('apply_morphology', False),
        'morph_kernel_size': request.session.get('morph_kernel_size', 3),
        'morph_iterations': request.session.get('morph_iterations', 1),
        'active_tab': request.session.get('active_tab', 'processing'),
        'is_first_item': current_item_index == 0,
        'is_last_item': current_item_index == len(item_ids) - 1,
        'current_item_id': current_item_id
    })

    if current_item_id:
        # Limit to 12 images
        image_files = list(image_data[current_item_id].values())[:12]
        processed_images = []

        # Use ThreadPoolExecutor for multithreaded image processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Map images to threads and execute processing in parallel
            futures = {executor.submit(process_with_user_options, img, request): img for img in image_files}
            
            # Wait for all threads to complete and gather the results
            for future in concurrent.futures.as_completed(futures):
                _, updated_img_obj = future.result()
                processed_images.append(updated_img_obj)

        # Update context with image data
        context['image_files'] = image_files
        context['processed_images'] = processed_images

    return render(request, 'image_processing.html', context)

# Helper function to process the image with user options
def process_with_user_options(img_obj, request):
    """
    Apply image processing options from user session settings and save the processed image
    with 'processed_' prefix in its filename. Return the processed image and updated img_obj.
    """
    # Retrieve settings from session
    toggle_bg = request.session.get('toggle_bg', False)
    grayscale = request.session.get('grayscale', False)
    threshold = request.session.get('threshold', 128)
    brightness = request.session.get('brightness', 0)
    apply_morphology = request.session.get('apply_morphology', False)
    morph_kernel_size = request.session.get('morph_kernel_size', 3)
    morph_iterations = request.session.get('morph_iterations', 1)

    # Load the original image
    original_image_path = os.path.join(settings.MEDIA_ROOT, os.path.basename(img_obj['url']))
    processed_image_name = f"processed_{os.path.basename(img_obj['url'])}"
    processed_image_path = os.path.join(settings.MEDIA_ROOT, processed_image_name)

    # If the processed image exists, skip processing and return the cached image
    if os.path.exists(processed_image_path):
        return None, {
            'url': os.path.join('/media', processed_image_name),
            'name': os.path.basename(img_obj['url'])
        }

    # Process the image if not cached
    image = Image.open(original_image_path)

    # Step 1: Resize image
    image = resize_image(image)

    # Step 2: Remove background if enabled
    if toggle_bg:
        image = remove_background(image)
        image = invert_black_and_white(image)

    # Step 3: Convert to grayscale if enabled
    if grayscale:
        image = convert_to_grayscale(image)

    # Step 4: Apply threshold if enabled
    if grayscale and threshold > 0:
        image = threshold_image(image, threshold)

    # Step 5: Apply morphology if enabled
    if apply_morphology:
        image_np = np.array(image)
        kernel = np.ones((morph_kernel_size, morph_kernel_size), np.uint8)
        image_np = cv2.morphologyEx(image_np, cv2.MORPH_OPEN, kernel, iterations=morph_iterations)
        image = Image.fromarray(image_np)

    # Step 6: Adjust brightness
    if brightness != 0:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1 + (brightness / 100.0))

    # Save the processed image to the /media/ folder
    image.save(processed_image_path)

    # Return the processed image and the updated img_obj
    return image, {
        'url': os.path.join('/media', processed_image_name),  # Return relative URL with '/media' prefix
        'name': os.path.basename(img_obj['url'])  # Return the original filename as 'name'
    }
