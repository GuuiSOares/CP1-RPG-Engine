import streamlit as st
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configuração da página
st.set_page_config(page_title="SQLgard", page_icon="⚔️")

def get_connection():
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN")
    )

st.title("⚔️ SQLgard: O Despertar do Kernel Ancestral")
st.write("A névoa venenosa avança. A cada turno, a vida dos heróis é drenada!")

def listar_herois():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Busca os heróis no banco
        cursor.execute("SELECT id_heroi, nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY id_heroi")
        
        # Pega o nome das colunas e os dados para montar a tabela
        colunas = [col[0] for col in cursor.description]
        dados = cursor.fetchall()
        
        # DataFrame do pandas para a tabela
        df = pd.DataFrame(dados, columns=colunas)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao conectar no banco de dados: {e}")
        st.info("Dica: Verifique se o seu arquivo .env está configurado corretamente e se as tabelas foram criadas.")

def processar_turno():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # O Bloco PL/SQL
        plsql_block = """
        DECLARE
            v_dano NUMBER := 10;
        BEGIN
            FOR r IN (SELECT id_heroi, hp_atual FROM TB_HEROIS WHERE status = 'ATIVO') LOOP
                IF r.hp_atual <= v_dano THEN
                    UPDATE TB_HEROIS SET hp_atual = 0, status = 'CAÍDO' WHERE id_heroi = r.id_heroi;
                ELSE
                    UPDATE TB_HEROIS SET hp_atual = hp_atual - v_dano WHERE id_heroi = r.id_heroi;
                END IF;
            END LOOP;
            COMMIT;
        END;
        """
        cursor.execute(plsql_block)
        conn.close()
        
        st.toast("A névoa avançou... O tempo passou em SQLgard!", icon="☠️")
    except Exception as e:
        st.error(f"Erro ao processar o turno: {e}")

def resetar_herois():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Restaura a vida
        sql = "UPDATE TB_HEROIS SET hp_atual = hp_max, status = 'ATIVO'"
        cursor.execute(sql)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        st.toast("Heróis curados! O jogo recomeçou.", icon="✨")
    except Exception as e:
        st.error(f"Erro ao resetar os heróis: {e}")


st.subheader("🛡️ Estado Atual dos Heróis")
listar_herois()

st.divider()

# Cria duas colunas para colocar os botões lado a lado
col1, col2 = st.columns(2)

with col1:
    if st.button("⏳ Próximo Turno", type="primary", use_container_width=True):
        processar_turno()
        st.rerun() 

with col2:
    if st.button("🔄 Resetar Heróis", use_container_width=True):
        resetar_herois()
        st.rerun()