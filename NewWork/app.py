from flask import Flask, request, jsonify
from flask_cors import CORS
from database.database import get_db
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

app = Flask(__name__)
CORS(app)

SECRET = "chave-secreta-rental"


# =========================
# JWT
# =========================

def token_required(f):
    @wraps(f)
    def verificar(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not token:
            return jsonify({"erro": "Token não informado"}), 401

        try:
            jwt.decode(token, SECRET, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido ou expirado"}), 401

        return f(*args, **kwargs)

    return verificar


# =========================
# INÍCIO
# =========================

@app.route("/")
def inicio():
    return "Rental Events funcionando!"


# =========================
# TESTE DO BANCO
# =========================

@app.route("/teste-banco")
def teste_banco():
    conn = get_db()
    resultado = conn.run("SELECT * FROM equipamento")
    conn.close()

    return jsonify(resultado)


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["POST"])
def login():
    dados = request.json
    conn = get_db()

    usuario = conn.run(
        """
        SELECT id, username
        FROM usuario
        WHERE email = :email AND senha = :senha
        """,
        email=dados["email"],
        senha=dados["senha"]
    )

    conn.close()

    if not usuario:
        return jsonify({"erro": "Email ou senha inválidos"}), 401

    token = jwt.encode(
        {
            "id": usuario[0][0],
            "username": usuario[0][1],
            "exp": datetime.now(timezone.utc) + timedelta(hours=2)
        },
        SECRET,
        algorithm="HS256"
    )

    return jsonify({"token": token})


# =========================
# EQUIPAMENTOS
# =========================

@app.route("/equipamentos", methods=["GET"])
@token_required
def listar_equipamentos():
    conn = get_db()

    equipamentos = conn.run(
        """
        SELECT id, nome, categoria_id, marca, cor, dimensao,
               modelo, potencia, material, peso,
               estoque_atual, estoque_minimo
        FROM equipamento
        ORDER BY id
        """
    )

    conn.close()

    campos = [
        "id", "nome", "categoria_id", "marca", "cor",
        "dimensao", "modelo", "potencia", "material",
        "peso", "estoque_atual", "estoque_minimo"
    ]

    return jsonify([
        dict(zip(campos, equipamento))
        for equipamento in equipamentos
    ])


# =========================
# CADASTRAR EQUIPAMENTO
# =========================

@app.route("/equipamentos", methods=["POST"])
@token_required
def cadastrar_equipamento():
    dados = request.json
    conn = get_db()

    conn.run(
        """
        INSERT INTO equipamento
        (
            nome, categoria_id, marca, cor, dimensao,
            modelo, potencia, material, peso,
            estoque_atual, estoque_minimo
        )
        VALUES
        (
            :nome, :categoria, :marca, :cor, :dimensao,
            :modelo, :potencia, :material, :peso,
            :estoque, :minimo
        )
        """,
        nome=dados["nome"],
        categoria=dados["categoria_id"],
        marca=dados["marca"],
        cor=dados["cor"],
        dimensao=dados["dimensao"],
        modelo=dados["modelo"],
        potencia=dados["potencia"],
        material=dados["material"],
        peso=dados["peso"],
        estoque=dados["estoque_atual"],
        minimo=dados["estoque_minimo"]
    )

    conn.close()

    return jsonify({"mensagem": "Equipamento cadastrado"}), 201


# =========================
# EDITAR EQUIPAMENTO
# =========================

@app.route("/equipamentos/<int:id>", methods=["PUT"])
@token_required
def editar_equipamento(id):
    dados = request.json
    conn = get_db()

    conn.run(
        """
        UPDATE equipamento
        SET
            nome=:nome,
            categoria_id=:categoria,
            marca=:marca,
            cor=:cor,
            dimensao=:dimensao,
            modelo=:modelo,
            potencia=:potencia,
            material=:material,
            peso=:peso,
            estoque_atual=:estoque,
            estoque_minimo=:minimo
        WHERE id=:id
        """,
        nome=dados["nome"],
        categoria=dados["categoria_id"],
        marca=dados["marca"],
        cor=dados["cor"],
        dimensao=dados["dimensao"],
        modelo=dados["modelo"],
        potencia=dados["potencia"],
        material=dados["material"],
        peso=dados["peso"],
        estoque=dados["estoque_atual"],
        minimo=dados["estoque_minimo"],
        id=id
    )

    conn.close()

    return jsonify({"mensagem": "Equipamento atualizado"})


# =========================
# DELETAR EQUIPAMENTO
# =========================

@app.route("/equipamentos/<int:id>", methods=["DELETE"])
@token_required
def deletar_equipamento(id):
    conn = get_db()

    conn.run(
        "DELETE FROM equipamento WHERE id=:id",
        id=id
    )

    conn.close()

    return jsonify({"mensagem": "Equipamento deletado"})


# =========================
# CATEGORIAS
# =========================

@app.route("/categorias", methods=["GET"])
@token_required
def listar_categorias():
    conn = get_db()

    categorias = conn.run(
        "SELECT id, nome FROM categoria ORDER BY id"
    )

    conn.close()

    return jsonify([
        {
            "id": categoria[0],
            "nome": categoria[1]
        }
        for categoria in categorias
    ])


# =========================
# USUÁRIOS
# =========================

@app.route("/usuarios", methods=["GET"])
@token_required
def listar_usuarios():
    conn = get_db()

    usuarios = conn.run(
        "SELECT id, email, username FROM usuario ORDER BY id"
    )

    conn.close()

    return jsonify([
        {
            "id": usuario[0],
            "email": usuario[1],
            "username": usuario[2]
        }
        for usuario in usuarios
    ])


# =========================
# EXECUTAR
# =========================

if __name__ == "__main__":
    app.run(debug=True)
