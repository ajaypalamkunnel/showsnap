let selectedSeats = [];
let totalAmount = 0;

function selectSeat(seatName, price) {
    const seatIndex = selectedSeats.indexOf(seatName);
    if (seatIndex !== -1) {
        // If seat is already selected, remove it
        selectedSeats.splice(seatIndex, 1);
        totalAmount -= price;
        document.getElementById('selected-seats-input').value = selectedSeats.join(',');
        document.getElementById('total-amount').innerText = totalAmount.toFixed(2);
    } else {
        // If seat is not selected, add it
        selectedSeats.push(seatName);
        totalAmount += price;
        document.getElementById('selected-seats-input').value = selectedSeats.join(',');
        document.getElementById('total-amount').innerText = totalAmount.toFixed(2);
    }
}

// Additional JavaScript code for seat selection can be added here
