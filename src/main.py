import machine
import time

# Constantes do Sistema
DEBOUNCE_MS = 50    # 50 milissegundos de debouncing
STOP_MS = 3000      # 3 segundos para alertar a micro-parada
LUX_THRESHOLD = 500 # Limiar de 500 lux para detecção do objeto

# Definição dos Pinos Utilizados
BUTTON_PIN = 25
LDR_DIGITAL_PIN = 26
LDR_ANALOG_PIN = 27

# Variáveis do Sistema
part_counter = 0

# Configuração dos Pinos
reset_btn = machine.Pin(BUTTON_PIN, machine.Pin.IN)
ldr_digital = machine.Pin(LDR_DIGITAL_PIN, machine.Pin.IN)
ldr_analog = machine.ADC(machine.Pin(LDR_ANALOG_PIN))
ldr_analog.atten(machine.ADC.ATTN_11DB)

# Inicialização
print("Contador de Producao Inicializado")

# Loop Principal
while True:
    time.sleep_ms(10) # Pequeno atraso para evitar travamentos no simulador