const seats = document.querySelectorAll('.seat');
const selectedSeats = [];

// Seat click event
seats.forEach(seat => {
  seat.addEventListener('click', () => {
    if (!seat.classList.contains('booked')) {
      seat.classList.toggle('selected');
      const seatName = seat.textContent;
      const price = parseInt(seat.dataset.price);
      if (seat.classList.contains('selected')) {
        selectedSeats.push({ name: seatName, price: price });
      } else {
        const index = selectedSeats.findIndex(s => s.name === seatName);
        if (index !== -1) {
          selectedSeats.splice(index, 1);
        }
      }
      updateSelectedSeatsList();
    }
  });
});

// Update selected seats list
function updateSelectedSeatsList() {
  const selectedSeatsList = document.getElementById('selected-seats');
  selectedSeatsList.innerHTML = '';
  selectedSeats.forEach(seat => {
    const li = document.createElement('li');
    li.textContent = `Seat: ${seat.name}, Amount: ${seat.price}`;
    selectedSeatsList.appendChild(li);
  });
}
