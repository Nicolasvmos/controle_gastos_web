from flask import Flask, render_template, request, redirect, jsonify
import json
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
ARQUIVO = "gastos.json"

def carregar_dados():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if not conteudo:
                    return []
                return json.loads(conteudo)
        except json.JSONDecodeError:
            return []
    return []

def salvar_dados(gastos):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(gastos, f, indent=2, ensure_ascii=False)

def gerar_id(gastos):
    return max((g["id"] for g in gastos), default=0) + 1

@app.route("/")
def index():
    gastos = carregar_dados()
    total = sum(g["valor"] for g in gastos)
    return render_template("index.html", gastos=gastos, total=total)

@app.route("/adicionar", methods=["POST"])
def adicionar():
    gastos = carregar_dados()
    novo = {
        "id": gerar_id(gastos),
        "descricao": request.form["descricao"],
        "valor": float(request.form["valor"]),
        "categoria": request.form["categoria"],
        "data": request.form["data"] or datetime.today().strftime("%Y-%m-%d")
    }
    gastos.append(novo)
    salvar_dados(gastos)
    return redirect("/")

@app.route("/remover/<int:id>")
def remover(id):
    gastos = [g for g in carregar_dados() if g["id"] != id]
    salvar_dados(gastos)
    return redirect("/")

@app.route("/dados_grafico")
def dados_grafico():
    gastos = carregar_dados()
    meses = defaultdict(float)
    for g in gastos:
        try:
            data_obj = datetime.strptime(g["data"], "%Y-%m-%d")
            mes = data_obj.strftime("%m/%Y")
            meses[mes] += g["valor"]
        except:
            continue
    return jsonify(dict(meses))

if __name__ == "__main__":
    app.run(debug=True)
