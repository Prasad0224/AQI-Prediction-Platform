const API = "http://127.0.0.1:5000";
let chart;

const stateSelect = document.getElementById("state");
const citySelect = document.getElementById("city");
const predictBtn = document.getElementById("predictBtn");

const aqiValue = document.getElementById("aqiValue");
const aqiStatus = document.getElementById("aqiStatus");

const forecastValue = document.getElementById("forecastValue");
const forecastStatus = document.getElementById("forecastStatus");

const weatherValue = document.getElementById("weatherValue");

window.onload = () => loadStates();

predictBtn.addEventListener("click", getAQI);
stateSelect.addEventListener("change", loadCities);

function loadStates(){
    fetch(API + "/states")
    .then(res => res.json())
    .then(data => {
        stateSelect.innerHTML = "";
        data.forEach(x => stateSelect.innerHTML += `<option>${x}</option>`);
        loadCities();
    });
}

function loadCities(){
    let state = stateSelect.value;
    fetch(API + "/cities/" + state)
    .then(res => res.json())
    .then(data => {
        citySelect.innerHTML = "";
        data.forEach(x => citySelect.innerHTML += `<option>${x}</option>`);
    });
}

function getAQI(){
    aqiValue.innerText = "Loading...";
    forecastValue.innerText = "Loading...";
    weatherValue.innerText = "Loading...";
    aqiStatus.innerText = "";
    forecastStatus.innerText = "";

    let city = citySelect.value;

    fetch(API + "/predict/" + city)
    .then(res => res.json())
    .then(data => {
        const aqi = data.predicted_AQI;
        aqiValue.innerText = aqi;

        let status = getAQIStatus(aqi);
        aqiStatus.innerText = status.text;
        aqiStatus.style.color = status.color;

        weatherValue.innerText =
          `${data.weather.temperature}°C | Humidity ${data.weather.humidity}% | Wind ${data.weather.wind_speed} km/h`;

        return fetch(API + "/history/" + city);
    })
    .then(res => res.json())
    .then(data => {
        drawChart(data.timestamps, data.aqi_values);
        return fetch(API + "/forecast/" + city);
    })
    .then(res => res.json())
    .then(data => {
        const nextAQI = data.next_hour_AQI;
        forecastValue.innerText = nextAQI;

        let status = getAQIStatus(nextAQI);
        forecastStatus.innerText = status.text;
        forecastStatus.style.color = status.color;
    });
}

function drawChart(labels, values){
    const ctx = document.getElementById("aqiChart");
    if(chart) chart.destroy();

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: "AQI History",
                data: values,
                borderColor: "#00c6ff",
                borderWidth: 2,
                tension: 0.3,
                fill: false
            }]
        },
        options:{
            responsive:true,
            plugins:{
                legend:{labels:{color:"white"}}
            },
            scales:{
                x:{ticks:{color:"white"}},
                y:{ticks:{color:"white"}}
            }
        }
    });
}

function getAQIStatus(aqi){
    if(aqi <= 50) return {text:"Good 😊", color:"#00e400"};
    if(aqi <=100) return {text:"Moderate 🙂", color:"#ffff00"};
    if(aqi <=200) return {text:"Unhealthy 😷", color:"#ff7e00"};
    if(aqi <=300) return {text:"Very Unhealthy ☠️", color:"#ff0000"};
    return {text:"Hazardous ☢️", color:"#8f3f97"};
}