from flask import Flask, render_template, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "chave-secreta-carrinho"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQ_PRODUTOS = os.path.join(BASE_DIR, "produtos.json")


def carregar_produtos():
    try:
        if not os.path.exists(ARQ_PRODUTOS):
            return []
        with open(ARQ_PRODUTOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("ERRO AO CARREGAR PRODUTOS:", e)
        return []


@app.route("/")
def index():
    try:
        produtos = carregar_produtos()
        carrinho = session.get("carrinho", [])
        total = sum(float(p.get("preco", 0)) for p in carrinho)
        return render_template(
            "index.html",
            produtos=produtos,
            carrinho=carrinho,
            total=total
        )
    except Exception as e:
        return f"<h1>Erro interno</h1><pre>{e}</pre>"


@app.route("/add/<int:id_produto>")
def add(id_produto):
    produtos = carregar_produtos()

    if id_produto < 0 or id_produto >= len(produtos):
        return redirect(url_for("index"))

    carrinho = session.get("carrinho", [])
    carrinho.append(produtos[id_produto])
    session["carrinho"] = carrinho

    return redirect(url_for("index"))


@app.route("/limpar")
def limpar():
    session["carrinho"] = []
    return redirect(url_for("index"))


@app.route("/finalizar")
def finalizar():
    carrinho = session.get("carrinho", [])

    if not carrinho:
        return redirect(url_for("index"))

    total = sum(float(p.get("preco", 0)) for p in carrinho)
    desconto = 10.0
    frete = 15.0
    total_final = total - desconto + frete

    mensagem = "🛒 Pedido - Loja de Suplementos%0A%0A"

    for p in carrinho:
        mensagem += f"- {p.get('nome')} (R$ {float(p.get('preco',0)):.2f})%0A"

    mensagem += (
        f"%0A💰 Total: R$ {total:.2f}"
        f"%0A🎯 Desconto: R$ {desconto:.2f}"
        f"%0A🚚 Frete: R$ {frete:.2f}"
        f"%0A✅ Total final: R$ {total_final:.2f}"
    )

    session["carrinho"] = []

    whatsapp = "5522981106356"
    return redirect(f"https://wa.me/{whatsapp}?text={mensagem}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
