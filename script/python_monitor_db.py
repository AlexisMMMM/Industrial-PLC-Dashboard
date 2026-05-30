from pymodbus.client import ModbusTcpClient
import sqlite3
import time as time_module
from datetime import datetime

# Conexión al PLC
client = ModbusTcpClient(host='127.0.0.1', port=502)

# Conexión a SQLite
db_path = 'plc_industrial.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS plc_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        sensor_object INTEGER NOT NULL,
        motor_running INTEGER NOT NULL
    )
''')
conn.commit()

def main():
    if not client.connect():
        print("Error: No se pudo conectar al PLC")
        return

    print("Conectado al PLC — escribiendo a SQLite...")
    print("-" * 40)

    try:
        while True:
            sensor = client.read_coils(address=0, count=1)
            motor = client.read_discrete_inputs(address=0, count=1)

            sensor_val = 1 if sensor.bits[0] else 0
            motor_val = 1 if motor.bits[0] else 0

            timestamp = int(time_module.time() * 1000)

            cursor.execute('''
                INSERT INTO plc_data (timestamp, sensor_object, motor_running)
                VALUES (?, ?, ?)
            ''', (timestamp, sensor_val, motor_val))
            conn.commit()

            print(f"[{timestamp}] Sensor: {bool(sensor_val)} | Motor: {bool(motor_val)}")

            time_module.sleep(1)

    except KeyboardInterrupt:
        print("\nMonitoreo detenido.")
        client.close()
        conn.close()

if __name__ == "__main__":
    main()
