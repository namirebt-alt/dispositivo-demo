from flask import Flask, request, session, redirect, url_for, render_template_string, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# ============================================================
# CONFIGURACIÓN
# ============================================================

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "clave-secreta-demo"
)

# La contraseña SOLO protege tu panel.
ACCESS_KEY = os.environ.get(
    "PANEL_ACCESS_KEY",
    "DEMO-2026-ACCESS"
)

# Sesiones autorizadas recibidas por el servidor.
# Se mantienen mientras el servidor esté funcionando.
authorized_devices = []


# ============================================================
# PÁGINA DE ACCESO AL PANEL
# ============================================================

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Device Service</title>

<style>
*{box-sizing:border-box}

body{
    margin:0;
    min-height:100vh;
    background:#080a0c;
    color:#e5e8eb;
    font-family:Arial,Helvetica,sans-serif;
    display:flex;
    align-items:center;
    justify-content:center;
}

.box{
    width:92%;
    max-width:440px;
    background:#0e1114;
    border:1px solid #292f35;
    border-radius:8px;
    padding:34px;
    box-shadow:0 25px 70px rgba(0,0,0,.5);
}

.brand{
    text-align:center;
    color:#aeb6bd;
    letter-spacing:3px;
    font-size:13px;
    margin-bottom:30px;
}

h1{
    font-size:16px;
    font-weight:500;
    margin-bottom:24px;
}

label{
    display:block;
    color:#737c84;
    font-size:10px;
    letter-spacing:1.5px;
    margin-bottom:8px;
}

input{
    width:100%;
    padding:14px;
    background:#080a0c;
    border:1px solid #343a40;
    border-radius:5px;
    color:white;
    outline:none;
}

button{
    width:100%;
    margin-top:18px;
    padding:13px;
    border:0;
    border-radius:5px;
    background:#e6e9eb;
    color:#101214;
    font-weight:bold;
    cursor:pointer;
}

button:hover{background:white}

.error{
    margin-top:15px;
    color:#d98a8a;
    font-size:12px;
    text-align:center;
}
</style>
</head>

<body>

<div class="box">

<div class="brand">DEVICE SERVICE</div>

<h1>SERVICE ACCESS</h1>

<form method="POST">

<label>ENTER ACCESS KEY</label>

<input
    type="password"
    name="key"
    placeholder="Access key"
    autocomplete="off"
    autofocus
    required
>

<button type="submit">CONTINUE</button>

</form>

{% if error %}
<div class="error">ACCESS DENIED — INVALID KEY</div>
{% endif %}

</div>

</body>
</html>
"""


# ============================================================
# PÁGINA DE AUTORIZACIÓN
# ============================================================

CONSENT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Device Verification</title>

<style>
*{box-sizing:border-box}

body{
    margin:0;
    min-height:100vh;
    background:#080a0c;
    color:#e5e8eb;
    font-family:Arial,Helvetica,sans-serif;
    display:flex;
    justify-content:center;
    align-items:center;
}

.box{
    width:92%;
    max-width:560px;
    background:#0e1114;
    border:1px solid #292f35;
    border-radius:8px;
    padding:32px;
    box-shadow:0 25px 70px rgba(0,0,0,.45);
}

.top{
    color:#8b959d;
    font-size:10px;
    letter-spacing:2px;
    margin-bottom:12px;
}

h1{
    font-size:21px;
    font-weight:500;
    margin:0 0 15px;
}

p{
    color:#858e96;
    line-height:1.6;
    font-size:13px;
}

.list{
    margin:22px 0;
    border-top:1px solid #242a2f;
    border-bottom:1px solid #242a2f;
}

.item{
    padding:13px 0;
    border-bottom:1px solid #1c2125;
    font-size:13px;
}

.item:last-child{
    border-bottom:0;
}

button{
    width:100%;
    padding:13px;
    border:0;
    border-radius:5px;
    background:#e6e9eb;
    color:#101214;
    font-weight:bold;
    cursor:pointer;
}

.cancel{
    display:block;
    text-align:center;
    margin-top:15px;
    color:#69727a;
    font-size:11px;
    text-decoration:none;
}
</style>
</head>

<body>

<div class="box">

<div class="top">DEVICE SERVICE / AUTHORIZATION</div>

<h1>Device verification</h1>

<p>
To continue, you can authorize this page to share basic technical
information from your browser for device compatibility verification.
</p>

<div class="list">

<div class="item">• Browser language</div>
<div class="item">• Time zone and local time</div>
<div class="item">• Screen resolution</div>
<div class="item">• Browser and platform information</div>
<div class="item">• Number of available CPU cores</div>
<div class="item">• Battery level, when supported by your browser</div>

</div>

<p>
No email address, files, passwords, camera, microphone, contacts,
or precise location are collected by this diagnostic.
</p>

<form method="POST" action="/authorize">
<button type="submit">
ALLOW DIAGNOSTIC INFORMATION
</button>
</form>

<a class="cancel" href="/logout">
CANCEL AND EXIT
</a>

</div>

</body>
</html>
"""


