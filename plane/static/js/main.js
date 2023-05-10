document.getElementById('flight-search-form').addEventListener('submit', function (event) {
  event.preventDefault();

  const departure = document.getElementById('departure').value;
  const arrival = document.getElementById('arrival').value;
  const date = document.getElementById('date').value;

  const requestData = {
    departure: departure,
    arrival: arrival,
    date: date
  };

  axios.get('/findflight', {
    params: requestData
  })
  .then(function (response) {
    if (response.status === 200) {
      console.log('Query successful');
    } else if (response.status === 503) {
      console.log('Query failed');
    }
  })
  .catch(function (error) {
    console.log('Error:', error);
  });
});
