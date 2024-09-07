document.addEventListener("DOMContentLoaded", () => {
    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const step3 = document.getElementById('step-3');
    const step4 = document.getElementById('step-4');

    const nextToStep2Btn = document.getElementById('next-to-step-2');
    const startTestBtn = document.getElementById('start-test');

    // Show next step (model selection)
    nextToStep2Btn.addEventListener('click', () => {
        step1.classList.remove('active');
        step2.classList.add('active');
    });

    // Show loading screen, then results
    startTestBtn.addEventListener('click', () => {
        step2.classList.remove('active');
        step3.classList.add('active');

        // Simulate loading
        setTimeout(() => {
            step3.classList.remove('active');
            step4.classList.add('active');
        }, 3000); // Adjust time as needed
    });
});
