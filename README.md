# Contador de Produção Não-Intrusivo

Este arquivo contém o relatório final do desafio técnico para o processo seletivo do PNAAT, detalhando as decisões de arquitetura, hardware e software do projeto embarcado desenvolvido no ambiente Wokwi.

---

## Identificação do Candidato

- **Nome completo:** Gabriel Cavalcanti Coelho
- **GitHub:** https://github.com/GabrielC248

---

## Visão Geral da Solução

O projeto consiste no desenvolvimento de um sistema embarcado para realizar a contagem não intrusiva de peças em uma linha de produção utilizando um microcontrolador ESP32 e um sensor óptico baseado em LDR. A solução foi implementada em MicroPython e simulada na plataforma Wokwi.

O princípio de funcionamento baseia-se na variação da luminosidade incidente sobre o sensor. Enquanto o ambiente permanece iluminado, o sistema entende que não há nenhuma peça sobre o sensor. Quando uma peça interrompe a iluminação, ocorre uma mudança no valor lido pelo LDR, permitindo identificar a presença do objeto. A contagem é realizada somente após a peça deixar a região de detecção, evitando múltiplas contagens para um mesmo objeto.

Além da contagem de produção, o sistema monitora possíveis micro-paradas da esteira. Caso o sensor permaneça obstruído por um período superior ao tempo configurado, o firmware identifica essa condição e informa o operador através da interface serial.

Também foi implementado um botão de reset responsável por reiniciar os contadores do turno, utilizando tratamento de debounce para evitar acionamentos múltiplos decorrentes das oscilações mecânicas do botão.

Toda a interação do usuário ocorre através do monitor serial, onde são exibidas as mensagens de inicialização, contagem de peças, detecção de micro-paradas e confirmação do reset do turno.

---

## Arquitetura do Sistema Embarcado

A aplicação foi desenvolvida utilizando uma interrupção para tratar o "pressionar" do botão e o laço principal para executar as leituras e a lógica do sistema de forma periódica e não bloqueante. Foi feita a parametrização do tempo de debounce, do tempo para a micro-parada, do limiar de lux para a detecção dos objetos e dos pinos conectados, facilitando a reutilização do código.

A estrutura geral pode ser representada pelo fluxo abaixo:

```text
          Inicialização
                │
                ▼
     Configuração dos pinos
                │
                ▼
   Configuração da interrupção
            do botão
                │
                ▼
    Mensagem de inicialização
                │
                ▼
┌───────────────────────────────┐
│        Loop Principal         │
│                               │
│   • Lê o sensor LDR           │
│   • Detecta entrada da peça   │
│   • Detecta saída da peça     │
│   • Incrementa contador       │
│   • Verifica micro-paradas    │
│   • Trata o reset do botão    │
└───────────────────────────────┘
```

## Fluxo do `main.py`

Durante a inicialização, o firmware configura todos os periféricos necessários:

- configuração do botão de reset;
- configuração do conversor ADC para leitura do LDR;
- configuração da interrupção externa do botão;
- cálculo do limiar de detecção utilizado pelo ADC;
- inicialização das variáveis de controle.

Após essa etapa, o programa permanece executando continuamente o laço principal.

Dentro do laço são realizadas quatro tarefas principais:

1. tratamento da solicitação de reset;
2. leitura do sensor óptico;
3. detecção da passagem de peças;
4. monitoramento de micro-paradas.

O comportamento do sistema é controlado através de variáveis booleanas que representam os estados de operação.

### Esteira livre

O sensor encontra-se iluminado e nenhuma peça está sendo detectada (part_detected = False).

### Peça Detectada

Quando o valor do ADC ultrapassa o limiar definido, entende-se que uma peça iniciou sua passagem pelo sensor. (part_detected = True)
Enquanto esse estado permanecer ativo, o sistema monitora duas situações:

- retorno da iluminação, indicando que a peça passou completamente;
- permanência excessiva da obstrução, caracterizando uma micro-parada.

Quando a iluminação retorna ao estado normal, a contagem é incrementada e o sistema retorna ao estado inicial.

## Interação entre os componentes

O funcionamento do sistema pode ser resumido da seguinte forma:

- o LDR fornece continuamente informações sobre a intensidade luminosa;
- o ADC converte essa informação em valores digitais;
- o firmware compara o valor lido com um limiar previamente calculado;
- o contador é incrementado somente após a peça deixar o sensor;
- a interrupção do botão sinaliza uma solicitação de reset através de uma flag;
- o loop principal processa essa flag e reinicializa as variáveis do sistema.

Essa abordagem reduz o tempo gasto dentro da rotina de interrupção, mantendo a maior parte da lógica concentrada no fluxo principal do programa.

---

## Componentes Utilizados na Simulação

