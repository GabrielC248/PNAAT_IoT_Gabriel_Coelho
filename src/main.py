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

# Variáveis para o Tratamento do Botão
button_flag = False
current_time = 0
last_time = 0

# Variáveis do Sistema
part_counter = 0

# Definição da Rotina de Interrupção do Botão
def button_isr_handler(pin):
    global button_flag, last_time, current_time
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_time) > DEBOUNCE_MS:
        button_flag = True
        last_time = current_time

# Configuração dos Pinos
reset_btn = machine.Pin(BUTTON_PIN, machine.Pin.IN)
ldr_digital = machine.Pin(LDR_DIGITAL_PIN, machine.Pin.IN)
ldr_analog = machine.ADC(machine.Pin(LDR_ANALOG_PIN))
ldr_analog.atten(machine.ADC.ATTN_11DB)

# Configuração da Interrupção do botão
reset_btn.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_isr_handler)

# Inicialização
print("Contador de Producao Inicializado")

# Loop Principal
while True:

    # Tratamento da Flag do Botão
    if button_flag:
        irq_state = machine.disable_irq()
        part_counter = 0
        button_flag = False
        print("Turno resetado com sucesso. Contadores zerados.")
        machine.enable_irq(irq_state)

    time.sleep_ms(10) # Pequeno atraso para evitar travamentos no simulador