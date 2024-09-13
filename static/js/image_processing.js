$(document).ready(function() {
    const currentItemIndex = parseInt(new URLSearchParams(window.location.search).get('item_index') || '0');

    // Event handler for the Next button
    $('#next-button').on('click', function() {
        window.location.href = `${window.location.pathname}?item_index=${currentItemIndex + 1}`;
    });

    // Event handler for the Previous button
    $('#prev-button').on('click', function() {
        window.location.href = `${window.location.pathname}?item_index=${currentItemIndex - 1}`;
    });

    // Set the height of the image tools section to match the height of the right content
    const imageTools = $('#image-tools');
    const imageTabsContainer = $('#image-tabs-container');
    if (imageTabsContainer.length && imageTools.length) {
        const rightContentHeight = imageTabsContainer.height();
        imageTools.height(rightContentHeight);
    }

    // Green channel filter related elements
    const greenMinSlider = $('#green-min-slider');
    const greenMaxSlider = $('#green-max-slider');
    const greenMinValue = $('#green-min-value');
    const greenMaxValue = $('#green-max-value');
    const toggleGreenFilter = $('#toggle-green-filter');

    // Grayscale related elements
    const toggleGrayscale = $('#toggle-grayscale');

    // Display loading indicator before processing
    function showLoading(processedImageId) {
        $(processedImageId).find('img').hide();  // Hide the image
        $(processedImageId).append('<div class="loading-spinner">Loading...</div>');  // Show loading spinner
    }

    // Hide loading indicator after processing
    function hideLoading(processedImageId) {
        $(processedImageId).find('.loading-spinner').remove();  // Remove loading spinner
        $(processedImageId).find('img').show();  // Show the processed image
    }

    // Enable/disable green channel sliders based on checkbox state
    toggleGreenFilter.on('change', function() {
        const isChecked = $(this).is(':checked');
        greenMinSlider.prop('disabled', !isChecked);
        greenMaxSlider.prop('disabled', !isChecked);
        if (isChecked) {
            applyGreenFilter();
        }
    });

    // Apply Grayscale filter when checkbox is toggled
    toggleGrayscale.on('change', function() {
        applyGrayscaleFilter();
    });

    // Update green channel values on slider input but process only on change (when user stops dragging)
    greenMinSlider.on('change', function() {
        greenMinValue.text($(this).val());
        applyGreenFilter();  // Process filter when slider interaction ends
    });

    greenMaxSlider.on('change', function() {
        greenMaxValue.text($(this).val());
        applyGreenFilter();  // Process filter when slider interaction ends
    });

    // Apply the green filter
    function applyGreenFilter() {
        const greenMin = parseInt($('#green-min-slider').val());
        const greenMax = parseInt($('#green-max-slider').val());

        // Loop through all original images and apply the filter
        $('.image-square img').each(function() {
            const imgElement = $(this)[0];
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = imgElement.width;
            canvas.height = imgElement.height;
            ctx.drawImage(imgElement, 0, 0);
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;

            // Display loading while processing
            const processedImageId = '#processed-' + imgElement.alt.toLowerCase().replace(/\./g, '\\.');
            showLoading(processedImageId);

            setTimeout(() => {  // Simulate async processing with a timeout
                for (let i = 0; i < data.length; i += 4) {
                    const g = data[i + 1]; // Green channel
                    // If green value is outside the range, set pixel to white
                    if (g < greenMin || g > greenMax) {
                        data[i] = 255;   // Red
                        data[i + 1] = 255; // Green
                        data[i + 2] = 255; // Blue
                    }
                }
                ctx.putImageData(imageData, 0, 0);
                $(processedImageId).find('img').attr('src', canvas.toDataURL());

                // Hide loading after processing
                hideLoading(processedImageId);
            }, 500);  // Simulate processing delay (500ms)
        });
    }

    // Apply Grayscale filter
    function applyGrayscaleFilter() {
        const applyGrayscale = toggleGrayscale.is(':checked');

        $('.image-square img').each(function() {
            const imgElement = $(this)[0];
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = imgElement.width;
            canvas.height = imgElement.height;
            ctx.drawImage(imgElement, 0, 0);
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;

            // Display loading while processing
            const processedImageId = '#processed-' + imgElement.alt.toLowerCase().replace(/\./g, '\\.');
            showLoading(processedImageId);

            setTimeout(() => {  // Simulate async processing with a timeout
                for (let i = 0; i < data.length; i += 4) {
                    const r = data[i];
                    const g = data[i + 1];
                    const b = data[i + 2];
                    const gray = 0.299 * r + 0.587 * g + 0.114 * b; // Grayscale calculation
                    data[i] = gray;    // Red
                    data[i + 1] = gray; // Green
                    data[i + 2] = gray; // Blue
                }
                ctx.putImageData(imageData, 0, 0);
                $(processedImageId).find('img').attr('src', canvas.toDataURL());

                // Hide loading after processing
                hideLoading(processedImageId);
            }, 500);  // Simulate processing delay (500ms)
        });
    }
});
