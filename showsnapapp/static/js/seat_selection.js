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
// Update selected seats list
function updateSelectedSeatsList() {
  const selectedSeatsInput = document.getElementById('selected-seats-input');
  const totalAmountInput = document.getElementById('total-amount-input');
  let selectedSeatsString = '';
  let totalPrice = 0;
  
  selectedSeats.forEach((seat, index) => {
    selectedSeatsString += seat.name;
    totalPrice += seat.price; // Accumulate the total price
    
    // If it's not the last seat, add a comma separator
    if (index < selectedSeats.length - 1) {
      selectedSeatsString += ',';
    }
  });
  
  // Set the selected seats string and total amount as the value of the input boxes
  selectedSeatsInput.value = selectedSeatsString;
  totalAmountInput.value = totalPrice;
}

