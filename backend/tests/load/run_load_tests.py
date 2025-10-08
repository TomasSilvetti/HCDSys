"""
Script para ejecutar pruebas de carga y generar informes
"""
import os
import sys
import subprocess
import argparse
import json
import time
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# Configuración de rutas
SCRIPT_DIR = Path(__file__).parent
REPORTS_DIR = SCRIPT_DIR / "reports"
LOCUSTFILE = SCRIPT_DIR / "locustfile.py"

def setup_environment():
    """
    Configurar el entorno para las pruebas
    """
    # Crear directorio de informes si no existe
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # Verificar que locust está instalado
    try:
        subprocess.run(["locust", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Locust no está instalado o no está en el PATH.")
        print("Instala las dependencias con: pip install -r requirements.txt")
        sys.exit(1)

def run_load_test(users, spawn_rate, runtime, host):
    """
    Ejecutar la prueba de carga con los parámetros especificados
    
    Args:
        users: Número máximo de usuarios concurrentes
        spawn_rate: Tasa de generación de usuarios por segundo
        runtime: Duración de la prueba en segundos
        host: URL del host a probar
    
    Returns:
        Path al archivo CSV con los resultados
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = REPORTS_DIR / f"results_{timestamp}.csv"
    
    print(f"\n{'=' * 80}")
    print(f"Iniciando prueba de carga con {users} usuarios, tasa de {spawn_rate}/s, duración {runtime}s")
    print(f"Host: {host}")
    print(f"{'=' * 80}\n")
    
    # Comando para ejecutar locust en modo headless
    cmd = [
        "locust",
        "-f", str(LOCUSTFILE),
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", f"{runtime}s",
        "--headless",
        "--csv", str(csv_file.with_suffix('')),  # Locust añade _stats.csv automáticamente
        "--html", str(REPORTS_DIR / f"report_{timestamp}.html")
    ]
    
    # Ejecutar locust
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Mostrar salida en tiempo real
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode != 0:
            print(f"Error: La prueba de carga falló con código de salida {process.returncode}")
            return None
        
        return csv_file.with_suffix('_stats.csv')
    
    except Exception as e:
        print(f"Error al ejecutar la prueba de carga: {str(e)}")
        return None

def generate_report(csv_file):
    """
    Generar un informe con gráficos a partir de los resultados CSV
    
    Args:
        csv_file: Ruta al archivo CSV con los resultados
    """
    if not csv_file or not os.path.exists(csv_file):
        print("No se encontró el archivo de resultados.")
        return
    
    try:
        # Cargar datos
        df = pd.read_csv(csv_file)
        
        # Crear gráficos
        plt.figure(figsize=(12, 8))
        
        # Gráfico 1: Tiempo de respuesta
        plt.subplot(2, 2, 1)
        plt.plot(df['Name'], df['Median Response Time'], 'b-', label='Mediana')
        plt.plot(df['Name'], df['95%'], 'r-', label='95%')
        plt.xticks(rotation=45, ha='right')
        plt.title('Tiempos de Respuesta')
        plt.ylabel('Tiempo (ms)')
        plt.legend()
        plt.grid(True)
        
        # Gráfico 2: Tasa de solicitudes
        plt.subplot(2, 2, 2)
        plt.bar(df['Name'], df['Requests/s'], color='green')
        plt.xticks(rotation=45, ha='right')
        plt.title('Tasa de Solicitudes')
        plt.ylabel('Solicitudes/s')
        plt.grid(True)
        
        # Gráfico 3: Tasa de errores
        plt.subplot(2, 2, 3)
        plt.bar(df['Name'], df['Failure Count'], color='red')
        plt.xticks(rotation=45, ha='right')
        plt.title('Errores')
        plt.ylabel('Número de errores')
        plt.grid(True)
        
        # Gráfico 4: Resumen
        plt.subplot(2, 2, 4)
        plt.bar(['Total', 'Éxito', 'Error'], 
                [df['# requests'].sum(), df['# requests'].sum() - df['Failure Count'].sum(), df['Failure Count'].sum()],
                color=['blue', 'green', 'red'])
        plt.title('Resumen de Solicitudes')
        plt.ylabel('Número de solicitudes')
        plt.grid(True)
        
        plt.tight_layout()
        
        # Guardar gráficos
        report_file = csv_file.replace('_stats.csv', '_report.png')
        plt.savefig(report_file)
        print(f"\nInforme gráfico guardado en: {report_file}")
        
        # Generar resumen en texto
        summary = {
            "total_requests": int(df['# requests'].sum()),
            "failed_requests": int(df['Failure Count'].sum()),
            "success_rate": float(1 - df['Failure Count'].sum() / df['# requests'].sum()) * 100 if df['# requests'].sum() > 0 else 0,
            "avg_response_time": float(df['Average Response Time'].mean()),
            "median_response_time": float(df['Median Response Time'].mean()),
            "95_percentile": float(df['95%'].mean()),
            "requests_per_second": float(df['Requests/s'].sum())
        }
        
        summary_file = csv_file.replace('_stats.csv', '_summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Resumen guardado en: {summary_file}")
        print("\nResumen de resultados:")
        print(f"  Total de solicitudes: {summary['total_requests']}")
        print(f"  Solicitudes fallidas: {summary['failed_requests']}")
        print(f"  Tasa de éxito: {summary['success_rate']:.2f}%")
        print(f"  Tiempo de respuesta promedio: {summary['avg_response_time']:.2f} ms")
        print(f"  Tiempo de respuesta mediana: {summary['median_response_time']:.2f} ms")
        print(f"  Percentil 95: {summary['95_percentile']:.2f} ms")
        print(f"  Solicitudes por segundo: {summary['requests_per_second']:.2f}")
        
    except Exception as e:
        print(f"Error al generar el informe: {str(e)}")

def run_stress_test(host, max_users=1000, step=100, target_rps=None):
    """
    Ejecutar una prueba de estrés incremental para encontrar el límite del sistema
    
    Args:
        host: URL del host a probar
        max_users: Número máximo de usuarios a probar
        step: Incremento de usuarios en cada paso
        target_rps: Tasa objetivo de solicitudes por segundo
    """
    print(f"\n{'=' * 80}")
    print(f"Iniciando prueba de estrés incremental")
    print(f"Host: {host}")
    print(f"Usuarios máximos: {max_users}, Incremento: {step}")
    print(f"{'=' * 80}\n")
    
    results = []
    
    for users in range(step, max_users + step, step):
        print(f"\nPrueba con {users} usuarios concurrentes:")
        
        # Ejecutar prueba con este número de usuarios
        csv_file = run_load_test(users, spawn_rate=users/10, runtime=30, host=host)
        
        if not csv_file or not os.path.exists(csv_file):
            print(f"La prueba con {users} usuarios falló. Deteniendo prueba de estrés.")
            break
        
        # Analizar resultados
        df = pd.read_csv(csv_file)
        
        # Calcular métricas clave
        total_rps = df['Requests/s'].sum()
        avg_response_time = df['Average Response Time'].mean()
        error_rate = df['Failure Count'].sum() / df['# requests'].sum() if df['# requests'].sum() > 0 else 0
        
        results.append({
            "users": users,
            "rps": total_rps,
            "avg_response_time": avg_response_time,
            "error_rate": error_rate * 100
        })
        
        print(f"  Usuarios: {users}")
        print(f"  RPS total: {total_rps:.2f}")
        print(f"  Tiempo de respuesta promedio: {avg_response_time:.2f} ms")
        print(f"  Tasa de error: {error_rate * 100:.2f}%")
        
        # Verificar si hemos alcanzado el límite
        if error_rate > 0.1:  # Más del 10% de errores
            print(f"\n¡LÍMITE ALCANZADO! La tasa de error supera el 10% con {users} usuarios.")
            break
            
        if avg_response_time > 2000:  # Tiempo de respuesta superior a 2 segundos
            print(f"\n¡LÍMITE ALCANZADO! El tiempo de respuesta supera los 2 segundos con {users} usuarios.")
            break
            
        if target_rps and total_rps >= target_rps:
            print(f"\n¡OBJETIVO ALCANZADO! Se ha alcanzado la tasa objetivo de {target_rps} RPS con {users} usuarios.")
            break
    
    # Generar informe de la prueba de estrés
    if results:
        df_results = pd.DataFrame(results)
        
        plt.figure(figsize=(12, 8))
        
        # Gráfico 1: RPS vs Usuarios
        plt.subplot(2, 2, 1)
        plt.plot(df_results['users'], df_results['rps'], 'b-o')
        plt.title('Solicitudes por segundo vs Usuarios')
        plt.xlabel('Usuarios concurrentes')
        plt.ylabel('Solicitudes/s')
        plt.grid(True)
        
        # Gráfico 2: Tiempo de respuesta vs Usuarios
        plt.subplot(2, 2, 2)
        plt.plot(df_results['users'], df_results['avg_response_time'], 'r-o')
        plt.title('Tiempo de respuesta vs Usuarios')
        plt.xlabel('Usuarios concurrentes')
        plt.ylabel('Tiempo de respuesta (ms)')
        plt.grid(True)
        
        # Gráfico 3: Tasa de error vs Usuarios
        plt.subplot(2, 2, 3)
        plt.plot(df_results['users'], df_results['error_rate'], 'g-o')
        plt.title('Tasa de error vs Usuarios')
        plt.xlabel('Usuarios concurrentes')
        plt.ylabel('Tasa de error (%)')
        plt.grid(True)
        
        plt.tight_layout()
        
        # Guardar gráficos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = REPORTS_DIR / f"stress_test_report_{timestamp}.png"
        plt.savefig(report_file)
        
        # Guardar resultados en CSV
        csv_file = REPORTS_DIR / f"stress_test_results_{timestamp}.csv"
        df_results.to_csv(csv_file, index=False)
        
        print(f"\nInforme de prueba de estrés guardado en: {report_file}")
        print(f"Resultados detallados guardados en: {csv_file}")
        
        # Determinar el límite del sistema
        if len(results) > 1:
            max_users_stable = results[-2]['users']  # El último punto estable
            max_rps_stable = results[-2]['rps']
            print(f"\nLímite del sistema:")
            print(f"  Usuarios concurrentes máximos: {max_users_stable}")
            print(f"  RPS máximo estable: {max_rps_stable:.2f}")
        else:
            print("\nNo se pudo determinar el límite del sistema. Intente con valores iniciales más bajos.")

def main():
    """
    Función principal
    """
    parser = argparse.ArgumentParser(description="Ejecutar pruebas de carga y estrés")
    parser.add_argument("--host", default="http://localhost:8000", help="URL del host a probar")
    parser.add_argument("--users", type=int, default=100, help="Número de usuarios concurrentes")
    parser.add_argument("--spawn-rate", type=int, default=10, help="Tasa de generación de usuarios por segundo")
    parser.add_argument("--runtime", type=int, default=60, help="Duración de la prueba en segundos")
    parser.add_argument("--stress", action="store_true", help="Ejecutar prueba de estrés incremental")
    parser.add_argument("--max-users", type=int, default=1000, help="Número máximo de usuarios para la prueba de estrés")
    parser.add_argument("--step", type=int, default=100, help="Incremento de usuarios en cada paso de la prueba de estrés")
    parser.add_argument("--target-rps", type=int, help="Tasa objetivo de solicitudes por segundo para la prueba de estrés")
    
    args = parser.parse_args()
    
    # Configurar entorno
    setup_environment()
    
    if args.stress:
        # Ejecutar prueba de estrés
        run_stress_test(args.host, args.max_users, args.step, args.target_rps)
    else:
        # Ejecutar prueba de carga
        csv_file = run_load_test(args.users, args.spawn_rate, args.runtime, args.host)
        
        if csv_file:
            # Generar informe
            generate_report(csv_file)

if __name__ == "__main__":
    main()
