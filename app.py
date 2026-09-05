from flask import Flask, render_template, request, url_for, redirect, session
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import sqlite3
import random
import smtplib
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("CHAVE")
banco = os.getenv("DATABASE_PATH")
emailk = os.getenv("EMAILKEY")
def conecta_banco():
    return sqlite3.connect(banco) 
c = conecta_banco()
cursor = c.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS registro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT NOT NULL,
        telefone INTEGER NOT NULL,
        livro TEXT, 
        retirado TEXT,
        devolvido TEXT
)
""")
c.commit()
c.close()
@app.route("/", methods=["GET", "POST"])
def registro():
    paragrafo = None
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            paragrafo = "Insira o email oficial da biblioteca"
        else:
                num = random.randint(10000, 99999)
                session["codigo_salvo"] = num
                mensagem = MIMEText(f"copie o código: {num}")
                mensagem["Subject"] = "Inicie a Sessão do Sistema Livrarin"
                mensagem["From"] = "ruanad040611@gmail.com"
                mensagem["To"] = f"{email}"
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login("ruanad040611@gmail.com", f"{emailk}")
                    smtp.send_message(mensagem)
                    return redirect(url_for("recebimento"))
    return render_template("registro.html", p=paragrafo)
@app.route("/recebido.html", methods=["GET", "POST"])
def recebimento():
    paragrafo = None
    if request.method == "POST": 
        entrada = request.form.get("entrada")
        if not entrada:
            paragrafo = "Insira o Código"
        elif str(entrada) != str(session.get("codigo_salvo")):
            paragrafo = "Código incorreto"
        else:
            return redirect(url_for("normal"))
    return render_template("recebido.html", p=paragrafo)
@app.route("/index.html", methods=["GET", "POST"])
def normal():
    paragrafo = None
    c = sqlite3.connect("Livrarin/banco.db")
    cursor = c.cursor()
    click = request.form.get("click")
    nome = request.form.get("nome")
    cpf = request.form.get("cpf")
    telefone = request.form.get("telefone")
    livro = request.form.get("livro")
    retirado = request.form.get("retirado")
    devolvido = request.form.get("devolvido")
    cpf_input = request.form.get("excluir_cpf")
    if click == "Colocar no sistema":
        if not nome or not cpf or not telefone or not livro or not retirado or not devolvido:
            paragrafo = "Existem campos vazios"
        else:
            cursor.execute("INSERT INTO registro (nome, cpf, telefone, livro, retirado, devolvido) VALUES (?, ?, ?, ?, ?, ?)", (nome, cpf, telefone, livro, retirado, devolvido))
            c.commit()
            paragrafo = "Novo REGISTRO!"
    elif click == "Excluir":
        cursor.execute("SELECT cpf FROM registro")
        confirma = [linha[0] for linha in cursor.fetchall()]
        if cpf_input not in confirma:
            paragrafo = "Cpf não está no sistema"
        else:
            cursor.execute("DELETE FROM registro WHERE cpf = ?", (cpf_input,))
            c.commit()
            paragrafo = "Registro apagado"
    cursor.execute("SELECT * FROM registro")
    mostra = cursor.fetchall()
    c.close()
    return render_template("index.html", p=paragrafo, dados=mostra)
if __name__ == "__main__":
    app.run()