from flask import Flask, render_template, request, jsonify
from infrastructure_monitor import InfrastructureRiskMonitor
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        city = request.form.get('city', 'Washington, DC')
        radius = float(request.form.get('radius', 5.0))
        
        # Initialize monitor with real infrastructure data
        monitor = InfrastructureRiskMonitor(city=city, radius_km=radius)
        infrastructure_data = []
        
        # Get infrastructure data and calculate risk for each
        for location in monitor.infrastructure_locations:
            risk_score, risk_factors = monitor.calculate_risk_score(location['id'])
            infrastructure_data.append({
                'id': location['id'],
                'name': location['name'],
                'type': location['type'],
                'latitude': location['latitude'],
                'longitude': location['longitude'],
                'risk_score': risk_score,
                'risk_factors': risk_factors
            })
        
        return jsonify({
            'success': True,
            'center': monitor.city_center,
            'infrastructure': infrastructure_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001) # to run it on local
    # app.run(debug=True, host='0.0.0.0', port=5001)