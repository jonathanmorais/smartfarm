from flask import Flask, request, jsonify
from prometheus_client import Counter, Gauge, Histogram, generate_latest
import time
from datetime import datetime

app = Flask(__name__)

# Métricas Prometheus
sensor_requests_total = Counter('sensor_requests_total', 'Total sensor requests', ['device_id', 'status'])
umidade_analogica_gauge = Gauge('sensor_umidade_analogica', 'Umidade analógica', ['device_id'])
umidade_digital_gauge = Gauge('sensor_umidade_digital', 'Umidade digital', ['device_id'])
request_duration = Histogram('sensor_request_duration_seconds', 'Request duration')

# Storage em memória (para simplicidade)
sensor_data = []

@app.route('/')
def home():
    return {
        'status': 'online',
        'message': 'Sensor API com Prometheus',
        'endpoints': {
            'POST /sensor': 'Enviar dados do sensor',
            'GET /dados': 'Listar dados recentes',
            'GET /metrics': 'Métricas Prometheus'
        },
        'grafana': 'http://localhost:3000 (admin/admin123)',
        'prometheus': 'http://localhost:9090'
    }

@app.route('/sensor', methods=['POST'])
@request_duration.time()
def receive_data():
    """Recebe dados do sensor e atualiza métricas Prometheus"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        # Validação
        if not data or 'umidade_analogica' not in data or 'umidade_digital' not in data:
            sensor_requests_total.labels(device_id='unknown', status='error').inc()
            return jsonify({'error': 'Dados inválidos'}), 400
        
        umidade_analogica = int(data['umidade_analogica'])
        umidade_digital = int(data['umidade_digital'])
        device_id = data.get('device_id', 'unknown')
        
        # Salva dados (simples - em memória)
        sensor_data.append({
            'timestamp': datetime.now().isoformat(),
            'umidade_analogica': umidade_analogica,
            'umidade_digital': umidade_digital,
            'device_id': device_id,
            'ip': request.remote_addr
        })
        
        # Mantém apenas últimos 1000 registros
        if len(sensor_data) > 1000:
            sensor_data.pop(0)
        
        # Atualiza métricas Prometheus
        umidade_analogica_gauge.labels(device_id=device_id).set(umidade_analogica)
        umidade_digital_gauge.labels(device_id=device_id).set(umidade_digital)
        sensor_requests_total.labels(device_id=device_id, status='success').inc()
        
        print(f"📊 Métricas atualizadas: A={umidade_analogica}, D={umidade_digital}, Device={device_id}")
        
        return jsonify({
            'success': True,
            'message': 'Dados salvos e métricas atualizadas',
            'timestamp': datetime.now().isoformat(),
            'processing_time': round(time.time() - start_time, 3)
        })
        
    except Exception as e:
        sensor_requests_total.labels(device_id='unknown', status='error').inc()
        print(f"❌ Erro: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/dados')
def get_data():
    """Lista dados recentes (últimos 20)"""
    try:
        recent_data = sensor_data[-20:] if len(sensor_data) > 20 else sensor_data
        
        return jsonify({
            'success': True,
            'total_in_memory': len(sensor_data),
            'showing': len(recent_data),
            'dados': recent_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/metrics')
def metrics():
    """Endpoint para Prometheus coletar métricas"""
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'total_samples': len(sensor_data)
    })

if __name__ == '__main__':
    print("🚀 Iniciando Sensor API com Prometheus...")
    print("📊 Métricas em: http://localhost:5000/metrics")
    print("📈 Prometheus: http://localhost:9090")
    print("🎯 Grafana: http://localhost:3000 (admin/admin123)")
    
    app.run(host='0.0.0.0', port=5000, debug=False)