import machine
import time

# Constantes do Sistema
DEBOUNCE_MS = 500   # 500 milissegundos de debouncing
STOP_MS = 5000      # 5 segundos para alertar a micro-parada
LUX_THRESHOLD = 500 # Limiar de 500 lux para detecção do objeto

# Definição dos Pinos Utilizados
BUTTON_PIN = 25
LDR_DIGITAL_PIN = 26
LDR_ANALOG_PIN = 27

# Constantes Calculadas (gamma = 0.7 | rl10 = 50k | ADC = 0-4095)
LDR_RESISTANCE = 50000 * ((10.0 / LUX_THRESHOLD) ** 0.7)                  # Resistência variável do LDR
ADC_THRESHOLD = int((LDR_RESISTANCE / (LDR_RESISTANCE + 10000.0)) * 4095) # Limiar do ADC com base no limiar de lux definido

# Variáveis para o Tratamento do Botão
button_flag = False
current_time = 0
last_time = -DEBOUNCE_MS

# Variáveis do Sistema
part_counter = 0
part_detected = False
stop_time = 0
stop_flag = False

# Definição da Rotina de Interrupção do Botão
def button_isr_handler(pin):
    global button_flag, last_time, current_time
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_time) > DEBOUNCE_MS: # Se passou tempo suficiente desde o último aperto, seta a flag (debouncing)
        button_flag = True
        last_time = current_time

# Configuração dos Pinos
reset_btn = machine.Pin(BUTTON_PIN, machine.Pin.IN)
ldr_digital = machine.Pin(LDR_DIGITAL_PIN, machine.Pin.IN)
ldr_analog = machine.ADC(machine.Pin(LDR_ANALOG_PIN))
ldr_analog.atten(machine.ADC.ATTN_11DB)

# Configuração da Interrupção do botão
reset_btn.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_isr_handler) # botão com pull-up externo -> borda de descida (IRQ_FALLING)

# Inicialização
print('Contador de Producao Inicializado')

# Loop Principal
while True:

    time.sleep_ms(250) # Pequeno atraso para evitar travamentos no simulador

    # Lógica de Detecção de Objetos
    ldr_value = ldr_analog.read() # Leitura do valor analógico do LDR

    if ldr_value > ADC_THRESHOLD and not part_detected: # Se escureceu (valor do ADC sobe) e não há nenhuma peça detectada
        part_detected = True
        stop_flag = True
        stop_time = time.ticks_ms() # Marca o momento que a peça entrou

    if ldr_value < ADC_THRESHOLD and part_detected: # Se clareou (valor do ADC cai) e tinha uma peça passando
        part_counter = part_counter + 1
        part_detected = False
        stop_flag = False
        print(f"Peca detectada! Total: {part_counter}")

    if stop_flag and time.ticks_diff(time.ticks_ms(), stop_time) > STOP_MS: # Se tem uma peça bloqueando o sensor por mais tempo que o permitido
        stop_flag = False
        print('Alerta: Micro-parada detectada!')

    # Tratamento da Flag do Botão
    if button_flag:
        irq_state = machine.disable_irq() # Pausa as interrupções
        part_counter = 0
        stop_flag = False
        button_flag = False
        print("Turno resetado com sucesso. Contadores zerados.")
        machine.enable_irq(irq_state) # Habilita as interrupções novamente