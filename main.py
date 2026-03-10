from flask import Flask, render_template_string, redirect, url_for, flash
import oracledb
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = "chave_secreta_sqlgard" # Exibir mensagens na tela

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>SQLgard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #ffffff; text-align: center; padding: 40px; }
        table { margin: 0 auto; border-collapse: collapse; width: 80%; max-width: 800px; background-color: #2d2d2d; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
        th, td { border: 1px solid #444; padding: 12px; }
        th { background-color: #007acc; color: white; }
        .btn { padding: 12px 24px; margin: 15px 10px; cursor: pointer; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; transition: 0.3s; }
        .btn-primary { background-color: #d9534f; color: white; }
        .btn-primary:hover { background-color: #c9302c; }
        .btn-secondary { background-color: #5bc0de; color: white; }
        .btn-secondary:hover { background-color: #31b0d5; }
        .toast { color: #5cb85c; font-weight: bold; font-size: 1.2em; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>⚔️ SQLgard: O Despertar do Kernel Ancestral</h1>
    <p>A névoa venenosa avança. A cada turno, a vida dos heróis é drenada!</p>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="toast">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <h2>🛡️ Estado Atual dos Heróis</h2>
    <table>
        <tr>
            <th>ID</th><th>Nome</th><th>Classe</th><th>HP Atual</th><th>HP Máximo</th><th>Status</th>
        </tr>
        {% for heroi in herois %}
        <tr>
            <td>{{ heroi[0] }}</td><td>{{ heroi[1] }}</td><td>{{ heroi[2] }}</td>
            <td><strong>{{ heroi[3] }}</strong></td><td>{{ heroi[4] }}</td>
            <td style="color: {% if heroi[5] == 'CAÍDO' %}#d9534f{% else %}#5cb85c{% endif %}; font-weight: bold;">
                {{ heroi[5] }}
            </td>
        </tr>
        {% endfor %}
    </table>

    <br>
    <form action="/processar" method="POST" style="display:inline;">
        <button type="submit" class="btn btn-primary">⏳ Próximo Turno</button>
    </form>
    
    <form action="/resetar" method="POST" style="display:inline;">
        <button type="submit" class="btn btn-secondary">🔄 Resetar Heróis</button>
    </form>
</body>
</html>
"""

def get_connection():
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN")
    )

@app.route('/')
def index():
    herois = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_heroi, nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY id_heroi")
        herois = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f"Erro ao conectar no banco de dados: {e}")
    
    # Renderiza o HTML passando a lista de heróis
    return render_template_string(HTML_TEMPLATE, herois=herois)

# Avançar o turno (Ação do botão)
@app.route('/processar', methods=['POST'])
def processar():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Bloco PL/SQL
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
        flash("☠️ A névoa avançou... O tempo passou em SQLgard!")
    except Exception as e:
        flash(f"Erro ao processar o turno: {e}")
    
    return redirect(url_for('index'))

# Resetar (Ação do botão)
@app.route('/resetar', methods=['POST'])
def resetar():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE TB_HEROIS SET hp_atual = hp_max, status = 'ATIVO'")
        conn.commit()
        cursor.close()
        conn.close()
        flash("✨ Heróis curados! O jogo recomeçou.")
    except Exception as e:
        flash(f"Erro ao resetar os heróis: {e}")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)