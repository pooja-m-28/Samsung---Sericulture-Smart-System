from datetime import datetime
import time
import RPi.GPIO as GPIO
import BlynkLib

# NEW DHT LIBRARY (Python 3.11 compatible)
import adafruit_dht
import board

# ============================================================================
# BLYNK CONFIGURATION
# ============================================================================

BLYNK_AUTH = "37CjFzm5cKFk9EDc2irOV2YbeRQN8n8b"

VPIN_TEMPERATURE = 0
VPIN_HUMIDITY = 1
VPIN_FAN_STATUS = 2
VPIN_PUMP_STATUS = 3
VPIN_FAN_CONTROL = 4
VPIN_PUMP_CONTROL = 5
VPIN_SYSTEM_STATUS = 6

# ============================================================================
# HARDWARE CONFIGURATION
# ============================================================================

# DHT11 Sensor
dhtDevice = adafruit_dht.DHT11(board.D17, use_pulseio=False)

FAN_RELAY_PIN = 6
PUMP_RELAY_PIN = 27
LED_PIN = 26   # LED GPIO pin (ACTIVE LOW)

MAX_TEMPERATURE = 25.0
MIN_HUMIDITY = 50.0

CHECK_INTERVAL = 5
DEVICE_RUN_TIME = 10

manual_fan_state = False
manual_pump_state = False

fan_start_time = 0
pump_start_time = 0
fan_auto_running = False
pump_auto_running = False

# ============================================================================
# INITIALIZE BLYNK
# ============================================================================

blynk = BlynkLib.Blynk(BLYNK_AUTH, server="blynk.cloud", port=8080)

# ============================================================================
# DEVICE CONTROL FUNCTIONS
# ============================================================================

def fan_on():
    GPIO.output(FAN_RELAY_PIN, GPIO.LOW)

def fan_off():
    GPIO.output(FAN_RELAY_PIN, GPIO.HIGH)

def pump_on():
    GPIO.output(PUMP_RELAY_PIN, GPIO.LOW)

def pump_off():
    GPIO.output(PUMP_RELAY_PIN, GPIO.HIGH)

# ACTIVE-LOW LED
def led_on():
    GPIO.output(LED_PIN, GPIO.LOW)

def led_off():
    GPIO.output(LED_PIN, GPIO.HIGH)

# ============================================================================
# BLYNK HANDLERS
# ============================================================================

def v4_fan_control(value):
    global manual_fan_state, fan_auto_running
    manual_fan_state = int(value[0]) == 1

    if manual_fan_state:
        fan_auto_running = False
        fan_on()
        blynk.virtual_write(VPIN_FAN_STATUS, "MANUAL ON")
        print("📱 Fan ON (Manual)")
    else:
        fan_off()
        blynk.virtual_write(VPIN_FAN_STATUS, "OFF")
        print("📱 Fan OFF")

def v5_pump_control(value):
    global manual_pump_state, pump_auto_running
    manual_pump_state = int(value[0]) == 1

    if manual_pump_state:
        pump_auto_running = False
        pump_on()
        blynk.virtual_write(VPIN_PUMP_STATUS, "MANUAL ON")
        print("📱 Pump ON (Manual)")
    else:
        pump_off()
        blynk.virtual_write(VPIN_PUMP_STATUS, "OFF")
        print("📱 Pump OFF")

def blynk_connected():
    print("✅ Connected to Blynk Cloud")
    blynk.virtual_write(VPIN_SYSTEM_STATUS, "System Online")
    blynk.sync_virtual(VPIN_FAN_CONTROL)
    blynk.sync_virtual(VPIN_PUMP_CONTROL)

def blynk_disconnected():
    print("⚠️ Disconnected from Blynk")

blynk.on("V" + str(VPIN_FAN_CONTROL), v4_fan_control)
blynk.on("V" + str(VPIN_PUMP_CONTROL), v5_pump_control)
blynk.on("connected", blynk_connected)
blynk.on("disconnected", blynk_disconnected)

# ============================================================================
# SENSOR READING
# ============================================================================

def read_sensor():
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        return humidity, temperature
    except RuntimeError:
        return None, None

# ============================================================================
# CONTROL LOGIC
# ============================================================================

def control_environment(temperature, humidity):
    global fan_start_time, pump_start_time, fan_auto_running, pump_auto_running

    now = time.time()
    fan_status = "OFF"
    pump_status = "OFF"

    if not manual_fan_state and temperature is not None:
        if temperature > MAX_TEMPERATURE and not fan_auto_running:
            fan_on()
            fan_auto_running = True
            fan_start_time = now
            fan_status = "AUTO ON"
            blynk.virtual_write(VPIN_FAN_STATUS, fan_status)
        elif fan_auto_running:
            if now - fan_start_time >= DEVICE_RUN_TIME:
                fan_off()
                fan_auto_running = False
                blynk.virtual_write(VPIN_FAN_STATUS, "OFF")
            else:
                fan_status = "AUTO ON"

    if not manual_pump_state and humidity is not None:
        if humidity < MIN_HUMIDITY and not pump_auto_running:
            pump_on()
            pump_auto_running = True
            pump_start_time = now
            pump_status = "AUTO ON"
            blynk.virtual_write(VPIN_PUMP_STATUS, pump_status)
        elif pump_auto_running:
            if now - pump_start_time >= DEVICE_RUN_TIME:
                pump_off()
                pump_auto_running = False
                blynk.virtual_write(VPIN_PUMP_STATUS, "OFF")
            else:
                pump_status = "AUTO ON"

    return fan_status, pump_status

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(FAN_RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(PUMP_RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.HIGH)  # LED OFF initially

    print("🚀 Sericulture Control System Started")

    try:
        while True:
            blynk.run()

            humidity, temperature = read_sensor()

            if humidity is None or temperature is None:
                time.sleep(2)
                continue

            # Send data to Blynk
            blynk.virtual_write(VPIN_TEMPERATURE, round(temperature, 1))
            blynk.virtual_write(VPIN_HUMIDITY, round(humidity, 1))

            # LED indication (LOW temperature)
            if temperature < MAX_TEMPERATURE:
                led_on()
            else:
                led_off()

            fan_status, pump_status = control_environment(temperature, humidity)

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"T={temperature:.1f}°C  H={humidity:.1f}%  "
                f"Fan={fan_status}  Pump={pump_status}  "
                f"LED={'ON' if temperature < MAX_TEMPERATURE else 'OFF'}"
            )

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")

    finally:
        fan_off()
        pump_off()
        led_off()
        GPIO.cleanup()
        dhtDevice.exit()
        print("🧹 GPIO cleaned up")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
