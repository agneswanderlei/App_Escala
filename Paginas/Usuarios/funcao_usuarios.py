import os
import psycopg2
import streamlit as st

# --- Configurações do PostgreSQL ---
DB_HOST = "postgres"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD") or "postgres"
DB_PORT = 5432

def conecta_db():
    """Cria e retorna uma conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        st.error(f"❌ Erro de conexão com o PostgreSQL: {e}")
        return None

def inserir_user(nome, username, password, perfil):
    conn = conecta_db()
    if conn is None:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Usuarios 
                (nome, username, password, perfil)
                VALUES (%s, %s, %s, %s)
                """, (nome, username, password, perfil)
            )
            conn.commit()
            st.success('✅ Usuário gravado com sucesso!')
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        st.error(f'🚫 Usuário {username} já cadastrado.')
    except Exception as e:
        conn.rollback()
        st.error(f'❌ Não foi possível cadastrar o usuário: {e}')
    finally:
        if conn:
            conn.close()

def consulta_user():
    conn = conecta_db()
    if conn is None:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM Usuarios
                """
            )
            dados = cursor.fetchall()
            return dados
    except psycopg2.Error as e:
        st.error(f'❌ Erro ao consultar usuários: {e}')
        return []
    finally:
        if conn:
            conn.close()