# Pruebas de Carga y Estrés para HCDSys

Este directorio contiene herramientas y scripts para realizar pruebas de carga y estrés en el sistema HCDSys.

## Herramientas Disponibles

Se incluyen dos herramientas principales para realizar las pruebas:

1. **Locust**: Herramienta de pruebas de carga basada en Python, fácil de usar y extensible.
2. **JMeter**: Herramienta más completa y robusta para pruebas de carga y rendimiento.

## Requisitos Previos

### Para Locust:
- Python 3.8+
- Dependencias instaladas: `pip install -r requirements.txt`

### Para JMeter:
- Java Runtime Environment (JRE) 8+
- Apache JMeter instalado (https://jmeter.apache.org/download_jmeter.cgi)
- Variable de entorno `JMETER_HOME` configurada o JMeter en el PATH

## Configuración

Antes de ejecutar las pruebas, asegúrese de:

1. Tener un usuario de prueba creado en el sistema
2. Configurar las variables de entorno en un archivo `.env` en la raíz del proyecto:

```
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=password123
LOAD_TEST_BASE_URL=http://localhost:8000
```

## Ejecución de Pruebas con Locust

### Prueba de Carga Básica

```bash
python run_load_tests.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --runtime=60
```

Parámetros:
- `--host`: URL del host a probar
- `--users`: Número de usuarios concurrentes
- `--spawn-rate`: Tasa de generación de usuarios por segundo
- `--runtime`: Duración de la prueba en segundos

### Prueba de Estrés Incremental

```bash
python run_load_tests.py --host=http://localhost:8000 --stress --max-users=1000 --step=100
```

Parámetros adicionales:
- `--stress`: Activa el modo de prueba de estrés incremental
- `--max-users`: Número máximo de usuarios a probar
- `--step`: Incremento de usuarios en cada paso
- `--target-rps`: Tasa objetivo de solicitudes por segundo (opcional)

### Interfaz Web de Locust

También puede ejecutar Locust con su interfaz web:

```bash
locust -f locustfile.py --host=http://localhost:8000
```

Luego abra http://localhost:8089 en su navegador.

## Ejecución de Pruebas con JMeter

### Modo No-GUI (Recomendado para Pruebas Reales)

```bash
./run_jmeter_tests.sh localhost 8000 http 100 30 300
```

Parámetros:
1. Host (por defecto: localhost)
2. Puerto (por defecto: 8000)
3. Protocolo (por defecto: http)
4. Número de hilos/usuarios (por defecto: 100)
5. Tiempo de rampa en segundos (por defecto: 30)
6. Duración en segundos (por defecto: 300)

### Modo GUI (Para Desarrollo y Depuración)

```bash
jmeter -t hcdsys_test_plan.jmx
```

## Análisis de Resultados

### Locust
- Los resultados se guardan en el directorio `reports/`
- Se generan archivos CSV con estadísticas detalladas
- Se crean gráficos PNG para visualización rápida
- Se genera un resumen JSON con métricas clave

### JMeter
- Los resultados se guardan en el directorio `reports/`
- Se genera un archivo JTL con datos detallados
- Se crea un dashboard HTML completo con gráficos y análisis

## Interpretación de Resultados

Al analizar los resultados, preste especial atención a:

1. **Tiempo de respuesta promedio**: Idealmente por debajo de 200ms
2. **Percentil 95**: Indica la experiencia del 95% de los usuarios
3. **Tasa de error**: Debe ser inferior al 1% en condiciones normales
4. **Solicitudes por segundo (RPS)**: Indica la capacidad de procesamiento del sistema

## Recomendaciones

- Ejecute las pruebas en un entorno similar al de producción
- Realice pruebas incrementales para identificar límites
- Monitoree el uso de recursos del servidor durante las pruebas
- Compare resultados entre diferentes versiones del sistema

## Solución de Problemas

Si encuentra errores al ejecutar las pruebas:

1. Verifique que el servidor esté en ejecución y accesible
2. Asegúrese de que las credenciales de prueba sean correctas
3. Compruebe que las dependencias están instaladas correctamente
4. Revise los logs del servidor para identificar posibles cuellos de botella
