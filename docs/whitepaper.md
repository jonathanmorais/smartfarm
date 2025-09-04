# Cálculos Meteorológicos para Sistema de Irrigação Inteligente

## 📋 Resumo

Este documento detalha os cálculos meteorológicos e de umidade utilizados no sistema de irrigação inteligente, fornecendo as bases científicas para as decisões automatizadas de irrigação baseadas em dados de sensores.

---

## 🌡️ 1. Evapotranspiração Potencial (ET₀)s

### **Definição:**
A evapotranspiração potencial é a quantidade máxima de água que pode ser perdida pela evaporação do solo e transpiração das plantas em condições ideais.

### **Fórmula Simplificada (Penman-Monteith Adaptada):**

```
ET₀ = 0.0023 × (T + 17.8) × √|100 - RH| × (FL + FUV)
```

**Onde:**
- **ET₀** = Evapotranspiração potencial (mm/dia)
- **T** = Temperatura do ar (°C)
- **RH** = Umidade relativa do ar (%)
- **FL** = Fator de luminosidade (0-1): `Luminosidade / 1023`
- **FUV** = Fator UV (0-1): `Intensidade_UV / 1023`

### **Interpretação:**
- **ET₀ < 3 mm/dia**: Demanda hídrica baixa
- **ET₀ 3-6 mm/dia**: Demanda moderada
- **ET₀ > 6 mm/dia**: Demanda alta (irrigação provável)

### **Implementação Arduino:**
```cpp
float calcular_ET0(float temp, float umidade, int luz, int uv) {
    float fator_luz = luz / 1023.0;
    float fator_uv = uv / 1023.0;
    
    return 0.0023 * (temp + 17.8) * 
           sqrt(abs(100 - umidade)) * 
           (fator_luz + fator_uv);
}
```

---

## 💨 2. Déficit de Pressão de Vapor (VPD)

### **Definição:**
O VPD indica o potencial da atmosfera para extrair água das plantas. Valores altos indicam stress hídrico.

### **Fórmulas:**

#### **Pressão de Vapor Saturado (es):**
```
es = 0.6108 × exp(17.27 × T / (T + 237.3))
```

#### **Pressão de Vapor Atual (ea):**
```
ea = es × (RH / 100)
```

#### **Déficit de Pressão de Vapor:**
```
VPD = es - ea
```

**Onde:**
- **es** = Pressão de vapor saturado (kPa)
- **ea** = Pressão de vapor atual (kPa)
- **VPD** = Déficit de pressão de vapor (kPa)
- **T** = Temperatura (°C)
- **RH** = Umidade relativa (%)

### **Interpretação:**
- **VPD < 0.5 kPa**: Sem stress hídrico
- **VPD 0.5-1.5 kPa**: Stress moderado
- **VPD > 1.5 kPa**: Stress alto (irrigação necessária)

### **Implementação Arduino:**
```cpp
float calcular_VPD(float temp, float umidade) {
    // Pressão de vapor saturado
    float es = 0.6108 * exp(17.27 * temp / (temp + 237.3));
    
    // Pressão de vapor atual
    float ea = es * umidade / 100.0;
    
    // Déficit de pressão de vapor
    return es - ea;
}
```

---

## 🌾 3. Índice de Stress Hídrico (ISH)

### **Definição:**
Índice composto que combina múltiplos fatores para quantificar o stress hídrico das plantas em uma escala 0-100.

### **Fórmula:**
```
ISH = (W × 40) + (VPD × 10) + (ET₀ × 5) + (ΔT × 2)
```

**Onde:**
- **W** = Índice de umidade do solo: `(1023 - Umidade_Solo) / 1023`
- **VPD** = Déficit de pressão de vapor (kPa)
- **ET₀** = Evapotranspiração potencial (mm/dia)
- **ΔT** = Excesso de temperatura: `max(0, Temperatura - 20)`

### **Pesos dos Fatores:**
- **Umidade Solo (40%)**: Fator mais importante
- **VPD (25%)**: Demanda atmosférica
- **ET₀ (20%)**: Perda de água potencial
- **Temperatura (15%)**: Stress térmico adicional

### **Interpretação:**
- **ISH < 30**: Sem necessidade de irrigação
- **ISH 30-50**: Monitorar condições
- **ISH 50-70**: Considerar irrigação
- **ISH > 70**: Irrigação urgente

### **Implementação Arduino:**
```cpp
float calcular_stress_hidrico(int umidade_solo, float temp, 
                             float umidade_ar, int luz, int uv) {
    // Fator umidade do solo (0-1)
    float w = (1023.0 - umidade_solo) / 1023.0;
    
    // Calcular VPD
    float vpd = calcular_VPD(temp, umidade_ar);
    
    // Calcular ET0
    float et0 = calcular_ET0(temp, umidade_ar, luz, uv);
    
    // Excesso de temperatura
    float delta_t = max(0.0, temp - 20.0);
    
    // Índice de stress hídrico
    float ish = (w * 40) + (vpd * 10) + (et0 * 5) + (delta_t * 2);
    
    return constrain(ish, 0, 100);
}
```

---

## 💧 4. Análise da Umidade do Solo

### **Conversão Sensor Analógico:**

#### **Fórmula de Calibração:**
```
Umidade_% = 100 × (Valor_Max - Leitura) / (Valor_Max - Valor_Min)
```

**Valores típicos HD-38:**
- **Valor_Min** = 300 (ar seco)
- **Valor_Max** = 950 (água)
- **Leitura** = Valor atual do sensor (0-1023)

