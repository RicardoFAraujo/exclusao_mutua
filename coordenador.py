import socket
import threading
import queue
import time

class Coordenador:
    def __init__(self, host='localhost', porta=5000):
        self.host = host
        self.porta = porta
        self.fila_pedidos = queue.Queue()
        self.atendimentos = {}
        self.lock = threading.Lock()
        self.rodando = True
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.porta))
        self.server_socket.listen(5)
        
        print(f'Coordenador ouvindo em {self.host}:{self.porta}')
        
    def log(self, mensagem):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with open("log_coordenador.txt", "a") as f:
            f.write(f'[{timestamp}] {mensagem}\n')
        print(f'[{timestamp}] {mensagem}')
        
    def receber_conexoes(self):
        while self.rodando:
            try:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self.tratar_mensagem, args=(conn,)).start()
            except socket.error:
                break
        
    def tratar_mensagem(self, conn):
        try:
            while self.rodando:
                mensagem = conn.recv(1024).decode()
                if not mensagem:
                    break
                
                self.log(f'Recebido: {mensagem}')
                partes = mensagem.split()
                
                if partes[0] == "REQUEST":
                    processo_id = partes[1]
                    with self.lock:
                        self.fila_pedidos.put(processo_id)
                    self.log(f'Processo {processo_id} adicionou pedido na fila')
                
                elif partes[0] == "RELEASE":
                    processo_id = partes[1]
                    with self.lock:
                        if not self.fila_pedidos.empty() and self.fila_pedidos.queue[0] == processo_id:
                            self.fila_pedidos.get()
                            self.atendimentos[processo_id] = self.atendimentos.get(processo_id, 0) + 1
                            self.log(f'Processo {processo_id} liberou a região crítica')
                
        except Exception as e:
            self.log(f'Erro: {e}')
        finally:
            conn.close()
    
    def gerenciar_exclusao_mutua(self):
        while self.rodando:
            with self.lock:
                if not self.fila_pedidos.empty():
                    processo_atual = self.fila_pedidos.queue[0]
                    self.log(f'Concedendo acesso ao Processo {processo_atual}')
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
        threading.Thread(target=self.receber_conexoes, daemon=True).start()
        threading.Thread(target=self.gerenciar_exclusao_mutua, daemon=True).start()
        self.interface_terminal()

if __name__ == "__main__":
    coordenador = Coordenador()
    coordenador.iniciar()
