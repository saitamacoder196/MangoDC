import threading
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
import concurrent.futures
from django.http import JsonResponse
from MangoDC import settings
from MangoDC.helper import process_with_user_options
from codev4.main import RunTime

server = RunTime()

# View cho trang Home
def home(request):
    return render(request, 'home.html')

# View cho trang Experiment
def experiment(request):
    return render(request, 'experiment.html')

# View cho trang Demo
def demo(request):
    return render(request, 'demo.html')

# View cho trang Demo
def demo2(request):
    return render(request, 'demo2.html')

def capture(request): 
    if not server.running:  # Only start if it's not already running
        threading.Thread(target=server.start).start()  # Run server.start() in a new thread
        return JsonResponse({'message': 'WebSocket server is starting in the background!'})
    else:
        return JsonResponse({'message': 'WebSocket server is already running!'})

def turnoff(request):
    if server.running:  # Only stop if it's running
        threading.Thread(target=server.stop).start()  # Run server.stop() in a new thread
        return JsonResponse({'message': 'WebSocket server is stopping in the background!'})
    else:
        return JsonResponse({'message': 'WebSocket server is not running!'})

def sort_image_files(image_files):
    # Define a custom sorting key to arrange by Left, Center, Right, and index
    def sort_key(item):
        name = item['name']
        # Extract the corner name and the index number
        corner, index = name.split('_')
        index = int(index)  # Convert the index to integer for proper sorting
        # Assign priority to Left, Center, Right
        priority = {'Left': 0, 'Center': 1, 'Right': 2}
        return (priority.get(corner, 3), index)

    # Sort the image files based on the custom sort key
    return sorted(image_files, key=sort_key)

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

    # Get values from query params
    toggle_bg = request.GET.get('toggle-bg', 'false') == 'true'
    grayscale = request.GET.get('grayscale', 'false') == 'true'
    threshold = int(request.GET.get('threshold-slider', 128))
    brightness = int(request.GET.get('brightness-slider', 0))
    apply_morphology = request.GET.get('apply-morphology', 'false') == 'true'
    morph_kernel_size = int(request.GET.get('morph-kernel-size', 3))
    morph_iterations = int(request.GET.get('morph-iterations', 1))
    active_tab = request.GET.get('active_tab', 'processing')

    # Load settings into context
    context.update({
        'toggle_bg': toggle_bg,
        'grayscale': grayscale,
        'threshold': threshold,
        'brightness': brightness,
        'apply_morphology': apply_morphology,
        'morph_kernel_size': morph_kernel_size,
        'morph_iterations': morph_iterations,
        'active_tab': active_tab,
        'is_first_item': current_item_index == 0,
        'is_last_item': current_item_index == len(item_ids) - 1,
        'current_item_id': current_item_id
    })

    if current_item_id:
        # Retrieve image files for the current item and sort them
        image_files = list(image_data[current_item_id].values())
        sorted_image_files = sort_image_files(image_files)  # Sort the image files
        processed_images = [None] * len(sorted_image_files)  # Initialize a list to store processed images

        # Use ThreadPoolExecutor for multithreaded image processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(process_with_user_options, img, request): i for i, img in enumerate(sorted_image_files)}

            # Wait for all threads to complete and place the results in the correct order
            for future in concurrent.futures.as_completed(futures):
                i = futures[future]  # Get the index of the processed image
                _, updated_img_obj = future.result()
                processed_images[i] = updated_img_obj  # Place the result in the correct position

        # Update context with sorted and processed image data
        context['image_files'] = sorted_image_files
        context['processed_images'] = processed_images

    return render(request, 'image_processing.html', context)
