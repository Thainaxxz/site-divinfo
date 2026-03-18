from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "chave-secreta-teste"


def criar_banco():
    conexao = sqlite3.connect("usuarios.db")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    usuario = request.form["usuario"]
    email = request.form["email"]
    senha = request.form["senha"]

    try:
        conexao = sqlite3.connect("usuarios.db")
        cursor = conexao.cursor()

        cursor.execute(
            "INSERT INTO usuarios (usuario, email, senha) VALUES (?, ?, ?)",
            (usuario, email, senha)
        )

        conexao.commit()
        conexao.close()

        return redirect(url_for("login"))

    except sqlite3.IntegrityError:
        return "Esse email já está cadastrado."


@app.route("/autenticar", methods=["POST"])
def autenticar():
    email = request.form["email"]
    senha = request.form["senha"]

    conexao = sqlite3.connect("usuarios.db")
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE email = ? AND senha = ?",
        (email, senha)
    )

    usuario = cursor.fetchone()
    conexao.close()

    if usuario:
        session["usuario"] = usuario[1]
        return redirect(url_for("painel"))
    else:
        return "Email ou senha incorretos."


@app.route("/painel")
def painel():
    if "usuario" in session:
        return f"Bem-vinda, {session['usuario']}! Login feito com sucesso."
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)