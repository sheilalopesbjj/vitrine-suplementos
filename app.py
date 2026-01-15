from flask import Flask, render_template, session, redirect, url_for, request
import json
import urllib.parse
import os

app = Flask(__name__)
app.secret_key = "chave_super_secreta_123"

ARQ_PRODUTOS = "produtos.json"

CUPONS = {
    "PRIMEIRA10": 10
}

FRETES = {
    "Retirada no local": 0,
    "Centro": 5.0,
    "Bairro A": 7.0,
    "Bairro B": 10.0
}

# -----------------------------
# UTILIDADES
# -----------------------------
def criar_arquivo_se_nao_existir():
    if not os.path.exists(ARQ_PRODUTOS):
        produtos_iniciais = [
            {"id": 1, "nome": "Creatina Monohidratada 300g", "preco": 99.9},
            {"id": 2, "nome": "Whey Protein Concentrado 900g", "preco": 129.9},
            {"id": 3, "nome": "Termogênico Natural", "preco": 79.9}
        ]
        with open(ARQ_PRODUTOS, "w", encoding="utf-8") as f:
            json.dump(produtos_iniciais, f, ensure_ascii=False, indent=2)

def carregar_produtos():
    criar_arquivo_se_nao_existir()
    with open(ARQ_PRODUTOS, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_produtos(produtos):
    with open(ARQ_PRODUTOS, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

# -----------------------------
# ROTAS
# -----------------------------
@app.route("/")
def index():
    produtos = carregar_produtos()
    return render_template("index.html", produtos=produtos)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    produtos = carregar_produtos()

    if request.method == "POST":
        nome = request.form["nome"]
        preco = float(request.form["preco"])

        novo_id = max(p["id"] for p in produtos) + 1 if produtos else 1

        produtos.append({
            "id": novo_id,
            "nome": nome,
            "preco": preco
        })

        salvar_produtos(produtos)
        return redirect(url_for("admin"))

    return render_template("admin.html", produtos=produtos)

@app.route("/admin/remover/<int:id>")
def remover_produto(id):
    produtos = carregar_produtos()
    produtos = [p for p in produtos if p["id"] != id]
    salvar_produtos(produtos)
    return redirect(url_for("admin"))

@app.route("/add/<int:id>")
def add(id):
    produtos = carregar_produtos()
    carrinho = session.get("carrinho", {})

    for p in produtos:
        if p["id"] == id:
            if str(id) in carrinho:
                carrinho[str(id)]["qtd"] += 1
            else:
                carrinho[str(id)] = {
                    "nome": p["nome"],
                    "preco": p["preco"],
                    "qtd": 1
                }

    session["carrinho"] = carrinho
    return redirect(url_for("index"))

@app.route("/carrinho", methods=["GET", "POST"])
def carrinho():
    carrinho = session.get("carrinho", {})
    cupom = session.get("cupom")
    bairro = session.get("bairro")

    desconto_percentual = CUPONS.get(cupom, 0)
    frete_valor = FRETES.get(bairro, 0)

    if request.method == "POST":
        codigo = request.form.get("cupom", "").upper()
        if codigo in CUPONS:
            session["cupom"] = codigo
            desconto_percentual = CUPONS[codigo]

        bairro_escolhido = request.form.get("bairro")
        if bairro_escolhido in FRETES:
            session["bairro"] = bairro_escolhido
            frete_valor = FRETES[bairro_escolhido]

    subtotal = sum(item["preco"] * item["qtd"] for item in carrinho.values())
    desconto = subtotal * (desconto_percentual / 100)
    total = subtotal - desconto + frete_valor

    return render_template(
        "carrinho.html",
        carrinho=carrinho,
        subtotal=subtotal,
        desconto=desconto,
        frete=frete_valor,
        total=total,
        cupom=cupom,
        bairro=bairro,
        fretes=FRETES
    )

@app.route("/finalizar")
def finalizar():
    carrinho = session.get("carrinho", {})
    cupom = session.get("cupom")
    bairro = session.get("bairro")

    desconto_percentual = CUPONS.get(cupom, 0)
    frete_valor = FRETES.get(bairro, 0)

    mensagem = "🛒 *Pedido - Loja de Suplementos*\n\n"
    subtotal = 0

    for item in carrinho.values():
        valor = item["preco"] * item["qtd"]
        mensagem += f"- {item['nome']} x{item['qtd']} — R$ {valor:.2f}\n"
        subtotal += valor

    desconto = subtotal * (desconto_percentual / 100)
    total = subtotal - desconto + frete_valor

    mensagem += f"\nSubtotal: R$ {subtotal:.2f}"
    if cupom:
        mensagem += f"\nCupom {cupom}: -R$ {desconto:.2f}"
    mensagem += f"\nFrete ({bairro}): R$ {frete_valor:.2f}"
    mensagem += f"\n💰 *Total:* R$ {total:.2f}"

    texto = urllib.parse.quote(mensagem)
    whatsapp = f"https://wa.me/5522981106356?text={texto}"

    session.clear()
    return redirect(whatsapp)

if __name__ == "__main__":
    app.run()
