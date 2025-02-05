import subprocess
import time

def iniciar_processos(n=5, repeticoes=3, tempo_espera=2):
    processos = []
    
    for i in range(1, n + 1):
        print(f"Iniciando Processo {i}...")
        p = subprocess.Popen(["py", "processo.py", str(i), str(repeticoes), str(tempo_espera)])
        processos.append(p)
        time.sleep(1)  # Pequeno atraso para evitar sobrecarga
    
    # Aguardar todos os processos terminarem
    for p in processos:
        p.wait()
    
    print("Todos os processos finalizaram.")

if __name__ == "__main__":
    iniciar_processos()
