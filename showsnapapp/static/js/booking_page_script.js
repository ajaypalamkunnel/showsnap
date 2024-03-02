const seats = document.querySelectorAll('.seat');
const count = document.getElementById('count');
const total = document.getElementById('total');
const selectedSeats = [];

// Update total and count
function updateSelectedCount() {
  count.innerText = selectedSeats.length;
  let totalPrice = 0;
  selectedSeats.forEach(seat => {
    totalPrice += seat.price;
  });
  total.innerText = totalPrice;
}

// Seat click event
seats.forEach(seat => {
  seat.addEventListener('click', () => {
    if (!seat.classList.contains('occupied')) {
      seat.classList.toggle('selected');
      const seatName = seat.dataset.seatName;
      const price = parseInt(seat.dataset.price);
      if (seat.classList.contains('selected')) {
        selectedSeats.push({ name: seatName, price: price });
      } else {
        const index = selectedSeats.findIndex(s => s.name === seatName);
        if (index !== -1) {
          selectedSeats.splice(index, 1);
        }
      }
      updateSelectedCount();
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
