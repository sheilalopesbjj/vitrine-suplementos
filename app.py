from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

ARQ_PRODUTOS = "produtos.json"


def carregar_produtos():
    if not os.path.exists(ARQ_PRODUTOS):
        return []
    with open(ARQ_PRODUTOS, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_produtos(produtos):
    with open(ARQ_PRODUTOS, "w", encoding="utf-8") as f:
        json.dump(produtos, f, indent=4, ensure_ascii=False)


@app.route("/")
def index():
    produtos = carregar_produtos()
    return render_template("index.html", produtos=produtos)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    produtos = carregar_produtos()

    if request.method == "POST":
        novo = {
            "nome": request.form["nome"],
            "preco": request.form["preco"],
            "imagem": request.form["imagem"],
            "descricao": request.form["descricao"],
            "whatsapp": request.form["whatsapp"]
        }
        produtos.append(novo)
        salvar_produtos(produtos)
        return redirect(url_for("admin"))

    return render_template("admin.html", produtos=produtos)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
