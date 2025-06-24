from machine import Pin, PWM
from utime import sleep_ms, ticks_ms
import random
import time
import _thread

#PINES Se quedo enganchado 2 botones del switch pero se puede probar funcionalidad de niveles intercambiando los Pines al 0 segun el nivel que se quiera comprobar
leds = [Pin(i, Pin.OUT) for i in (3, 4, 5, 6)]
botones = [Pin(i, Pin.IN, Pin.PULL_DOWN) for i in (7, 8, 9, 10)]
dip_leyenda      = Pin(2, Pin.IN, Pin.PULL_DOWN)
dip_avanzado     = Pin(1, Pin.IN, Pin.PULL_DOWN)
dip_principiante = Pin(0, Pin.IN, Pin.PULL_DOWN)
boton_reset      = Pin(19, Pin.IN, Pin.PULL_DOWN)

#Buzzer
buzzer = PWM(Pin(11))
DEFAULT_VOLUME = 40000      
buzzer.duty_u16(DEFAULT_VOLUME)
SPEED_FACTOR = 1.0          

# Pines para display 7 segmentos
data  = Pin(15, Pin.OUT)
clock = Pin(16, Pin.OUT)

# Patrones 7 segmentos (0-F)
segmentos = {
    0:0x3F, 1:0x06, 2:0x5B, 3:0x4F, 4:0x66, 5:0x6D, 6:0x7D, 7:0x07,
    8:0x7F, 9:0x6F, 10:0x77, 11:0x7C, 12:0x39, 13:0x5E, 14:0x79, 15:0x71
}

# Diccionario de notas y silencios
notas = {
    "C4": 261, "D4": 294, "E4": 329, "F4": 349,
    "G4": 392, "A4": 440, "B4": 494,
    "C5": 523, "D5": 587, "E5": 659, "F5": 698,
    "G5": 784, "A5": 880, "B5": 988,
    "C6":1047, "D6":1175, "E6":1319, "F6":1397,
    "G6":1568, "A6":1760, "B6":1976,
    "G#5":830, "A#5":932,
    "R": 0
}

# Melodías (duraciones en segundos)
melodia_intro = [
    ("E5", 0.2), ("A5", 0.2), ("B5", 0.2), ("C6", 0.6),
    ("R", 0.1),
    ("E5", 0.2), ("A5", 0.2), ("B5", 0.2), ("C6", 0.6),
    ("R", 0.6),
    ("F5", 0.2), ("A5", 0.2), ("B5", 0.2), ("C6", 0.6),
    ("R", 0.1),
    ("F5", 0.2), ("A5", 0.2), ("B5", 0.2), ("C6", 0.6),
    ("R", 0.1),
    ("D5", 0.2), ("G5", 0.2), ("A5", 0.2), ("B5", 0.6),
    ("R", 0.1),
    ("D5", 0.2), ("G5", 0.2), ("A5", 0.2), ("B5", 0.6),
    ("R", 0.6),
    ("C6", 0.2), ("D6", 0.2), ("C6", 0.2), ("B5", 0.6),
    ("R", 0.5)
]

melodia_cambio_nivel = [
    ("E5", 0.1), ("G5", 0.1), ("E5", 0.1),
    ("C5", 0.1), ("D5", 0.1), ("G5", 0.2)
]

melodia_victoria = [
    ("C5", 0.2), ("D5", 0.2), ("E5", 0.2), ("F5", 0.2),
    ("G5", 0.2), ("A5", 0.2), ("B5", 0.2), ("C6", 0.3),
    ("E6", 0.3), ("C6", 0.2), ("A5", 0.2), ("F5", 0.3),
    ("G5", 0.3), ("C5", 0.6)
]

melodia_game_over = [
    ("C6", 0.25), ("G5", 0.25), ("E5", 0.25),
    ("A5", 0.25), ("B5", 0.25), ("A5", 0.25),
    ("G#5", 0.2), ("A#5", 0.2), ("G#5", 0.25),
    ("E5", 0.25), ("D5", 0.25), ("E5", 0.4)
]

melodia_5_aciertos = [
    ("C6", 0.1), ("G5", 0.1), ("E5", 0.1),
    ("G5", 0.1), ("C6", 0.1), ("E6", 0.2)
]


#FUNCIONES DE SONIDO
def play_note(note: str, duration: float, volume: int = DEFAULT_VOLUME):
    freq = notas.get(note, 0)
    if freq == 0:
        buzzer.duty_u16(0)
    else:
        buzzer.freq(freq)
        buzzer.duty_u16(volume)
    time.sleep(duration)
    buzzer.duty_u16(0)
    time.sleep(0.015)  

def reproducir_melodia(melodia, speed_factor=SPEED_FACTOR):
    for note, dur in melodia:
        play_note(note, dur * speed_factor)

def tono_inicio():
    reproducir_melodia(melodia_intro)

def tono_cambio_nivel():
    reproducir_melodia(melodia_cambio_nivel)

def tono_victoria():
    reproducir_melodia(melodia_victoria)

def tono_game_over():
    reproducir_melodia(melodia_game_over)

def enviar_display(valor):
    if valor > 15:
        valor = 15  # evita errores por valores no representables
    pat = segmentos.get(valor, 0) & 0x7F
    for i in range(7, -1, -1):
        bit = (pat >> i) & 1
        data.value(bit)
        clock.value(1)
        sleep_ms(1)
        clock.value(0)
        sleep_ms(1)



