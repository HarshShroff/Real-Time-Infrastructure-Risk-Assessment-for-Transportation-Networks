# Real-Time Infrastructure Risk Assessment for Transportation Networks

![Screenshot of the application](static/imgs/overview.png)

## Overview

This project is a web-based application designed to assess and visualize real-time risks to transportation infrastructure within a specified geographic area. It integrates data from multiple sources, including OpenStreetMap, OpenWeatherMap, and TomTom Traffic API, to provide a dynamic risk assessment based on factors like traffic congestion, weather conditions, and infrastructure characteristics.

## Key Features

- **Real-Time Risk Assessment:** Calculates a risk score for each infrastructure point based on current conditions.
- **Interactive Map Visualization:** Displays infrastructure on a map with color-coded markers representing risk levels.
- **Data Integration:** Combines data from OpenStreetMap (infrastructure), OpenWeatherMap (weather), and TomTom (traffic).
- **Filtering and Sorting:** Allows users to filter infrastructure by risk level and sort by name, risk score, or type.
- **Modern User Interface:** Utilizes a clean and responsive design for optimal user experience.
- **Scalable Architecture:** Designed to accommodate additional data sources and risk factors.

## Technologies Used

### Frontend:
- HTML5
- CSS3
- JavaScript
- Leaflet (for map visualization)

### Backend:
- Python
- Flask (web framework)

### Data Sources:
- OpenStreetMap (via Overpass API)
- OpenWeatherMap API
- TomTom Traffic API

### Database:
- PostgreSQL with PostGIS (for spatial data management)

### Other:
- dotenv (for managing environment variables)
- overpy (Python Overpass API wrapper library)

## Setup and Installation

### 1. Clone the Repository
```sh
git clone https://github.com/HarshShroff/Real-Time-Infrastructure-Risk-Assessment-for-Transportation-Networks/tree/main
cd Real-Time-Infrastructure-Risk-Assessment-for-Transportation-Networks
```

### 2. Create a Virtual Environment (Recommended)
```sh
python -m venv <venv_name>
source venv/bin/activate  # On Linux and macOS
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

1. Create a `.env` file in the root directory.
2. Add the following variables with your API keys and database credentials:

```sh
OPENWEATHER_API_KEY=your_openweathermap_api_key
TOMTOM_API_KEY=your_tomtom_api_key

# PostgreSQL credentials
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_username
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=your_db_host
POSTGRES_PORT=your_db_port
```

### 5. Set Up the PostgreSQL Database

- Create a PostgreSQL database with PostGIS extension enabled.
- Update the `.env` file with your database credentials.
- Optionally, you can provide an SQL schema file (if available) to initialize the tables.

### 6. Run the Application
```sh
python app.py
```
- The application will start running at `http://127.0.0.1:5001/`.

## Usage

1. Open the application in your web browser.
2. Enter a city name and radius in the search form.
3. Click "Search" to display infrastructure points on the map.
4. View risk assessments by hovering over map markers.
5. Filter and sort the results using the controls above the results list.

## Project Structure

```
├── app.py                           # Flask application
├── infrastructure_monitor.py        # Risk assessment logic and data integration
├── requirements.txt                 # Project dependencies
├── README.md                        # Project documentation (this file)
├── .env                             # Environment variables
├── static/
│   ├── css/
│   │   └── style.css                # CSS styles
│   └── js/
│       └── main.js                  # JavaScript logic
└── templates/
    └── index.html                   # HTML template
```

## Future Enhancements

- **Additional Data Sources:** Integrate more real-time data sources, such as seismic activity or flood sensors.
- **Predictive Modeling:** Implement machine learning models to forecast future risk levels based on historical data.
- **Alerting System:** Develop an alerting system to notify stakeholders when risk levels exceed certain thresholds.
- **Expanded Infrastructure Types:** Support additional infrastructure types, such as power grids or water pipelines.
- **User Authentication and Authorization:** Implement user accounts with different roles and permissions.
- **Mobile App Development:** Create native mobile apps for iOS and Android platforms.

## Credits

This project was created by **Harsh Shroff** _[LinkedIn](https://www.linkedin.com/in/harshroff/)_.

- Utilizes data from OpenStreetMap, OpenWeatherMap, and TomTom Traffic API.
- Uses Leaflet for interactive map visualizations.
- Flask for the web framework.

## License

```plaintext
MIT License

Copyright (c) [Year] [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
