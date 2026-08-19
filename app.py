from flask import Flask, request, session, redirect, url_for, render_template_string
import os

app = Flask(__name__)

# En producción es mejor guardar esta clave como variable de entorno.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "clave-secreta-demo")

ACCESS_KEY = os.environ.get("PANEL_ACCESS_KEY", "DEMO-2026-ACCESS")

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Access</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: #000;
            color: #00ff66;
            font-family: "Courier New", monospace;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .terminal {
            width: 90%;
            max-width: 520px;
            border: 1px solid #00ff66;
            padding: 40px;
            box-shadow: 0 0 25px rgba(0,255,102,.15);
        }

        .title {
            font-size: 25px;
            margin-bottom: 35px;
            text-align: center;
        }

        .prompt {
            margin-bottom: 12px;
            font-size: 15px;
        }

        input {
            width: 100%;
            background: #050505;
            color: #00ff66;
            border: 1px solid #00ff66;
            padding: 14px;
            outline: none;
            font-family: "Courier New", monospace;
            font-size: 16px;
        }

        input:focus {
            box-shadow: 0 0 10px rgba(0,255,102,.25);
        }

        button {
            width: 100%;
            margin-top: 20px;
            padding: 13px;
            background: #00ff66;
            color: #000;
            border: none;
            font-family: "Courier New", monospace;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            background: #7affad;
        }

        .error {
            color: #ff3333;
            margin-top: 20px;
            text-align: center;
        }

        .cursor {
            animation: blink 1s infinite;
        }

        @keyframes blink {
            50% {
                opacity: 0;
            }
        }
    </style>
</head>

<body>

<div class="terminal">

    <div class="title">
        SYSTEM ACCESS<span class="cursor">_</span>
    </div>

    <div class="prompt">
        &gt; ENTER THE KEY
    </div>

    <form method="POST">
        <input
            type="password"
            name="key"
            placeholder="Enter access key..."
            autocomplete="off"
            autofocus
            required
        >

        <button type="submit">
            ACCESS
        </button>
    </form>

    {% if error %}
        <div class="error">
            &gt; ACCESS DENIED
        </div>
    {% endif %}

</div>

</body>
</html>
"""


PANEL_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Device Demo Panel</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: #050505;
            color: #00ff66;
            font-family: "Courier New", monospace;
        }

        header {
            border-bottom: 1px solid #00ff66;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .container {
            max-width: 1100px;
            margin: 40px auto;
            padding: 20px;
        }

        .card {
            border: 1px solid #00ff66;
            padding: 25px;
            margin-bottom: 20px;
            background: #080808;
        }

        .card h2 {
            margin-top: 0;
        }

        .data {
            display: grid;
            grid-template-columns: 180px 1fr;
            gap: 12px;
        }

        .label {
            color: #888;
        }

        .logout {
            color: #000;
            background: #00ff66;
            padding: 10px 15px;
            text-decoration: none;
            font-weight: bold;
        }

        .status {
            color: #00ff66;
        }
    </style>
</head>

<body>

<header>
    <div>SYSTEM PANEL</div>
    <a class="logout" href="/logout">LOGOUT</a>
</header>

<div class="container">

    <div class="card">
        <h2>&gt; DEVICE DEMO</h2>

        <div class="data">
            <div class="label">STATUS</div>
            <div class="status">AUTHORIZED DEMO</div>

            <div class="label">DEVICE</div>
            <div>Demo Device</div>

            <div class="label">SYSTEM</div>
            <div>Demo Operating System</div>

            <div class="label">ID</div>
            <div>DEMO-DEVICE-001</div>
        </div>
    </div>

    <div class="card">
        <h2>&gt; INFORMATION</h2>
        <p>
            This panel is a demonstration interface.
        </p>
        <p>
            Only authorized and consented device information
            should be displayed here.
        </p>
    </div>

</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def login():

    if session.get("authenticated"):
        return redirect(url_for("panel"))

    error = False

    if request.method == "POST":

        entered_key = request.form.get("key", "")

        if entered_key == ACCESS_KEY:
            session["authenticated"] = True
            return redirect(url_for("panel"))

        error = True

    return render_template_string(LOGIN_PAGE, error=error)


@app.route("/panel")
def panel():

    if not session.get("authenticated"):
        return redirect(url_for("login"))

    return render_template_string(PANEL_PAGE)


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
