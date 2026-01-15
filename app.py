from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "chave-secreta-carrinho"

ARQ_PRODUTOS = "produtos.json"


def carregar_produtos():
    if not os.path.exists(ARQ_PRODUTOS):
        return []
    with open(ARQ_PRODUTOS, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    produtos = carregar_produtos()
    carrinho = session.get("carrinho", [])
    return render_template("index.html", produtos=produtos, carrinho=carrinho)


@app.route("/add/<int:id_produto>")
def add(id_produto):
    produtos = carregar_produtos()
    carrinho = session.get("carrinho", [])

    produto = produtos[id_produto]
    carrinho.append(produto)

    session["carrinho"] = carrinho
    return redirect(url_for("index"))


@app.route("/finalizar")
def finalizar():
    carrinho = session.get("carrinho", [])

    if not carrinho:
        return redirect(url_for("index"))

    total = sum(float(p["preco"]) for p in carrinho)
    desconto = 10
    frete = 15

    total_final = total - desconto + frete

    mensagem = "Olá! Quero finalizar meu pedido:%0A%0A"

    for p in carrinho:
        mensagem += f"- {p['nome']} (R$ {p['preco']})%0A"

    mensagem += f"%0ATotal: R$ {total:.2f}"
    mensagem += f"%0ADesconto: R$ {desconto:.2f}"
    mensagem += f"%0AFrete: R$ {frete:.2f}"
    mensagem += f"%0ATotal final: R$ {total_final:.2f}"

    session["carrinho"] = []

    whatsapp = "5522981106356"

    return redirect(f"https://wa.me/{whatsapp}?text={mensagem}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
