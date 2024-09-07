window.onload = function() {
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    const currentItemIndex = parseInt(new URLSearchParams(window.location.search).get('item_index') || '0');

    // Event handler for the Next button
    nextButton.addEventListener('click', function() {
        window.location.href = `${window.location.pathname}?item_index=${currentItemIndex + 1}`;
    });

    // Event handler for the Previous button
    prevButton.addEventListener('click', function() {
        window.location.href = `${window.location.pathname}?item_index=${currentItemIndex - 1}`;
    });

    // Set the height of the image tools section to match the height of the right content
    const imageTools = document.getElementById('image-tools');
    const imageTabsContainer = document.getElementById('image-tabs-container');
    if (imageTabsContainer && imageTools) {
        const rightContentHeight = imageTabsContainer.offsetHeight;
        imageTools.style.height = rightContentHeight + 'px';
    }

    // Function to get the CSRF token from cookies
    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the CSRF token name?
                if (cookie.substring(0, 'csrftoken'.length + 1) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Function to save settings to the server via AJAX
    function saveSettings() {
        const toggleBg = document.getElementById('toggle-bg').checked;
        const grayscale = document.getElementById('grayscale').checked;
        const threshold = document.getElementById('threshold-slider').value;
        const brightness = document.getElementById('brightness-slider').value;
        const applyMorphology = document.getElementById('apply-morphology').checked;
        const morphKernelSize = document.getElementById('morph-kernel-size').value;
        const morphIterations = document.getElementById('morph-iterations').value;
        const activeTab = document.querySelector('.nav-link.active').getAttribute('id');

        const data = new FormData();
        data.append('toggle_bg', toggleBg);
        data.append('grayscale', grayscale);
        data.append('threshold', threshold);
        data.append('brightness', brightness);
        data.append('apply_morphology', applyMorphology);
        data.append('morph_kernel_size', morphKernelSize);
        data.append('morph_iterations', morphIterations);
        data.append('active_tab', activeTab);

        fetch(window.location.href, {
            method: 'POST',
            body: data,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()  // Include the CSRF token in the headers
            }
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
    }

    // Add event listeners for image processing tools
    const inputs = document.querySelectorAll('#image-tools input, #image-tools select');
    inputs.forEach(input => {
        input.addEventListener('input', saveSettings);
    });

    const tabs = document.querySelectorAll('.nav-link');
    tabs.forEach(tab => {
        tab.addEventListener('click', saveSettings);
    });
};
