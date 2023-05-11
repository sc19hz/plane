function renderFlightData(flight) {
  const flightInfo = document.createElement("div");
  flightInfo.classList.add("flight-info");
  flightInfo.innerHTML = `
    <h4>${flight.air_name}</h4>
    <p>Departure Time: ${flight.departure_time}</p>
    <p>Arrival Time: ${flight.arrival_time}</p>
  `;
  flightInfo.dataset.flight = JSON.stringify(flight);
  flightInfo.addEventListener("click", function () {
    const flightData = JSON.parse(this.dataset.flight);
    localStorage.setItem("selectedFlight", JSON.stringify(flightData));
    window.location.href = `/flight_detail/${flight.flight_id}`;
  });
  return flightInfo;
}




document.addEventListener("DOMContentLoaded", function () {
    const flightSearchForm = document.getElementById('flight-search-form');
    if (flightSearchForm) {
        flightSearchForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const departure_place = document.getElementById('departure_place').value;
            const destin_place = document.getElementById('destin_place').value;
            const departure_time = document.getElementById('departure_time').value;

            const queryParams = new URLSearchParams({
                departure_place,
                destin_place,
                departure_time
            });

            fetch(`/find_flight?${queryParams.toString()}`)
                .then(response => response.json())
.then(data => {
    console.log('Processed API response:', data);
    if (data.status === 200) {
        const flightResults = document.getElementById('flight-results');
        flightResults.innerHTML = ''; // 清空之前的搜索结果
        if (data.data && data.data.length > 0) {
            data.data.forEach(flight => {
                flightResults.appendChild(renderFlightData(flight));
            });
        } else {
            flightResults.innerHTML = '<p>No flights found.</p>';
        }

    } else if (data.status === 503) {
        alert('Flight search failed.');
    } else {
        alert('Unexpected error occurred.');
    }
})

    .catch(error => {
        console.error(error);
        alert('Error occurred while fetching flight data.');
    });
    });
  }
});


document.addEventListener('DOMContentLoaded', function() {
    // Your existing code goes here

    const cancelOrderBtn = document.getElementById('cancel-order-btn');
    if (cancelOrderBtn) {
        cancelOrderBtn.addEventListener('click', function() {
            const confirmation = confirm('Are you sure to delete this order?');
            if (confirmation) {
                const orderId = document.getElementById('order-id').textContent;
                const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

                fetch('/cancel_order/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ order_id: orderId })
                })
                .then(response => {
                    if (response.ok) {
                        alert('Order successfully canceled.');
                        window.location.href = '/order/';
                    } else {
                        alert('An error occurred while canceling the order. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while canceling the order. Please try again.');
                });
            }
        });
    }
});

