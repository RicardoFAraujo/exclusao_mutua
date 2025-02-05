import socket
import time
import sys
from datetime import datetime

F = 10  # Tamanho fixo das mensagens em bytes
SEPARADOR = '|'

class Processo:
    def __init__(self, id_processo, host='localhost', porta=5000, repeticoes=5, tempo_espera=2):
        self.id_processo = id_processo
        self.host = host
        self.porta = porta
        self.repeticoes = repeticoes
        self.tempo_espera = tempo_espera
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def formatar_mensagem(self, identificador):
        mensagem = f"{identificador}{SEPARADOR}{self.id_processo}{SEPARADOR}".ljust(F, '0')
        return mensagem
    
    def enviar_mensagem(self, mensagem):
        self.socket.sendto(mensagem.encode(), (self.host, self.porta))
    
    def aguardar_grant(self):
        while True:
            data, _ = self.socket.recvfrom(F)
            mensagem = data.decode().strip('0')
            partes = mensagem.split(SEPARADOR)
            if partes[0] == "3" and partes[1] == self.id_processo:
                print(f"Processo {self.id_processo} recebeu GRANT e pode acessar a região crítica")
                return
    
    def executar(self):
        for _ in range(self.repeticoes):
            # Solicita acesso à região crítica
            mensagem_request = self.formatar_mensagem("1")  # REQUEST
            self.enviar_mensagem(mensagem_request)
            print(f"Processo {self.id_processo} solicitou acesso à região crítica")
            
            # Aguarda permissão (GRANT)
            self.aguardar_grant()
            
            # Escreve no arquivo resultado.txt
            with open("resultado.txt", "a") as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                f.write(f"{self.id_processo} {timestamp}\n")
            print(f"Processo {self.id_processo} escreveu no arquivo")
            
            # Libera a região crítica
            mensagem_release = self.formatar_mensagem("2")  # RELEASE
            self.enviar_mensagem(mensagem_release)
            print(f"Processo {self.id_processo} liberou a região crítica")
            
            # Espera antes de repetir
            time.sleep(self.tempo_espera)
        
        print(f"Processo {self.id_processo} finalizado.")
        self.socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python3 processo.py <ID> <Repetições> <Tempo de Espera>")
        sys.exit(1)
    
    id_processo = sys.argv[1]
    repeticoes = int(sys.argv[2])
    tempo_espera = int(sys.argv[3])
    
    processo = Processo(id_processo, repeticoes=repeticoes, tempo_espera=tempo_espera)
    processo.executar()
