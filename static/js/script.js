window.onload = function() {
    // Any global initialization code goes here.
    // If you had some shared functionality across different pages, you could put it here.

    // Example: Menu scroll effect for sticky navigation or any global actions.
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.onscroll = function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-sticky');
            } else {
                navbar.classList.remove('navbar-sticky');
            }
        };
    }
};
