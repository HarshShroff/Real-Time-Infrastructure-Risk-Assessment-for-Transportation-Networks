import requests
import json
import numpy as np
from typing import Dict, List, Tuple
import overpy
import psycopg2
import time
from dotenv import load_dotenv
import os

class InfrastructureRiskMonitor:
    def __init__(self, city: str = "Washington, DC", radius_km: float = 5.0):
        load_dotenv()
        self.city = city
        self.radius_km = radius_km
        self.city_center = self.get_city_coordinates(city)
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.tomtom_api_key = os.getenv('TOMTOM_API_KEY')
        self.db_params = {
            'dbname': os.getenv('POSTGRES_DB'),
            'user': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'host': os.getenv('POSTGRES_HOST'),
            'port': os.getenv('POSTGRES_PORT')
        }
        self.infrastructure_locations = self.get_osm_infrastructure()

    def get_city_coordinates(self, city: str) -> Tuple[float, float]:
        try:
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': city,
                'format': 'json',
                'limit': 1,
                'featuretype': 'city'
            }
            headers = {
                'User-Agent': 'InfrastructureMonitor/1.0',
                'Accept': 'application/json'
            }
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                print(f"Found coordinates for {city}: {lat}, {lon}")
                return lat, lon
            return 38.8977, -77.0365
        except Exception as e:
            print(f"Error getting city coordinates: {e}")
            return 38.8977, -77.0365

    def get_weather_data(self, lat: float, lon: float) -> Dict:
        """Get weather data from OpenWeatherMap API"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'weather': data['weather'][0]['main']
                }
            return {'temperature': 20, 'humidity': 50, 'weather': 'Clear'}
        except Exception as e:
            print(f"Weather API error: {e}")
            return {'temperature': 20, 'humidity': 50, 'weather': 'Clear'}

    def get_traffic_data(self, lat: float, lon: float) -> Dict:
        """Get traffic data from TomTom API"""
        try:
            url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
            params = {
                'key': self.tomtom_api_key,
                'point': f"{lat},{lon}",
                'unit': 'MPH'
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'congestion': data.get('flowSegmentData', {}).get('currentSpeed', 0) / 
                                 data.get('flowSegmentData', {}).get('freeFlowSpeed', 1),
                    'confidence': data.get('flowSegmentData', {}).get('confidence', 0)
                }
            return {'congestion': 0.5, 'confidence': 0.5}
        except Exception as e:
            print(f"Traffic API error: {e}")
            return {'congestion': 0.5, 'confidence': 0.5}
        
    def get_osm_infrastructure(self) -> List[Dict]:
        """Get infrastructure data from OpenStreetMap using Overpass API"""
        max_retries = 3
        base_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    time.p(base_delay * (attempt + 1))
                
                api = overpy.Overpass()
                lat, lon = self.city_center
                radius = self.radius_km * 1000  # Convert to meters
                
                # Modified query with proper node resolution
                query = f"""
                    [out:json][timeout:90];
                    area[name="{self.city}"]->.searchArea;
                    (
                        way["highway"="primary"](around:{radius},{lat},{lon});
                        way["highway"="secondary"](around:{radius},{lat},{lon});
                        way["bridge"="yes"](around:{radius},{lat},{lon});
                        node["railway"="station"](around:{radius},{lat},{lon});
                    );
                    (._;>;);  // Get all nodes for ways
                    out body;
                    out skel qt;
                """
                
                # If the area-based query fails, fall back to a simpler query
                try:
                    result = api.query(query)
                except:
                    fallback_query = f"""
                        [out:json][timeout:90];
                        (
                            node["railway"="station"](around:{radius},{lat},{lon});
                            way["highway"="primary"](around:{radius},{lat},{lon});
                            way["highway"="secondary"](around:{radius},{lat},{lon});
                            way["bridge"="yes"](around:{radius},{lat},{lon});
                        );
                        (._;>;);
                        out body;
                        out skel qt;
                    """
                    result = api.query(fallback_query)
                
                infrastructure_list = []
                seen_names = set()  # To avoid duplicates
                
                # Process ways (roads, bridges)
                for way in result.ways:
                    try:
                        # Calculate center point
                        center_lat = sum(float(node.lat) for node in way.nodes) / len(way.nodes)
                        center_lon = sum(float(node.lon) for node in way.nodes) / len(way.nodes)
                        
                        # Determine infrastructure type
                        if "bridge" in way.tags and way.tags["bridge"] == "yes":
                            infra_type = "bridge"
                        elif "highway" in way.tags:
                            infra_type = "road"
                        else:
                            continue
                        
                        # Get name or generate one
                        name = way.tags.get("name", f"{infra_type.title()} {len(infrastructure_list) + 1}")
                        
                        # Avoid duplicates
                        if name in seen_names:
                            continue
                        seen_names.add(name)
                        
                        infrastructure_list.append({
                            "id": len(infrastructure_list) + 1,
                            "name": name,
                            "type": infra_type,
                            "latitude": center_lat,
                            "longitude": center_lon,
                            "tags": dict(way.tags)  # Store additional metadata
                        })
                    except Exception as e:
                        print(f"Error processing way: {e}")
                        continue
                
                # Process nodes (railway stations)
                for node in result.nodes:
                    try:
                        if "railway" in node.tags and node.tags["railway"] == "station":
                            name = node.tags.get("name", f"Station {len(infrastructure_list) + 1}")
                            
                            # Avoid duplicates
                            if name in seen_names:
                                continue
                            seen_names.add(name)
                            
                            infrastructure_list.append({
                                "id": len(infrastructure_list) + 1,
                                "name": name,
                                "type": "railway_station",
                                "latitude": float(node.lat),
                                "longitude": float(node.lon),
                                "tags": dict(node.tags)  # Store additional metadata
                            })
                    except Exception as e:
                        print(f"Error processing node: {e}")
                        continue
                
                if not infrastructure_list:
                    print("No infrastructure found, generating sample data...")
                    return []
                    
                print(f"Found {len(infrastructure_list)} infrastructure points")
                return infrastructure_list
                
            except overpy.exception.OverpassTooManyRequests:
                print(f"Server busy, retrying in {base_delay * (attempt + 1)} seconds...")
                continue
            except Exception as e:
                print(f"Error fetching OSM data: {e}")
                if attempt == max_retries - 1:
                    return []
                
    def fetch_infrastructure_locations(self) -> List[Dict]:
        """Fetch real infrastructure locations using Overpass API"""
        try:
            api = overpy.Overpass()
            infrastructure_list = []  # Will store the infrastructure data
            
            # Get infrastructure from OpenStreetMap
            infrastructure_data = self.get_osm_infrastructure()
            
            # Insert infrastructure into database and get IDs
            with psycopg2.connect(**self.db_params) as conn:
                with conn.cursor() as cur:
                    for infra in infrastructure_data:
                        # Check if infrastructure already exists
                        cur.execute("""
                            SELECT id FROM infrastructure 
                            WHERE name = %s AND ST_DWithin(
                                geometry,
                                ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                                0.001
                            )
                        """, (infra['name'], infra['longitude'], infra['latitude']))
                        
                        result = cur.fetchone()
                        if result:
                            infra['id'] = result[0]
                        else:
                            # Insert new infrastructure
                            cur.execute("""
                                INSERT INTO infrastructure (name, type, geometry)
                                VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                                RETURNING id
                            """, (
                                infra['name'],
                                infra['type'],
                                infra['longitude'],
                                infra['latitude']
                            ))
                            infra['id'] = cur.fetchone()[0]
                        
                        infrastructure_list.append(infra)
                    
                    conn.commit()
            
            return infrastructure_list
                    
        except Exception as e:
            print(f"Error fetching infrastructure locations: {e}")
            return []

    def calculate_risk_score(self, infrastructure_id: int) -> Tuple[float, Dict]:
        """Calculate risk score for infrastructure"""
        infra = next((i for i in self.infrastructure_locations if i['id'] == infrastructure_id), None)
        if not infra:
            return 0.5, {}
        
        # Get real-time data
        traffic = self.get_traffic_data(infra['latitude'], infra['longitude'])
        weather = self.get_weather_data(infra['latitude'], infra['longitude'])
        
        # Calculate risk factors
        risk_factors = {
            'traffic_congestion': traffic['congestion'],
            'weather_condition': 0.5 if weather['weather'] == 'Clear' else 0.8,
            'infrastructure_age': np.random.uniform(0.3, 0.7)  # Simulated
        }
        
        # Calculate total risk score
        total_risk = sum(risk_factors.values()) / len(risk_factors)
        
        return total_risk, risk_factors

    def update_search_parameters(self, city: str, radius: float):
        self.city = city
        self.radius_km = radius
        self.city_center = self.get_city_coordinates(city)
        self.infrastructure_locations = self.get_osm_infrastructure()

    def update_risk_assessments(self) -> List[Dict]:
        updated_data = []
        for infra in self.infrastructure_locations:
            risk_score, risk_factors = self.calculate_risk_score(infra['id'])
            updated_data.append({
                'id': infra['id'],
                'name': infra['name'],
                'risk_score': risk_score,
                'risk_factors': risk_factors
            })
        return updated_data
