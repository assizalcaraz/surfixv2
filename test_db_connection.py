#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos PostgreSQL
"""
import psycopg2
import os
import sys

def test_connection():
    """Prueba la conexión a PostgreSQL con diferentes configuraciones"""
    
    # Configuraciones a probar
    configs = [
        {
            'name': 'Configuración desde variables de entorno',
            'host': os.getenv('POSTGRES_HOST', 'db'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'surfix'),
            'user': os.getenv('POSTGRES_USER', 'surfix_user'),
            'password': os.getenv('POSTGRES_PASSWORD', '7f5Ejrhf4BGJD0mmullI6wZzh')
        },
        {
            'name': 'Configuración hardcodeada',
            'host': 'db',
            'port': '5432',
            'database': 'surfix',
            'user': 'surfix_user',
            'password': '7f5Ejrhf4BGJD0mmullI6wZzh'
        },
        {
            'name': 'Configuración con host localhost',
            'host': 'localhost',
            'port': '5432',
            'database': 'surfix',
            'user': 'surfix_user',
            'password': '7f5Ejrhf4BGJD0mmullI6wZzh'
        }
    ]
    
    for config in configs:
        print(f"\n🔍 Probando: {config['name']}")
        print(f"   Host: {config['host']}")
        print(f"   Port: {config['port']}")
        print(f"   Database: {config['database']}")
        print(f"   User: {config['user']}")
        
        try:
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password']
            )
            print("   ✅ Conexión exitosa!")
            
            # Probar una consulta simple
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"   📊 PostgreSQL version: {version[:50]}...")
            
            cursor.close()
            conn.close()
            
        except psycopg2.OperationalError as e:
            print(f"   ❌ Error de conexión: {e}")
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")

if __name__ == "__main__":
    print("🧪 Probando conexiones a PostgreSQL...")
    test_connection()
