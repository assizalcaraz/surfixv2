#!/usr/bin/env python3
"""
Script para inicializar la base de datos PostgreSQL correctamente
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def init_database():
    """Inicializa la base de datos y usuario"""
    
    # Conectar como superusuario postgres
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'db'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database='postgres',  # Base de datos por defecto
            user='postgres',      # Usuario superusuario
            password=os.getenv('POSTGRES_PASSWORD', '7f5Ejrhf4BGJD0mmullI6wZzh')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Conectado como superusuario postgres")
        
        # Crear usuario si no existe
        db_name = os.getenv('POSTGRES_DB', 'surfix')
        db_user = os.getenv('POSTGRES_USER', 'surfix_user')
        db_password = os.getenv('POSTGRES_PASSWORD', '7f5Ejrhf4BGJD0mmullI6wZzh')
        
        print(f"🔧 Creando usuario {db_user}...")
        cursor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{db_user}') THEN
                    CREATE USER {db_user} WITH PASSWORD '{db_password}';
                END IF;
            END
            $$;
        """)
        
        # Crear base de datos si no existe
        print(f"🔧 Creando base de datos {db_name}...")
        cursor.execute(f"""
            SELECT 'CREATE DATABASE {db_name} OWNER {db_user}'
            WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{db_name}')\\gexec
        """)
        
        # Otorgar privilegios
        print(f"🔧 Otorgando privilegios a {db_user}...")
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
        cursor.execute(f"ALTER USER {db_user} CREATEDB;")
        
        cursor.close()
        conn.close()
        
        print("✅ Base de datos inicializada correctamente")
        
        # Probar conexión con el usuario creado
        print(f"🧪 Probando conexión con usuario {db_user}...")
        test_conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'db'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=db_name,
            user=db_user,
            password=db_password
        )
        test_conn.close()
        print("✅ Conexión con usuario creado exitosa")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión: {e}")
        print("💡 Asegúrate de que PostgreSQL esté ejecutándose y las credenciales sean correctas")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    print("🚀 Inicializando base de datos PostgreSQL...")
    init_database()
