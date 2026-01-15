from flask import Flask, render_template, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "chave-super-secreta"

ARQ_PRODUTOS = "produtos.json"


def carregar_produtos():
    if not os.path.exists(ARQ_PRODUTOS):
        return []
    with open(ARQ_PRODUTOS, "r", encoding="utf-8") as f:
        return json.load(f)


def preco_para_float(valor):
    if isinstance(valor, (int, float)):
        return float(valor)
    valor = valor.replace("R$", "").strip()
    valor = valor.replace(",", ".")
    return float(valor)


@app.route("/")
def index():
    produtos = carregar_produtos()
    carrinho = session.get("carrinho", [])
    return render_template("index.html", produtos=produtos, carrinho=carrinho)


@app.route("/add/<int:id_produto>")
def add(id_produto):
    produtos = carregar_produtos()
    carrinho = session.get("carrinho", [])

    if 0 <= id_produto < len(produtos):
        carrinho.append(produtos[id_produto])
        session["carrinho"] = carrinho

    return redirect(url_for("index"))


@app.route("/carrinho")
def carrinho():
    carrinho = session.get("carrinho", [])

    total = sum(preco_para_float(p["preco"]) for p in carrinho)

    return render_template("carrinho.html", carrinho=carrinho, total=total)


@app.route("/finalizar")
def finalizar():
    carrinho = session.get("carrinho", [])

    if not carrinho:
        return redirect(url_for("index"))

    total = sum(preco_para_float(p["preco"]) for p in carrinho)
    desconto = 10.0
    frete = 15.0
    total_final = total - desconto + frete

    msg = "Olá! Quero finalizar meu pedido:%0A%0A"
    for p in carrinho:
        msg += f"- {p['nome']} (R$ {p['preco']})%0A"

    msg += f"%0ATotal: R$ {total:.2f}"
    msg += f"%0ADesconto: R$ {desconto:.2f}"
    msg += f"%0AFrete: R$ {frete:.2f}"
    msg += f"%0ATotal final: R$ {total_final:.2f}"

    session["carrinho"] = []

    whatsapp = "5522981106356"
    return redirect(f"https://wa.me/{whatsapp}?text={msg}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
