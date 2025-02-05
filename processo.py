import socket
import time
import sys
from datetime import datetime

class Processo:
    def __init__(self, id_processo, host='localhost', porta=5000, repeticoes=5, tempo_espera=2):
        self.id_processo = id_processo
        self.host = host
        self.porta = porta
        self.repeticoes = repeticoes
        self.tempo_espera = tempo_espera
        
    def enviar_mensagem(self, mensagem):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.porta))
                s.sendall(mensagem.encode())
        except ConnectionRefusedError:
            print(f"[Erro] Não foi possível conectar ao coordenador {self.host}:{self.porta}")
            sys.exit(1)
        
    def executar(self):
        for _ in range(self.repeticoes):
            # Solicita acesso à região crítica
            self.enviar_mensagem(f"REQUEST {self.id_processo}")
            print(f"Processo {self.id_processo} solicitou acesso à região crítica")
            
            # Aguarda permissão
            time.sleep(1)
            
            # Escreve no arquivo resultado.txt
            with open("resultado.txt", "a") as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                f.write(f"{self.id_processo} {timestamp}\n")
            print(f"Processo {self.id_processo} escreveu no arquivo")
            
            # Libera a região crítica
            self.enviar_mensagem(f"RELEASE {self.id_processo}")
            print(f"Processo {self.id_processo} liberou a região crítica")
            
            # Espera antes de repetir
            time.sleep(self.tempo_espera)
        
        print(f"Processo {self.id_processo} finalizado.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python3 processo.py <ID> <Repetições> <Tempo de Espera>")
        sys.exit(1)
    
    id_processo = sys.argv[1]
    repeticoes = int(sys.argv[2])
    tempo_espera = int(sys.argv[3])
    
    processo = Processo(id_processo, repeticoes=repeticoes, tempo_espera=tempo_espera)
    processo.executar()
