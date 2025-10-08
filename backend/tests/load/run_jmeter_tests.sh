#!/bin/bash

# Script para ejecutar pruebas de carga con JMeter

# Configuración
JMETER_HOME=${JMETER_HOME:-/opt/apache-jmeter}
TEST_PLAN="hcdsys_test_plan.jmx"
RESULTS_DIR="./reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="$RESULTS_DIR/results_$TIMESTAMP"
HOST=${1:-"localhost"}
PORT=${2:-"8000"}
PROTOCOL=${3:-"http"}
THREADS=${4:-"100"}
RAMP_UP=${5:-"30"}
DURATION=${6:-"300"}

# Crear directorio de resultados si no existe
mkdir -p "$RESULTS_DIR"

# Verificar que JMeter está instalado
if [ ! -f "$JMETER_HOME/bin/jmeter" ] && ! command -v jmeter &> /dev/null; then
    echo "Error: JMeter no está instalado o JMETER_HOME no está configurado correctamente."
    echo "Por favor, instala JMeter o configura la variable JMETER_HOME."
    exit 1
fi

# Determinar el comando de JMeter
if [ -f "$JMETER_HOME/bin/jmeter" ]; then
    JMETER_CMD="$JMETER_HOME/bin/jmeter"
else
    JMETER_CMD="jmeter"
fi

echo "==================================================="
echo "Iniciando pruebas de carga con JMeter"
echo "==================================================="
echo "Host: $PROTOCOL://$HOST:$PORT"
echo "Usuarios concurrentes: $THREADS"
echo "Tiempo de rampa: $RAMP_UP segundos"
echo "Duración: $DURATION segundos"
echo "Resultados: $RESULTS_FILE"
echo "==================================================="

# Ejecutar JMeter en modo no-GUI
$JMETER_CMD -n \
    -t "$TEST_PLAN" \
    -l "$RESULTS_FILE.jtl" \
    -e -o "$RESULTS_FILE-dashboard" \
    -Jhost=$HOST \
    -Jport=$PORT \
    -Jprotocol=$PROTOCOL \
    -JThreadGroup.threads=$THREADS \
    -JThreadGroup.ramp_time=$RAMP_UP \
    -JThreadGroup.duration=$DURATION

# Verificar si la prueba se ejecutó correctamente
if [ $? -eq 0 ]; then
    echo "==================================================="
    echo "Prueba completada con éxito."
    echo "Resultados guardados en: $RESULTS_FILE.jtl"
    echo "Dashboard HTML generado en: $RESULTS_FILE-dashboard"
    echo "==================================================="
else
    echo "==================================================="
    echo "Error al ejecutar la prueba."
    echo "==================================================="
    exit 1
fi
