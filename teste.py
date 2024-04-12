import struct
import sys
def calculate_checksum(data):
    sum = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            word = (data[i] + (data[i + 1] << 8))
        elif i < len(data):
            word = data[i]
        sum += word
        sum = (sum & 0xffff) + (sum >> 16)
    checksum = (~sum & 0xffff)
    return checksum  


def main():
    bin_data = b'Hello, World! How are you?'
    print (f"Data: {bin_data}")
    tamanho = len(bin_data)
    print(tamanho)
    checksum = calculate_checksum(bin_data)
    print (f"Checksum: {checksum}")
    header_checksum = struct.pack('H', checksum)
    print (f"Header checksum: {header_checksum}")
    data = header_checksum + bin_data
    print(data)
    checksum = struct.unpack('H', data[:2])[0]
    data = data[2:]
    print(data)
    calculated_checksum = calculate_checksum(data)
    if checksum == calculated_checksum:
        print("Checksum válido")
    return 0

if __name__ == "__main__":
    main()
