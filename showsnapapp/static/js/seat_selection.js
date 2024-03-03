const seats = document.querySelectorAll(".seat");
const selectedSeats = [];
// Seat click event
function selectSeat(seatName, screeningAmount) {
  seats.forEach((seat) => {
    seat.addEventListener("click", () => {
      if (!seat.classList.contains("booked")) {
        seat.classList.toggle("selected");
        const seatName = seat.textContent;
        if (seat.classList.contains("selected")) {
          selectedSeats.push({ name: seatName });
        } else {
          const index = selectedSeats.findIndex((s) => s.name === seatName);
          if (index !== -1) {
            selectedSeats.splice(index, 1);
          }
        }
        updateSelectedSeatsList();
      }
    });
  });

  // Update selected seats list and total amount
  function updateSelectedSeatsList() {
    const selectedSeatsInput = document.getElementById("selected-seats-input");
    const totalAmountInput = document.getElementById("total-amount-input");
    let selectedSeatsString = "";
    let totalPrice = 0;
    selectedSeats.forEach((seat) => {
      selectedSeatsString += `${seat.name}, `;
      totalPrice += parseInt(screeningAmount); // Use screening amount for each selected seat
    });
    // Set the selected seats string and total amount as the value of the input boxes
    selectedSeatsInput.value = selectedSeatsString.trim();
    totalAmountInput.value = totalPrice;
  }
}
