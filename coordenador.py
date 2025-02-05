import socket
import threading
import queue
import time

F = 10  # Tamanho fixo das mensagens em bytes
SEPARADOR = '|'

class Coordenador:
    def __init__(self, host='localhost', porta=5000):
        self.host = host
        self.porta = porta
        self.fila_pedidos = queue.Queue()
        self.atendimentos = {}
        self.lock = threading.Lock()
        self.rodando = True
        self.processos = {}  # Armazena endereço dos processos
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.porta))
        
        print(f'Coordenador ouvindo em {self.host}:{self.porta} (UDP)')
        
    def log(self, mensagem):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with open("log_coordenador.txt", "a") as f:
            f.write(f'[{timestamp}] {mensagem}\n')
        
    def formatar_mensagem(self, identificador, processo_id):
        mensagem = f"{identificador}{SEPARADOR}{processo_id}{SEPARADOR}".ljust(F, '0')
        return mensagem
    
    def receber_mensagens(self):
        while self.rodando:
            try:
                mensagem, addr = self.server_socket.recvfrom(F)
                mensagem = mensagem.decode().strip('0')
                
                if not mensagem:
                    continue
                
                partes = mensagem.split(SEPARADOR)
                processo_id = partes[1]
                self.processos[processo_id] = addr  # Armazena o endereço do processo
                
                self.log(f'Recebido de {processo_id} ({addr}): {mensagem}')
                
                if partes[0] == "1":  # REQUEST
                    with self.lock:
                        self.fila_pedidos.put(processo_id)
                    self.log(f'Processo {processo_id} adicionou pedido na fila')
                
                elif partes[0] == "2":  # RELEASE
                    with self.lock:
                        if not self.fila_pedidos.empty() and self.fila_pedidos.queue[0] == processo_id:
                            self.fila_pedidos.get()
                            self.atendimentos[processo_id] = self.atendimentos.get(processo_id, 0) + 1
                            self.log(f'Processo {processo_id} liberou a região crítica')
                
            except Exception as e:
                self.log(f'Erro: {e}')
    
    def gerenciar_exclusao_mutua(self):
        while self.rodando:
            with self.lock:
                if not self.fila_pedidos.empty():
                    processo_atual = self.fila_pedidos.queue[0]
                    if processo_atual in self.processos:
                        mensagem_grant = self.formatar_mensagem("3", processo_atual)  # 3 = GRANT
                        self.server_socket.sendto(mensagem_grant.encode(), self.processos[processo_atual])
                        self.log(f'Enviado GRANT para Processo {processo_atual}')
            time.sleep(1)
    
    def interface_terminal(self):
        while self.rodando:
            comando = input("Comando: ")
            if comando == "fila":
                with self.lock:
                    print("Fila de pedidos:", list(self.fila_pedidos.queue))
            elif comando == "atendimentos":
                with self.lock:
                    print("Atendimentos por processo:", self.atendimentos)
            elif comando == "sair":
                self.rodando = False
                self.server_socket.close()
                print("Encerrando coordenador...")
                break
            else:
                print("Comando desconhecido. Use: fila, atendimentos, sair")

    def iniciar(self):
        threading.Thread(target=self.receber_mensagens, daemon=True).start()
        threading.Thread(target=self.gerenciar_exclusao_mutua, daemon=True).start()
        self.interface_terminal()

if __name__ == "__main__":
    coordenador = Coordenador()
    coordenador.iniciar()
