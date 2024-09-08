document.addEventListener("DOMContentLoaded", () => {
    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const step3 = document.getElementById('step-3');
    const step4 = document.getElementById('step-4');
    const step5 = document.getElementById('step-5');

    const loadImagesBtn = document.getElementById('load-images');
    const runProcessBtn = document.getElementById('run-process');
    const showResultsBtn = document.getElementById('show-results');

    const originalImagesContainer = document.getElementById('original-images');
    const processedImagesContainer = document.getElementById('processed-images');
    const diseaseResultsTable = document.getElementById('disease-results');
    const conclusionText = document.getElementById('conclusion');

    // Placeholder data for diseases
    const diseases = [
        { name: "Thánh Thư", corner: "Left", area: 5000, percentage: 15 },
        { name: "Đốm đen", corner: "Right", area: 3000, percentage: 10 },
        { name: "Rùi đụt", corner: "Center", area: 12000, percentage: 25 },
        { name: "Da ếch", corner: "Left", area: 9000, percentage: 20 }
    ];

    // Step 1: Load images from folder
    loadImagesBtn.addEventListener('click', () => {
        step1.classList.remove('active');
        step2.classList.add('active');

        // Simulating the loading of 12 images
        for (let i = 1; i <= 12; i++) {
            const imgDiv = document.createElement('div');
            imgDiv.className = 'image-square';
            const img = document.createElement('img');
            img.src = `https://via.placeholder.com/150?text=Image+${i}`;
            imgDiv.appendChild(img);
            originalImagesContainer.appendChild(imgDiv);
        }
    });

    // Step 2: Process images
    runProcessBtn.addEventListener('click', () => {
        step2.classList.remove('active');
        step3.classList.add('active');

        // Simulate image processing with loading spinner
        setTimeout(() => {
            step3.classList.remove('active');
            step4.classList.add('active');

            // Display processed images
            for (let i = 1; i <= 12; i++) {
                const imgDiv = document.createElement('div');
                imgDiv.className = 'image-square';
                const img = document.createElement('img');
                img.src = `https://via.placeholder.com/150?text=Processed+${i}`;
                imgDiv.appendChild(img);
                processedImagesContainer.appendChild(imgDiv);
            }
        }, 3000); // Simulate processing time (3 seconds)
    });

    // Step 3: Show disease detection results with additional loading
    showResultsBtn.addEventListener('click', () => {
        step4.classList.remove('active');
        step3.classList.add('active'); // Reuse loading screen

        // Simulate result loading with a delay
        setTimeout(() => {
            step3.classList.remove('active');
            step5.classList.add('active');

            // Populate the disease results
            diseases.forEach(disease => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${disease.name}</td>
                    <td>${disease.corner}</td>
                    <td>${disease.area}</td>
                    <td>${disease.percentage}%</td>
                `;
                diseaseResultsTable.appendChild(row);
            });

            // Display the disease with the highest percentage
            const maxDisease = diseases.reduce((prev, current) => (prev.percentage > current.percentage) ? prev : current);
            conclusionText.textContent = `${maxDisease.name} with ${maxDisease.percentage}% affected area`;
        }, 3000); // Simulate additional loading time for results (3 seconds)
    });
});