# ANIMACIONES Y ERROR 
def animacion_set(puntaje):
 # Inicia la melodía de 5 aciertos en segundo plano
    _thread.start_new_thread(reproducir_melodia, (melodia_5_aciertos,))

    # Animación de LEDs secuencial
    for _ in range(3):
        for led in leds:
            led.value(1)
            sleep_ms(70)
            led.value(0)
    enviar_display(puntaje)  



def mostrar_error():
    # Inicia la melodía de “game over” en segundo plano
    _thread.start_new_thread(reproducir_melodia, (melodia_game_over,))

    # Animación de pérdida: parpadeo alternado
    for _ in range(2):
        for i, led in enumerate(leds):
            led.value(1 if i % 2 == 0 else 0)
        sleep_ms(150)
        for i, led in enumerate(leds):
            led.value(1 if i % 2 == 1 else 0)
        sleep_ms(150)

    # Animación de “carrera” rápida adelante y atrás
    for _ in range(2):
        for led in leds:
            apagar_leds()
            led.value(1)
            sleep_ms(80)
        for led in reversed(leds):
            apagar_leds()
            led.value(1)
            sleep_ms(80)
    apagar_leds()

    # Breve pausa para asegurarse de que el último fragmento de la melodía suene
    sleep_ms(200)

    # Esperar a que se presione RESET
    while not boton_reset.value():
        sleep_ms(50)

def animacion_victoria_leds(ciclos=3, delay=100):
    """
    Efecto "corriendo" de LEDs adelante y atrás.
    """
    for _ in range(ciclos):
        for led in leds:
            apagar_leds()
            led.value(1)
            sleep_ms(delay)
        for led in reversed(leds[1:-1]):
            apagar_leds()
            led.value(1)
            sleep_ms(delay)
    apagar_leds()

# ==== UTILIDADES ====
def apagar_leds():
    for led in leds:
        led.value(0)

# ESTADO GLOBAL 
total_aciertos = 0
set_count = 0              
tipo_set = 5             
nivel_actual = None


# GESTIÓN DE NIVELES 
def revisar_nivel():
    global nivel_actual
    if dip_leyenda.value():
        if total_aciertos >= 25:
            return "VICTORIA", 0
        modo, t = "LEYENDA", 200
    elif dip_avanzado.value():
        if total_aciertos >= 60:
            return "VICTORIA", 0
        modo, t = "AVANZADO", 500
    else:
        if total_aciertos >= 75:
            return "VICTORIA", 0
        elif total_aciertos >= 60:
            modo, t = "LEYENDA", 200
        elif total_aciertos >= 25:
            modo, t = "AVANZADO", 500
        else:
            modo, t = "PRINCIPIANTE", 1000
    if modo != nivel_actual and nivel_actual is not None:
        tono_cambio_nivel()
    nivel_actual = modo
    return modo, t

# PRINCIPAL 
tono_inicio()

while True:
    # Reinicio al comenzar nueva partida
    total_aciertos = 0
    set_count      = 0
    nivel_actual   = None

    # Mostrar 0 sets SOLO UNA VEZ al iniciar
    enviar_display(0)
    print("→ Juego iniciado. Sets: 0")

    # Bucle de juego
    while True:
        apagar_leds()
        sleep_ms(200)

        # Determina el modo y tiempo
        modo, t_lim = revisar_nivel()
        print("Modo:", modo, "| Límite (ms):", t_lim)

        # Patrón de LEDs
        if modo == "LEYENDA":
          cantidad_leds = random.choice([1, 2])
          expected = set()
          while len(expected) < cantidad_leds:
              expected.add(random.randint(0, 3))
        else:
            expected = {random.randint(0, 3)}

        for idx in expected:
            leds[idx].value(1)

        # Detectar pulsaciones
        inicio   = ticks_ms()
        acierto  = False
        pressed  = set()

        while True:
            if modo == "VICTORIA":
                tono_victoria()
                animacion_victoria_leds()
                print("¡Has ganado!")
                acierto = None
                break

            if ticks_ms() - inicio >= t_lim:
                mostrar_error()
                acierto = None
                break

            for j in range(4):
                if botones[j].value() and j not in expected:
                    mostrar_error()
                    acierto = None
                    break
            if acierto is None:
                break

            if modo == "LEYENDA":
                for i in expected - pressed:
                    if botones[i].value():
                        pressed.add(i)
                if pressed == expected:
                    while any(botones[i].value() for i in expected):
                        sleep_ms(10)
                    play_note("F6", 0.6)
                    acierto = True
                    break
            else:
                for i in expected - pressed:
                    if botones[i].value():
                        pressed.add(i)
                        play_note("F6", 0.6)
                if pressed == expected:
                    while any(botones[i].value() for i in expected):
                        sleep_ms(10)
                    acierto = True
                    break

        # Si falló, salimos al reset
        if acierto is not True:
            break

        # Acierto válido
        total_aciertos += 1
        print("Aciertos totales:", total_aciertos)

        # Verificamos si completaste un nuevo set
        if total_aciertos % tipo_set == 0:
          set_count = total_aciertos // tipo_set
          print(f"→ Nuevo set completado. Sets: {set_count}")
          enviar_display(set_count)   
          animacion_set(set_count) 
          sleep_ms(50)
#Esperamos botón RESET
    print("→ Esperando reset...")
    while not boton_reset.value():
        sleep_ms(50)

    print("→ Reiniciando juego...")
    sleep_ms(2000)