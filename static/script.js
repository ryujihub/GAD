// Toggle Mobile Menu
const menuBtn = document.getElementById('mobile-menu-btn');
const navMenu = document.getElementById('nav-menu');
const menuIcon = document.getElementById('menu-icon');

menuBtn.addEventListener('click', () => {
    navMenu.classList.toggle('hidden');
    navMenu.classList.toggle('mobile-menu-active');
            
    // Toggle icon between bars and X
    if (navMenu.classList.contains('hidden')) {
        menuIcon.classList.replace('fa-times', 'fa-bars');
    } else {
        menuIcon.classList.replace('fa-bars', 'fa-times');
    }
});

// Handle Dropdowns on Mobile
const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
const dropdownSubToggles = document.querySelectorAll('.dropdown-toggle-sub');

dropdownToggles.forEach(toggle => {
    toggle.addEventListener('click', (e) => {
        if (window.innerWidth < 1024) {
            e.preventDefault();
            const submenu = toggle.nextElementSibling;
            submenu.classList.toggle('hidden');
            // Optional: Rotate arrow
            toggle.querySelector('i').classList.toggle('rotate-180');
        }
    });
});

dropdownSubToggles.forEach(toggle => {
    toggle.addEventListener('click', (e) => {
        if (window.innerWidth < 1024) {
            e.preventDefault();
            const submenu = toggle.nextElementSibling;
            submenu.classList.toggle('hidden');
        }
    });
});