#### **Classificação por Umidade:**
- **< 300**: Solo extremamente seco (0-10%)
- **300-450**: Solo seco (10-30%)
- **450-650**: Solo moderado (30-60%)
- **650-800**: Solo úmido (60-85%)
- **> 800**: Solo saturado (85-100%)

### **Implementação Arduino:**
```cpp
float converter_umidade_percentual(int leitura) {
    const int VALOR_SECO = 300;
    const int VALOR_UMIDO = 950;
    
    if (leitura < VALOR_SECO) return 0;
    if (leitura > VALOR_UMIDO) return 100;
    
    return 100.0 * (VALOR_UMIDO - leitura) / (VALOR_UMIDO - VALOR_SECO);
}

String classificar_umidade(int leitura) {
    if (leitura < 300) return "Extremamente Seco";
    if (leitura < 450) return "Seco";
    if (leitura < 650) return "Moderado";
    if (leitura < 800) return "Úmido";
    return "Saturado";
}
```

---

## ☀️ 5. Análise de Fatores Ambientais

### **Índice UV:**
```
Índice_UV = (Leitura_UV / 1023) × 15
```

**Interpretação:**
- **0-2**: Baixo
- **3-5**: Moderado  
- **6-7**: Alto
- **8-10**: Muito Alto
- **>11**: Extremo

### **Intensidade Luminosa:**
```
Intensidade_% = (Leitura_LDR / 1023) × 100
```

**Correlação com irrigação:**
- **> 80%**: Sol forte → Aumenta ET₀
- **50-80%**: Sol moderado → ET₀ normal
- **< 50%**: Nublado → Reduz ET₀

### **Material Particulado:**
```
PM2.5_μg/m³ = Leitura_Analog × Fator_Calibração
```

**Impacto na irrigação:**
- **> 100 μg/m³**: Pode reduzir fotossíntese
- **> 200 μg/m³**: Stress adicional nas plantas

---

## 🧮 6. Algoritmo de Decisão Integrado

### **Score Final de Irrigação:**
```
Score = (Peso_Solo × F_Solo) + (Peso_Clima × F_Clima) + 
        (Peso_Tempo × F_Tempo) + (Peso_Crítico × F_Crítico)
```

### **Fatores e Pesos:**

#### **Fator Solo (40%):**
```
F_Solo = (1023 - Umidade_Solo) / 1023
```

#### **Fator Climático (30%):**
```
F_Clima = (VPD/3 + ET₀/8 + (Temp-20)/20) / 3
```

#### **Fator Temporal (20%):**
```
F_Tempo = Modificador baseado em hora do dia e estação
```

#### **Fator Crítico (10%):**
```
F_Crítico = 1 se ISH > 70, senão 0
```

### **Decisão Final:**
```cpp
bool decidir_irrigacao(float score, unsigned long ultima_irrigacao) {
    // Verificar intervalo mínimo (30 minutos)
    if (millis() - ultima_irrigacao < 1800000) {
        return false;
    }
    
    // Thresholds adaptativos
    float threshold_normal = 0.6;
    float threshold_critico = 0.4;
    
    // Hora do dia (evitar irrigação noturna)
    int hora = obter_hora_atual();
    if (hora < 6 || hora > 20) {
        threshold_normal += 0.2;
    }
    
    return score > threshold_normal || 
           (score > threshold_critico && condicao_critica());
}
```

---

## 📊 7. Validação e Calibração

### **Métricas de Performance:**
- **Eficiência Hídrica**: L água / kg produto
- **Precisão**: % decisões corretas
- **Recall**: % necessidades atendidas

### **Calibração de Campo:**
1. **Coletar dados** por 2-4 semanas
2. **Comparar** com decisões manuais
3. **Ajustar pesos** dos fatores
4. **Validar** em diferentes condições

### **Monitoramento Contínuo:**
```cpp
void log_decisao(bool irrigou, float score, float ish) {
    Serial.print("Decisão: ");
    Serial.print(irrigou ? "IRRIGAR" : "NÃO IRRIGAR");
    Serial.print(" | Score: ");
    Serial.print(score);
    Serial.print(" | ISH: ");
    Serial.println(ish);
}
```

---

## 🎯 8. Implementação Prática

### **Frequência de Cálculos:**
- **Leituras**: A cada 1 minuto
- **Cálculos**: A cada 5 minutos
- **Decisões**: A cada 15 minutos
- **Logs**: A cada decisão

### **Otimizações Arduino:**
- Usar `float` apenas quando necessário
- Cache de cálculos pesados
- Implementar lookup tables para `exp()`

### **Exemplo Completo:**
```cpp
void loop() {
    // Ler sensores
    DadosMeteorologicos dados = ler_sensores();
    
    // Calcular variáveis derivadas
    dados.et0 = calcular_ET0(dados.temp, dados.umidade_ar, 
                            dados.luz, dados.uv);
    dados.vpd = calcular_VPD(dados.temp, dados.umidade_ar);
    dados.ish = calcular_stress_hidrico(dados.umidade_solo, 
                                       dados.temp, dados.umidade_ar,
                                       dados.luz, dados.uv);
    
    // Decidir irrigação
    float score = calcular_score_irrigacao(dados);
    bool irrigar = decidir_irrigacao(score, ultima_irrigacao);
    
    if (irrigar) {
        executar_irrigacao();
        log_decisao(true, score, dados.ish);
    }
    
    delay(60000); // 1 minuto
}
```


*Documento versão 1.0 - Sistema de Irrigação Inteligente*