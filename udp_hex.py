import sys
import time
import socket


UDP_IP = "192.168.18.77"
UDP_PORT = 65533

path = "led_yellow.hex"


# UDP configuration
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.connect((UDP_IP, UDP_PORT))
# sock.bind((UDP_IP, UDP_PORT))


def send_row(len, data):
    for count in range(len):
        sock.sendto(data[count], (UDP_IP, UDP_PORT))
    print(data)


def run():
    bytes_count = 1  # Cuenta de los bytes de instruccion
    byte_crc = 0  # Bytes de checksum
    # Cuenta de los bytes de instrucción (se puede modificar para seleccionar la cantidad de bytes por linea)
    byte_maker = 0
    count_nibble = 1  # Posición de Nibble en ASCCI de la linea
    nibble1 = 0  # Primer nibble entero del byte
    nibble2 = 0  # Segundo nibble entero del byte
    nibbleTobyte = 0  # Junta los nibbles para formar en byte y lo convierte en formato byte
    data_row_hex = []  # Data total de cada linea del file hex son ":" y chcksm
    line_len_past = 0
    data_row_hex_past = []
    with open(path, 'r') as archivo:
        estado = "read_row"
        while True:
            match estado:
                case "read_row":
                    data_row_hex.clear()
                    linea = archivo.readline()
                    linea = linea.rstrip()
                    if not linea:  # Verifica si es la última linea
                        print("Booloader Finalizado de: " + path)
                        sys.exit(0)
                    if (linea[0] == ":"):  # Verifica si la linea inicia con ":"
                        pass
                    else:
                        continue
                    # Obtiene la cantidad de bytes de instruccion
                    line_len = int(((len(linea) - 1) / 2))
                    # Bucle según de cantidad bytes de instruccion
                    for byte_maker in range(line_len):
                        # Verifica que aún no se llegue al byte de checksum
                        if (bytes_count != line_len):
                            # Conversión de ascii a entero
                            # Verificacion de 0 a 9
                            if (ord(linea[count_nibble]) >= 48) and (ord(linea[count_nibble]) <= 57):
                                nibble1 = (
                                    (ord(linea[count_nibble]) - 48) << 4)
                                # print(nibble1)
                            # Verificación de A a F
                            elif (ord(linea[count_nibble]) >= 65) and (ord(linea[count_nibble]) <= 70):
                                # Corrimiento para juntarlo con nibble2 para formar un byte
                                # print(ord(linea[count_nibble]))
                                nibble1 = (
                                    (ord(linea[count_nibble]) + 10 - 65) << 4)
                                # print(nibble1)
                            else:
                                # print(ord(linea[count_nibble]))
                                nibble1 = (
                                    (ord(linea[count_nibble]) + 10 - 97) << 4)
                                # print(nibble1)
                            if (ord(linea[count_nibble + 1]) >= 48) and (ord(linea[count_nibble + 1]) <= 57):
                                nibble2 = (ord(linea[count_nibble + 1]) - 48)
                                # print(nibble2)
                            # Verificación de A a F
                            elif (ord(linea[count_nibble]) >= 65) and (ord(linea[count_nibble]) <= 70):
                                # Corrimiento para juntarlo con nibble2 para formar un byte
                                # print(ord(linea[count_nibble]))
                                nibble2 = (
                                    (ord(linea[count_nibble + 1]) + 10 - 65))
                                # print(nibble1)
                            else:
                                # print(ord(linea[count_nibble]))
                                nibble2 = (
                                    (ord(linea[count_nibble + 1]) + 10 - 97))
                                # print(nibble2)
                            # Junta los nibbles y lo convierte a formato byte
                            nibbleTobyte = bytes([nibble1 + nibble2])
                            # Aumenta la cuenta del bucle. Se suma dos porque se obtiene de 2 en 2 caracteres para formar un byte
                            count_nibble = count_nibble + 2
                            data_row_hex.append(nibbleTobyte)
                    count_nibble = 1  # Regresa la cuenta de caracteres a 1
                    estado = "read_answer"
                case "read_answer":
                    # buffer size is 1024 bytes
                    data, addr = sock.recvfrom(1024)
                    print(data)
                    if data == "k":
                        print("ready")
                        estado = "ok"
                    elif data == "r":
                        estado = "repeat"
                    else:
                        estado = "read_answer"
                case "ok":
                    send_row(line_len, data_row_hex)
                    line_len_past = line_len
                    data_row_hex_past = data_row_hex.copy()
                    estado = "read_row"
                case "repeat":
                    send_row(line_len_past, data_row_hex_past)
                    estado = "read_answer"


if __name__ == '__main__':
    run()
    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)
