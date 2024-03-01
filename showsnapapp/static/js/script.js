// Automatically slide movie banners horizontally
let currentPosition = 0;
const slides = document.querySelectorAll('.movie-slide');

// Set initial position to show the last banner on the right side
document.querySelector('.movie-slider').style.transform = `translateX(-${slides[0].offsetWidth}px)`;

function slide() {
    currentPosition++;

    // Reset the slide position to the beginning after reaching the end
    if (currentPosition === slides.length) {
        currentPosition = 0;
    }
}

setInterval(slide, 3000); // Change slide every 3 seconds


