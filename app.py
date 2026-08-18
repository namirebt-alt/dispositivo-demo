from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

sesiones = []


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/guardar", methods=["POST"])
def guardar():
    datos = request.get_json()

    sesion = {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "sistema": datos.get("sistema", "Desconocido"),
        "navegador": datos.get("navegador", "Desconocido"),
        "pantalla": datos.get("pantalla", "Desconocida"),
        "idioma": datos.get("idioma", "Desconocido"),
        "zona_horaria": datos.get("zona_horaria", "Desconocida")
    }

    sesiones.append(sesion)

    return jsonify({"ok": True})


@app.route("/panel")
def panel():
    return render_template("panel.html", sesiones=sesiones)


if __name__ == "__main__":
    print("===================================")
    print("       LUCKYPLAY - DEMO")
    print("===================================")
    print("Web:   http://127.0.0.1:5000")
    print("Panel: http://127.0.0.1:5000/panel")

    app.run(debug=True)