| Componente | Função |
|------------|--------|
| ESP32 DevKit C v4 | Microcontrolador responsável pela execução do firmware. |
| Sensor LDR | Sensor óptico utilizado para detectar a passagem das peças através da variação da luminosidade. A saída digital foi conectada no pino 26 e a saída analógica no pino 27.|
| Botão de Reset | Permite reiniciar o contador de produção e limpar o estado do sistema. A saída foi conectada no pino 25.|
| Resistor de pull-up | Resistor de 10k responsável por manter a linha em nível lógico '1' enquanto o botão estiver solto.|

---

## Decisões Técnicas Relevantes

### Resistor de pull-up externo

Embora o ESP32 permita a utilização do resistor de pull-up interno na entrada digital do botão, optou-se pela implementação de um resistor de pull-up externo de 10 kΩ. Essa escolha teve como objetivo aplicar, na prática, os conceitos de sinais e de entradas digitais estudados ao longo do curso, demonstrando o entendimento tanto da configuração por software quanto da implementação em hardware.

### Utilização da leitura analógica

Apesar do cenário disponibilizar um pino digital para o LDR, foi utilizada a leitura analógica do sensor. Essa abordagem permite definir um limiar de detecção diretamente em função da iluminância especificada no enunciado (500 lux), tornando o algoritmo independente do limiar pré-definido do sensor.

Para isso, foi calculada uma equação com base nos dados do LDR fornecidos pelo Wokwi para encontrar a resistência equivalente na iluminância desejada e, posteriormente, determinar o valor correspondente do ADC.

Dessa forma, o sistema passa a tomar decisões baseadas na grandeza física especificada no problema, e não apenas em níveis lógicos.

### Uso de interrupção para o botão

O botão de reset foi implementado utilizando interrupção externa (`IRQ_FALLING`).

A rotina de interrupção possui apenas a responsabilidade de identificar o acionamento e sinalizar uma flag para o programa principal. Toda a lógica de reset é executada posteriormente dentro do loop principal.

Essa organização reduz o tempo de execução da interrupção e evita operações demoradas em contexto de ISR.

### Debounce por software

Foi implementado um mecanismo de debounce baseado em tempo utilizando `time.ticks_ms()`.

Sempre que ocorre uma interrupção, o firmware verifica o intervalo desde o último acionamento válido. Apenas eventos separados pelo tempo de debounce definido são aceitos, evitando múltiplos resets causados pelo efeito mecânico do botão.

---

## Resultados Obtidos

A simulação apresentou o comportamento esperado para todos os requisitos propostos.

Na inicialização, o sistema configura corretamente os periféricos e informa que o contador foi inicializado.

Durante a passagem de uma peça pelo sensor, o firmware identifica a obstrução da luz e incrementa o contador somente após o retorno da iluminação, registrando corretamente o número acumulado de peças.

Quando o sensor permanece bloqueado por um intervalo superior a cinco segundos (configurável), o sistema identifica uma condição de micro-parada e informa essa ocorrência através da interface serial.

O acionamento do botão de reset reinicializa corretamente o contador e os estados internos do sistema, confirmando a operação por meio da mensagem serial especificada.

---

## Comentários Adicionais

Durante o desenvolvimento, uma das principais preocupações foi manter a implementação simples, organizada e compatível com o desenvolvimento para microcontroladores, que deve ser eficiente e enxuta.

Na etapa de testes automatizados, o **cenário 3** apresentou desafios de validação. O problema não estava na lógica de interrupção do firmware, mas sim em uma condição de corrida do próprio ambiente de testes. O delay de 200 ms após o "pressionar do botão" causava uma dessincronização: a rotina de interrupção do botão era processada e a mensagem serial era enviada antes que o ambiente de teste estivesse pronto para interceptá-la, ou seja, o alerta de reset era enviado corretamente, mas a simulação estava no delay e não no wait-serial, resultando em erro de timeout.

Para contornar essa limitação, foi necessário realizar um ajuste empírico no firmware, ajustando o delay para estabilidade da simulação no começo do loop principal para 250 ms. Essa adequação permitiu que na validação, o microcontrolador enviasse a mensagem na janela de tempo certa para o teste, resultando em sucesso no cenário 3.

Como melhoria futura, seria possível expandir o sistema para registrar métricas adicionais de produção, como tempo médio entre peças, produtividade por turno, taxa de produção e armazenamento das informações em memória não volátil ou envio para um sistema supervisório utilizando protocolos de comunicação como o MQTT.

O desenvolvimento deste projeto permitiu consolidar conceitos relacionados à programação de sistemas embarcados em microPython, tratamento de interrupções, leitura de sensores analógicos, debounce por software, temporização não bloqueante e desenvolvimento de firmware para aplicações de monitoramento industrial.
