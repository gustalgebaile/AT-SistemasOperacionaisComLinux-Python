import time
import threading
import multiprocessing
import asyncio

def tarefa_io():
    time.sleep(1)

async def tarefa_async():
    await asyncio.sleep(1)

# 1. Sequencial (Original)
def rodar_sequencial():
    for _ in range(4):
        tarefa_io()

# 2. Multithreading
def rodar_threads():
    threads = [threading.Thread(target=tarefa_io) for _ in range(4)]
    for t in threads: t.start()
    for t in threads: t.join()

# 3. Multiprocessing
def rodar_multiprocessing():
    processos = [multiprocessing.Process(target=tarefa_io) for _ in range(4)]
    for p in processos: p.start()
    for p in processos: p.join()

# 4. Asyncio
async def rodar_asyncio():
    await asyncio.gather(*(tarefa_async() for _ in range(4)))

if __name__ == "__main__":
    print("Iniciando testes (4 tarefas de 1 segundo)...\n")

    # Original
    inicio = time.perf_counter()
    rodar_sequencial()
    t_seq = time.perf_counter() - inicio
    print(f"Sequencial (Original) : {t_seq:.3f} s")

    # Multithreading
    inicio = time.perf_counter()
    rodar_threads()
    t_thr = time.perf_counter() - inicio
    print(f"Multithreading        : {t_thr:.3f} s")

    # Multiprocessing
    inicio = time.perf_counter()
    rodar_multiprocessing()
    t_mp = time.perf_counter() - inicio
    print(f"Processamento Paralelo: {t_mp:.3f} s")

    # Asyncio
    inicio = time.perf_counter()
    asyncio.run(rodar_asyncio())
    t_async = time.perf_counter() - inicio
    print(f"Asyncio               : {t_async:.3f} s")