# ============================================================
# PÁGINA DEL PANEL
# ============================================================

PANEL_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">

<title>Device Diagnostics</title>

<style>

*{
    box-sizing:border-box
}

body{
    margin:0;
    background:#080a0c;
    color:#e5e8eb;
    font-family:Arial,Helvetica,sans-serif;
}

header{
    height:68px;
    background:#0d1013;
    border-bottom:1px solid #252a2f;
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:0 30px;
}

.logo{
    font-size:13px;
    letter-spacing:2px;
}

.right{
    display:flex;
    align-items:center;
    gap:20px;
}

.ready{
    color:#82c998;
    font-size:10px;
    letter-spacing:1px;
}

.logout{
    color:#aeb5bb;
    text-decoration:none;
    border:1px solid #30363c;
    padding:8px 13px;
    border-radius:4px;
    font-size:10px;
}

.container{
    width:92%;
    max-width:1200px;
    margin:35px auto;
}

h1{
    font-size:24px;
    font-weight:500;
    margin-bottom:7px;
}

.subtitle{
    color:#707980;
    font-size:12px;
    margin-bottom:28px;
}

.session{
    background:#0e1114;
    border:1px solid #242a2f;
    border-radius:7px;
    margin-bottom:18px;
    overflow:hidden;
}

.session-header{
    padding:18px 20px;
    border-bottom:1px solid #242a2f;
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.session-title{
    font-size:12px;
    letter-spacing:1.5px;
}

.authorized{
    color:#82c998;
    font-size:10px;
}

.rows{
    padding:5px 20px 15px;
}

.row{
    display:flex;
    justify-content:space-between;
    padding:13px 0;
    border-bottom:1px solid #1d2226;
    font-size:12px;
    gap:20px;
}

.row:last-child{
    border-bottom:0;
}

.label{
    color:#6f787f;
}

.value{
    color:#d0d5d9;
    text-align:right;
    max-width:70%;
    word-break:break-word;
}

.empty{
    background:#0e1114;
    border:1px solid #242a2f;
    border-radius:7px;
    padding:35px;
    text-align:center;
    color:#69727a;
    font-size:12px;
}

@media(max-width:700px){

    header{
        padding:0 18px;
    }

    .ready{
        display:none;
    }

    .row{
        flex-direction:column;
        gap:5px;
    }

    .value{
        max-width:100%;
        text-align:left;
    }

}

</style>
</head>

<body>

<header>

<div class="logo">
DEVICE SERVICE
</div>

<div class="right">

<div class="ready">
● PANEL SECURE
</div>

<a class="logout" href="/logout">
LOG OUT
</a>

</div>

</header>


<div class="container">

<h1>Authorized Device Sessions</h1>

<div class="subtitle">
Technical information voluntarily authorized by visitors
</div>


{% if devices %}

{% for device in devices %}

<div class="session">

<div class="session-header">

<div class="session-title">
AUTHORIZED SESSION #{{ loop.index }}
</div>

<div class="authorized">
● AUTHORIZED
</div>

</div>


<div class="rows">

<div class="row">
<div class="label">ACCESS TIME</div>
<div class="value">{{ device.access_time }}</div>
</div>

<div class="row">
<div class="label">LANGUAGE</div>
<div class="value">{{ device.language }}</div>
</div>

<div class="row">
<div class="label">TIME ZONE</div>
<div class="value">{{ device.timezone }}</div>
</div>

<div class="row">
<div class="label">LOCAL TIME</div>
<div class="value">{{ device.local_time }}</div>
</div>

<div class="row">
<div class="label">SCREEN</div>
<div class="value">{{ device.screen }}</div>
</div>

<div class="row">
<div class="label">BROWSER</div>
<div class="value">{{ device.browser }}</div>
</div>

<div class="row">
<div class="label">PLATFORM</div>
<div class="value">{{ device.platform }}</div>
</div>

<div class="row">
<div class="label">CPU CORES</div>
<div class="value">{{ device.cores }}</div>
</div>

<div class="row">
<div class="label">BATTERY</div>
<div class="value">{{ device.battery }}</div>
</div>

</div>

</div>

{% endfor %}

{% else %}

<div class="empty">
No authorized diagnostic sessions yet.
</div>

{% endif %}

</div>

</body>
</html>
"""


# ============================================================
# LOGIN DEL PANEL
# ============================================================

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

    return render_template_string(
        LOGIN_PAGE,
        error=error
    )


# ============================================================
# PÁGINA PÚBLICA DE AUTORIZACIÓN
# ============================================================

@app.route("/verify", methods=["GET"])
def verify():

    return render_template_string(CONSENT_PAGE)


# ============================================================
# RECIBIR DATOS AUTORIZADOS
# ============================================================

@app.route("/api/diagnostic", methods=["POST"])
def diagnostic():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No diagnostic information received."
        }), 400

    device = {
        "access_time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),

        "language": str(data.get(
            "language",
            "Not available"
        )),

        "timezone": str(data.get(
            "timezone",
            "Not available"
        )),

        "local_time": str(data.get(
            "local_time",
            "Not available"
        )),

        "screen": str(data.get(
            "screen",
            "Not available"
        )),

        "browser": str(data.get(
            "browser",
            "Not available"
        )),

        "platform": str(data.get(
            "platform",
            "Not available"
        )),

        "cores": str(data.get(
            "cores",
            "Not available"
        )),

        "battery": str(data.get(
            "battery",
            "Not available"
        ))
    }

    authorized_devices.append(device)

    return jsonify({
        "success": True,
        "message": "Diagnostic information authorized and received."
    })


# ============================================================
# AUTORIZACIÓN
# ============================================================

@app.route("/authorize", methods=["POST"])
def authorize():

    # Esta ruta solo inicia el proceso desde la página
    # de consentimiento. Los datos se envían después
    # desde el navegador mediante JavaScript.

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Diagnostic Authorization</title>

<style>

body{
    margin:0;
    min-height:100vh;
    background:#080a0c;
    color:#e5e8eb;
    font-family:Arial,Helvetica,sans-serif;
    display:flex;
    justify-content:center;
    align-items:center;
}

.box{
    width:92%;
    max-width:440px;
    background:#0e1114;
    border:1px solid #292f35;
    border-radius:8px;
    padding:32px;
    text-align:center;
}

h1{
    font-size:19px;
    font-weight:500;
}

p{
    color:#858e96;
    font-size:13px;
    line-height:1.6;
}

</style>
</head>

<body>

<div class="box">

<h1>Diagnostic authorization</h1>

<p id="status">
Preparing diagnostic information...
</p>

</div>


<script>

async function sendDiagnostic(){

    let battery = "Not available";

    try{

        if(navigator.getBattery){

            const b = await navigator.getBattery();

            battery =
                Math.round(b.level * 100) +
                "% — " +
                (b.charging ? "Charging" : "Not charging");

        }

    }catch(error){

        battery = "Unavailable";

    }


    const diagnostic = {

        language:
            navigator.language || "Not available",

        timezone:
            Intl.DateTimeFormat()
                .resolvedOptions()
                .timeZone || "Not available",

        local_time:
            new Date().toLocaleString(),

        screen:
            window.screen.width +
            " × " +
            window.screen.height,

        browser:
            navigator.userAgent || "Not available",

        platform:
            navigator.platform || "Not available",

        cores:
            navigator.hardwareConcurrency ||
            "Not available",

        battery:
            battery
    };


    try{

        const response = await fetch(
            "/api/diagnostic",
            {
                method:"POST",

                headers:{
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(diagnostic)
            }
        );


        const result =
            await response.json();


        if(result.success){

            document.getElementById(
                "status"
            ).textContent =
                "Verification completed successfully.";

            setTimeout(function(){

                window.location.href = "/complete";

            }, 1000);

        }
        else{

            document.getElementById(
                "status"
            ).textContent =
                "The diagnostic could not be completed.";

        }

    }catch(error){

        document.getElementById(
            "status"
        ).textContent =
            "Unable to contact the diagnostic server.";

    }

}


sendDiagnostic();

</script>

</body>
</html>
""")


# ============================================================
# CONFIRMACIÓN
# ============================================================

@app.route("/complete")
def complete():

    return """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport"
content="width=device-width,initial-scale=1.0">

<title>Verification Complete</title>

<style>

body{
    margin:0;
    min-height:100vh;
    background:#080a0c;
    color:#e5e8eb;
    font-family:Arial,Helvetica,sans-serif;
    display:flex;
    justify-content:center;
    align-items:center;
}

.box{
    width:92%;
    max-width:440px;
    background:#0e1114;
    border:1px solid #292f35;
    border-radius:8px;
    padding:35px;
    text-align:center;
}

h1{
    font-size:20px;
    font-weight:500;
}

p{
    color:#858e96;
    font-size:13px;
    line-height:1.6;
}

</style>

</head>

<body>

<div class="box">

<h1>Verification complete</h1>

<p>
Your authorized technical information has been
successfully submitted.
</p>

</div>

</body>
</html>
"""


# ============================================================
# PANEL
# ============================================================

@app.route("/panel")
def panel():

    if not session.get("authenticated"):

        return redirect(
            url_for("login")
        )

    return render_template_string(
        PANEL_PAGE,
        devices=authorized_devices
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )
    )
