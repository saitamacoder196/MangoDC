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

    // Enable/disable green channel sliders based on checkbox state
    toggleGreenFilter.on('change', function() {
        const isChecked = $(this).is(':checked');
        greenMinSlider.prop('disabled', !isChecked);
        greenMaxSlider.prop('disabled', !isChecked);
        saveSettings();  // Save settings immediately when checkbox is toggled
    });

    // Update green channel values on slider input
    greenMinSlider.on('input', function() {
        greenMinValue.text($(this).val());
        saveSettings();
    });

    greenMaxSlider.on('input', function() {
        greenMaxValue.text($(this).val());
        saveSettings();
    });

    // Function to get the CSRF token from cookies
    function getCSRFToken() {
        const name = 'csrftoken=';
        const cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.indexOf(name) === 0) {
                return decodeURIComponent(cookie.substring(name.length));
            }
        }

        return null;
    }

    // Function to save settings to the server via AJAX
    function saveSettings() {
        const data = {
            toggle_green_filter: toggleGreenFilter.is(':checked'),
            green_min: greenMinSlider.val(),
            green_max: greenMaxSlider.val(),
            toggle_bg: $('#toggle-bg').is(':checked'),
            grayscale: $('#grayscale').is(':checked'),
            threshold: $('#threshold-slider').val(),
            brightness: $('#brightness-slider').val(),
            apply_morphology: $('#apply-morphology').is(':checked'),
            morph_kernel_size: $('#morph-kernel-size').val(),
            morph_iterations: $('#morph-iterations').val(),
            active_tab: $('.nav-link.active').attr('id')
        };

        $.ajax({
            url: window.location.href,
            type: 'POST',
            data: data,
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    }

    // Add event listeners for image processing tools
    $('#image-tools input, #image-tools select').on('input change', saveSettings);

    // Save settings when tab is changed
    $('.nav-link').on('click', saveSettings);
});
