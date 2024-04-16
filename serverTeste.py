import socket
import struct
import os as cv2

TIMEOUT = 5


class Package:
    # Construtor da classe deve possuir o data e o número do segmento
    # no contrutor é calculado o checksum
    def __init__(self, data, number):
        self.data = data
        self.number = number
        self.checksum = self.calculate_checksum()
        self.createPackage()
        

    def calculate_checksum(self):
        sum = 0
        for i in range(0, len(self.data), 2):
            if i + 1 < len(self.data):
                word = (self.data[i] + (self.data[i + 1] << 8))
            elif i < len(self.data):
                word = self.data[i]
            sum += word
            sum = (sum & 0xffff) + (sum >> 16)
        checksum = (~sum & 0xffff)
        return checksum  
    
    def addChecksum(self):  
        checksum = self.calculate_checksum()
        header_format = "H"
        header_with_checksum = struct.pack(header_format, checksum)
        self.packge =  header_with_checksum + self.data

    def addNumberSegment(self):
        header_format = "H"
        header_with_number = struct.pack(header_format, self.number)
        self.packge = header_with_number + self.packge

    def createPackage(self):
        self.addChecksum()
        self.addNumberSegment()

    # a classe packege deve possuir um método para criar o pacote a partir das funções add number e add checksum
    def getPackage(self):
        return self.packge
    

class UDPServer:
    #O construtor da classe deve receber a porta e o endereço do servidor
    # e criar o socket
    def __init__(self, port, host):
        self.port = port
        self.host = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.host, self.port))
        #self.server.settimeout(TIMEOUT)
        self.file = None
        self.requests = []
        self.currentClientAddress = None
        self.segment_size = 1024
        self.startServer()
    
    def getFile (self, filename):
        try:
            file = open(f"server/arquivos/{filename}", "rb")
            self.file = file.read()
            return True
        except FileNotFoundError:
            self.server.sendto(Package("Arquvo encontrado".encode("utf-8"), 0).getPackage(), self.currentClientAddress)
            return False
        
            
    
    def closeServer(self):
        self.server.close()
        self.destroy()

    def filterMessage(self, message):
        if(message == "exit"):
            self.server.sendto(Package("exit".encode() , 0).getPackage(), self.currentClientAddress)
            return False
        message = message.split(" ")
        if(message.__len__() < 2 or message[0] != "GET"):
            self.server.sendto(Package("Comando Inválido".encode(), 0).getPackage(), self.currentClientAddress)
            return False
        if(message[0] == "GET"):
            return message[1]
        
    def sendFile(self):
        
        segments = [self.file[i:i+self.segment_size] for i in range(0, len(self.file), self.segment_size)]
        self.server.settimeout(TIMEOUT)
        i = 0
        while i < len(segments):
            package = Package(segments[i], i).getPackage()
            self.server.sendto(package, self.currentClientAddress)
            try:
                message, addr = self.server.recvfrom(1024)
                while(addr != self.currentClientAddress):
                    print("Descartando pacote de outro cliente")
                    self.requests.append({"data": message, "address": addr})
                    message, addr = self.server.recvfrom(1024)
                message = message.decode("utf-8").split(" ")
                numberACK = int(message[1])
                print("Recebendo ACK", numberACK)
                if numberACK < i:
                    print("Erro no envio do segmento")
                    i = numberACK + 1
                    continue
                elif message :
                    print("Segmento enviado com sucesso")
                i += 1 
            except socket.timeout:
                print("Timeout")
                continue 
        print("Mandando EOF")
        package = Package("EOF".encode("utf-8"), 0)
        self.server.sendto(package.getPackage(), addr)
        try:
            while True:
                message, addr = self.server.recvfrom(1024)
                print("message: ", message.decode("utf-8"))
                message = message.decode("utf-8").split(" ")
                if message[0] == "RECEBIDO":
                    break
            
        except socket.timeout:
            print("Timeout, não foi possível enviar o arquivo")
            return
        print("Arquivo enviado com sucesso")
            

    def startServer(self):
        while True:
            self.server.settimeout(None)
            while len(self.requests) == 0:
                data , addr = self.server.recvfrom(1024)
                self.requests.append({"data": data, "address": addr})

            request = self.requests.pop(0)
            data = request["data"]
            self.currentClientAddress = request["address"]
            try:
                print("Aberto conexão com o cliente", self.currentClientAddress , "com o comando", data.decode("utf-8"))
                data = self.filterMessage(data.decode("utf-8"))
                if(data == False):
                    continue
                if(self.getFile(data)):
                    self.sendFile()
            except Exception as e:
                print(e)
                print("Erro ao enviar protocolo de comunicação")
                continue
        


def main():
    serverSocket = UDPServer(5555,"127.0.0.1")

if __name__ == "__main__":
    main()