#!/usr/bin/env python
"""
Script para probar la funcionalidad de búsqueda de documentos desde la línea de comandos.
Permite verificar si hay problemas con caracteres especiales o con la configuración CORS.

Uso:
    python test_search.py --term "término de búsqueda" --token "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGVfaWQiOjEsImV4cCI6MTc2MDEyODQ1OX0.tJsq8YuKF8pMXLllAzOxFb2AxOeNhaRGO6XOjzFn2_o"
"""

import argparse
import json
import requests
import sys
from urllib.parse import quote

def main():
    parser = argparse.ArgumentParser(description='Probar la búsqueda de documentos')
    parser.add_argument('--term', type=str, required=True, help='Término de búsqueda')
    parser.add_argument('--token', type=str, default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGVfaWQiOjEsImV4cCI6MTcyODQyMjQwMH0.n8O1BXkgOsjwNbIbFMnNJC9EzN9kSGAjUCJmGM4WIpM", help='Token JWT de autenticación')
    parser.add_argument('--url', type=str, default='http://localhost:8000', help='URL base de la API')
    parser.add_argument('--diagnostics', action='store_true', help='Usar ruta de diagnóstico en lugar de búsqueda real')
    args = parser.parse_args()

    # Configurar encabezados con token JWT
    headers = {
        'Authorization': f'Bearer {args.token}',
        'Content-Type': 'application/json'
    }

    # Determinar la URL a usar
    if args.diagnostics:
        url = f"{args.url}/api/documents/diagnostics/search?termino={quote(args.term)}"
        print(f"Realizando diagnóstico de búsqueda con término: '{args.term}'")
    else:
        url = f"{args.url}/api/documents?termino={quote(args.term)}&page=1&sort_by=fecha_modificacion&sort_order=desc"
        print(f"Realizando búsqueda con término: '{args.term}'")

    try:
        # Realizar la solicitud HTTP
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        
        response = requests.get(url, headers=headers)
        
        # Verificar el código de estado
        print(f"Código de estado: {response.status_code}")
        
        # Mostrar encabezados de respuesta
        print("\nEncabezados de respuesta:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
        
        # Intentar parsear la respuesta como JSON
        try:
            data = response.json()
            print("\nRespuesta JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("\nLa respuesta no es un JSON válido:")
            print(response.text[:500])  # Mostrar solo los primeros 500 caracteres
        
        # Si es una búsqueda normal, mostrar estadísticas
        if not args.diagnostics and response.status_code == 200:
            data = response.json()
            print(f"\nEstadísticas de búsqueda:")
            print(f"  Total de documentos: {data.get('total', 'N/A')}")
            print(f"  Página actual: {data.get('page', 'N/A')}")
            print(f"  Total de páginas: {data.get('total_pages', 'N/A')}")
            print(f"  Documentos en esta página: {len(data.get('items', []))}")
            
            # Mostrar títulos de documentos encontrados
            if 'items' in data and data['items']:
                print("\nDocumentos encontrados:")
                for i, doc in enumerate(data['items'], 1):
                    print(f"  {i}. {doc.get('titulo', 'Sin título')} (ID: {doc.get('id', 'N/A')})")
            else:
                print("\nNo se encontraron documentos que coincidan con la búsqueda.")
        
    except requests.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
