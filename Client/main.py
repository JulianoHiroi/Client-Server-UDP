import socket

def main():
    host = "127.0.0.1"
    port = 4455 
    addr = (host, port)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        data = input("Enter a word: ")

        data = data.encode()
        client.sendto(data, addr)
        
        data,addr = client.recvfrom(1024)
        data = data.decode("utf-8")
        print (f"Server: {data}")

if __name__ == "__main__":
    main()
