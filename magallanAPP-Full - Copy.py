import serial.tools.list_ports
import serial
import time

def find_serial_port(driver_name):
    for port, desc, hwid in serial.tools.list_ports.comports():
        if driver_name in desc:
            return port
    return None

def configure_serial(driver_name, baud_rate, data_bits, stop_bits, parity):
    com_port = find_serial_port(driver_name)
    if com_port:
        try:
            ser = serial.Serial(com_port, baud_rate, bytesize=data_bits, stopbits=stop_bits, parity=parity, timeout=1)
            return ser
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
    else:
        print(f"Device with driver name '{driver_name}' not found.")
    return None

def send_host_command(ser, command):
    ser.write(command.encode('utf-8') + b'\r')  # Send the command and terminate with '\r'

def receive_data(ser):
    barcode_data_received = False  # Flag to indicate if barcode data has been received
    last_barcode_data = None  # To keep track of the last received barcode data
    weight_data_received = False  # Flag to indicate if weight data has been received

    try:
        while True:
            data = ser.readline()
            if data:
                data = data.decode('utf-8').strip()
                if data.startswith("S144"):
                    weight_data_received = True
                    print(f"Weight values: {data}")
                else:
                    if data != last_barcode_data:
                        barcode_data_received = True
                        print(f"Barcode read: {data}")
                        last_barcode_data = data

                        # Send the host command when barcode data is received
                        host_command = "S14\x0d"
                        send_host_command(ser, host_command)
                    else:
                        barcode_data_received = False

                if barcode_data_received or weight_data_received:
                    time.sleep(5)  # Add a 5-second delay before checking for the next data

    except KeyboardInterrupt:
        print("Received KeyboardInterrupt. Exiting...")
    except Exception as e:
        print(f"Error while receiving data: {e}")
    finally:
        ser.close()

if __name__ == "__main__":
    driver_name = "USB-SERIAL CH340"  # Modify this to match the driver name you want to use
    baud_rate = 9600
    data_bits = 7
    stop_bits = 1
    parity = serial.PARITY_ODD

    serial_connection = configure_serial(driver_name, baud_rate, data_bits, stop_bits, parity)
    if serial_connection:
        print(f"Connected to a device with driver name '{driver_name}' at {baud_rate} baud rate with data bits {data_bits}, stop bits {stop_bits}, and odd parity.")

        receive_data(serial_connection)
