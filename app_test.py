import requests
import time
import random
from datetime import datetime

def enviar(analogica, digital, device="sensor_001"):
    """Função simples para enviar dados"""
    dados = {
        "umidade_analogica": analogica,
        "umidade_digital": digital,
        "device_id": device
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/sensor",
            json=dados,
            timeout=5
        )
        
        if response.status_code == 200:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"✅ {timestamp} - Enviado: A={analogica}, D={digital}")
            return True
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro conexão: {e}")
        return False

def simular_sensor_realista():
    """Simula variações realistas de um sensor de umidade"""
    base_umidade = random.randint(300, 600)  # Umidade base
    variacao = random.randint(-50, 50)       # Variação pequena
    umidade = max(0, min(1023, base_umidade + variacao))  # Limita entre 0-1023
    
    # Digital baseado no analógico (threshold em 400)
    digital = 1 if umidade > 400 else 0
    
    return umidade, digital

def enviar_continuamente():
    """Envia dados continuamente simulando um sensor real"""
    print("🔄 Iniciando envio contínuo de dados...")
    print("⏹️  Pressione Ctrl+C para parar")
    print("-" * 40)
    
    contador = 0
    sucessos = 0
    
    try:
        while True:
            contador += 1
            
            # Simula leitura do sensor
            analogica, digital = simular_sensor_realista()
            
            # Envia dados
            if enviar(analogica, digital, f"sensor_continuo_{contador}"):
                sucessos += 1
            
            # Estatísticas a cada 10 envios
            if contador % 10 == 0:
                taxa_sucesso = (sucessos / contador) * 100
                print(f"📊 Stats: {contador} envios, {sucessos} sucessos ({taxa_sucesso:.1f}%)")
            
            # Aguarda 5 segundos (simula coleta real)
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Parado pelo usuário")
        print(f"📈 Total: {contador} envios, {sucessos} sucessos")

def enviar_lote_teste():
    """Envia um lote de dados de teste"""
    print("🧪 Enviando lote de teste...")
    
    dados_teste = [
        (250, 0, "sensor_seco"),
        (350, 0, "sensor_medio_seco"),
        (450, 1, "sensor_medio_umido"),
        (650, 1, "sensor_umido"),
        (800, 1, "sensor_muito_umido"),
    ]
    
    for i, (analogica, digital, device) in enumerate(dados_teste, 1):
        print(f"📤 Enviando {i}/{len(dados_teste)}...")
        enviar(analogica, digital, device)
        time.sleep(1)  # Pausa entre envios
    
    print("✅ Lote de teste concluído!")

def menu():
    """Menu interativo"""
    while True:
        print("\n" + "="*40)
        print("📡 ENVIADOR DE DADOS DO SENSOR")
        print("="*40)
        print("1. Enviar dados únicos")
        print("2. Enviar lote de teste")
        print("3. Enviar continuamente (simula sensor real)")
        print("4. Sair")
        
        opcao = input("\nEscolha (1-4): ").strip()
        
        if opcao == "1":
            try:
                analogica = int(input("Umidade analógica (0-1023): "))
                digital = int(input("Umidade digital (0 ou 1): "))
                device = input("Device ID (Enter para sensor_manual): ").strip() or "sensor_manual"
                enviar(analogica, digital, device)
            except ValueError:
                print("❌ Digite números válidos!")
        
        elif opcao == "2":
            enviar_lote_teste()
        
        elif opcao == "3":
            enviar_continuamente()
        
        elif opcao == "4":
            print("👋 Saindo...")
            break
        
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    menu()