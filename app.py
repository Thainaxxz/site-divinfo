from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            STATUS TEXT NOT NULL DEFAULT 'Aberto',
            prioridade TEXT NOT NULL DEFAULT 'Média',
            criado_por INTEGER NOT NULL,
            atribuido_para INTEGER NOT NULL,
            FOREIGN KEY(criado_por) REFERENCES usuarios(id),
            FOREIGN KEY(atribuido_para) REFERENCES usuarios(id)
        )
    """)

    conexao.commit()
    conexao.close()

criar_banco()
    

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
        session["usuario_id"] = usuario[0]
        session["usuario"] = usuario[1]
        return redirect(url_for("chamados"))
    else:
        return "Email ou senha incorretos."


@app.route("/chamados")
def chamados():
    if "usuario_id" not in session:    
        return redirect(url_for("login"))

    conexao = sqlite3.connect("usuarios.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT 
            c.id,
            c.titulo,
            c.descricao,
            c.status,
            c.prioridade,   
            c.criado_por,
            c.atribuido_para,
            u1.usuario AS criador,
            u2.usuario AS atribuido
        FROM chamados c
        JOIN usuarios u1 ON c.criado_por = u1.id
        JOIN usuarios u2 ON c.atribuido_para = u2.id
        ORDER BY c.id DESC
    """)

    chamados = cursor.fetchall()

    cursor.execute("SELECT id, usuario FROM usuarios ORDER BY usuario")
    usuarios = cursor.fetchall()

    conexao.close()

    return render_template("chamados.html", chamados=chamados, usuarios=usuarios)


@app.route("/criar_chamado", methods=["POST"])
def criar_chamado():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    titulo = request.form["titulo"]
    descricao = request.form["descricao"]
    status = request.form["status"]
    prioridade = request.form["prioridade"]
    criado_por = session["usuario_id"]
    atribuido_para = request.form["atribuido_para"]
    
    

    conexao = sqlite3.connect("usuarios.db")
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO chamados (titulo, descricao, status, prioridade, criado_por, atribuido_para)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (titulo, descricao, status, prioridade, criado_por, atribuido_para))

    conexao.commit()
    conexao.close()

    return redirect(url_for("chamados"))



@app.route("/atualizar_chamado/<int:id>", methods=["POST"])
def atualizar_chamado(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = sqlite3.connect("usuarios.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT criado_por FROM chamados WHERE id = ?", (id,))
    chamado = cursor.fetchone()

    if not chamado:
        conexao.close()
        return "Chamado não encontrado."

    if chamado[0] != session["usuario_id"]:
        conexao.close()
        return "Você não tem permissão para editar este chamado."

    titulo = request.form["titulo"]
    descricao = request.form["descricao"]
    status = request.form["status"]
    prioridade = request.form["prioridade"]
    atribuido_para = request.form["atribuido_para"]

    cursor.execute("""
        UPDATE chamados
        SET titulo = ?, descricao = ?, status = ?, prioridade = ?, atribuido_para = ?
        WHERE id = ?
    """, (titulo, descricao, status, prioridade, atribuido_para, id))

    conexao.commit()
    conexao.close()

    return redirect(url_for("chamados"))

@app.route("/editar_chamado/<int:id>", methods=["POST"])
def editar_chamado(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = sqlite3.connect("usuarios.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT criado_por FROM chamados WHERE id = ?", (id,))
    chamado = cursor.fetchone()

    if not chamado:
        conexao.close()
        return "Chamado não encontrado."

    if chamado[0] != session["usuario_id"]:
        conexao.close()
        return "Você não tem permissão para editar este chamado."

    titulo = request.form["titulo"]
    descricao = request.form["descricao"]
    status = request.form["status"]
    prioridade = request.form["prioridade"]
    atribuido_para = request.form["atribuido_para"]

    cursor.execute("""
        UPDATE chamados
        SET titulo = ?, descricao = ?, status = ?, prioridade = ?, atribuido_para = ?
        WHERE id = ?
    """, (titulo, descricao, status, prioridade, atribuido_para, id))

    conexao.commit()
    conexao.close()

    return redirect(url_for("chamados"))


@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    session.pop("usuario", None)
    return redirect(url_for("login"))




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)