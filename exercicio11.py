import random
import time
import argparse
import multiprocessing
import asyncio
import os
from datetime import datetime

# 1. Algoritmo Base (Worker)
def monte_carlo_worker(samples_partial):
    """Executa o cálculo de Monte Carlo para um bloco específico."""
    hits = 0
    for _ in range(samples_partial):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if x*x + y*y <= 1.0:
            hits += 1
    return hits

# 2. Monitoramento e Logging (Asyncio e I/O)
def write_log(progress):
    """Escreve o progresso no arquivo de log com Timestamp e PID."""
    with open("monte_carlo_progress.log", "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] Progresso: {progress:6.2f}% | PID Writer: {os.getpid()}\n")

async def async_monitor(task_id):
    """Tarefa assíncrona simulando rotinas de monitoramento."""
    while True:
        await asyncio.sleep(0.5) # Cede o controle ao Event Loop (Não bloqueante)

# 3. Orquestração Paralela
async def run_parallel(n_tasks, chunk_size):
    # Lança as 20 tarefas assíncronas concorrentes
    monitors = [asyncio.create_task(async_monitor(i)) for i in range(20)]

    pool = multiprocessing.Pool()
    
    # Dispara os blocos de forma assíncrona para o Pool (não bloqueia o loop)
    results = [pool.apply_async(monte_carlo_worker, (chunk_size,)) for _ in range(n_tasks)]
    
    tasks_completed = 0
    while tasks_completed < n_tasks:
        # Conta quantos chunks já retornaram resposta
        tasks_completed = sum(1 for r in results if r.ready())
        progress = (tasks_completed / n_tasks) * 100
        
        # Rotina de I/O
        write_log(progress)
        
        if tasks_completed == n_tasks:
            break
            
        # Ponto chave: Cede a CPU para que as 20 tarefas assíncronas executem
        await asyncio.sleep(0.1)

    pool.close()
    pool.join()

    # Cancela as tarefas de monitoramento após o fim do cálculo
    for m in monitors:
        m.cancel()

    return sum(r.get() for r in results)

# 4. Ponto de Entrada (CLI)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aproximação de Pi por Monte Carlo")
    parser.add_argument("--n_tasks", type=int, default=100, help="Número de blocos")
    parser.add_argument("--chunk_size", type=int, default=100000, help="Iterações por bloco")
    args = parser.parse_args()

    total_samples = args.n_tasks * args.chunk_size
    print(f"--- Iniciando Monte Carlo (Tasks: {args.n_tasks} | Chunk: {args.chunk_size} | Total: {total_samples}) ---")

    # A. Versão Serial
    print("\nExecutando versão Serial...")
    start_serial = time.perf_counter()
    hits_serial = monte_carlo_worker(total_samples)
    pi_serial = 4 * hits_serial / total_samples
    time_serial = time.perf_counter() - start_serial
    print(f"[Serial]   Pi: {pi_serial:.5f} | Tempo: {time_serial:.3f} s")

    # B. Versão Paralela
    print("\nExecutando versão Paralela...")
    open("monte_carlo_progress.log", "w").close() # Limpa o log anterior
    start_parallel = time.perf_counter()
    hits_parallel = asyncio.run(run_parallel(args.n_tasks, args.chunk_size))
    pi_parallel = 4 * hits_parallel / total_samples
    time_parallel = time.perf_counter() - start_parallel
    print(f"[Paralela] Pi: {pi_parallel:.5f} | Tempo: {time_parallel:.3f} s")
    
    print("\nVerifique o arquivo de log local para evidências de progresso.")
