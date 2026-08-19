from flask import Flask, request, session, redirect, url_for, render_template_string, jsonify
import os
from datetime import datetime

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "clave-secreta-demo"
)

ACCESS_KEY = os.environ.get(
    "PANEL_ACCESS_KEY",
    "DEMO-2026-ACCESS"
)


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


CONSENT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Diagnostic Authorization</title>

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

.item:last-child{border-bottom:0}

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

<h1>Diagnostic information access</h1>

<p>
This diagnostic session can display information provided by your browser.
Please review the information before continuing.
</p>

<div class="list">

<div class="item">• Browser language</div>
<div class="item">• Time zone and local time</div>
<div class="item">• Screen resolution</div>
<div class="item">• Browser and device information</div>
<div class="item">• Battery level, when supported by your browser</div>

</div>

<p>
No email address is collected automatically. You may close this page
at any time.
</p>

<form method="POST" action="/authorize">
<button type="submit">ALLOW DIAGNOSTIC INFORMATION</button>
</form>

<a class="cancel" href="/logout">CANCEL AND EXIT</a>

</div>

</body>
</html>
"""


PANEL_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">

<title>Device Diagnostics</title>

<style>
*{box-sizing:border-box}

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

.grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:16px;
}

.card{
    background:#0e1114;
    border:1px solid #242a2f;
    border-radius:7px;
    padding:22px;
}

.large{
    grid-column:span 2;
}

.full{
    grid-column:1/-1;
}

.title{
    color:#737c84;
    font-size:10px;
    letter-spacing:1.8px;
    margin-bottom:18px;
}

.device{
    font-size:22px;
    margin-bottom:8px;
}

.muted{
    color:#69727a;
    font-size:11px;
}

.row{
    display:flex;
    justify-content:space-between;
    padding:12px 0;
    border-bottom:1px solid #1d2226;
    font-size:12px;
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
    max-width:60%;
    word-break:break-word;
}

.good{
    color:#82c998;
}

.log{
    font-family:"Courier New",monospace;
    color:#707980;
    font-size:11px;
    line-height:2;
}

@media(max-width:800px){
    .grid{grid-template-columns:1fr}
    .large,.full{grid-column:span 1}
    header{padding:0 18px}
    .ready{display:none}
}
</style>
</head>

<body>

<header>

<div class="logo">DEVICE SERVICE</div>

<div class="right">
<div class="ready">● AUTHORIZED SESSION</div>
<a class="logout" href="/logout">LOG OUT</a>
</div>

</header>

<div class="container">

<h1>System Diagnostics</h1>

<div class="subtitle">
Authorized device diagnostic environment
</div>

<div class="grid">

<div class="card large">

<div class="title">DEVICE OVERVIEW</div>

<div class="device" id="deviceType">
Detecting device...
</div>

<div class="muted" id="platform">
Reading browser information...
</div>

</div>


<div class="card">

<div class="title">SESSION</div>

<div class="row">
<div class="label">STATUS</div>
<div class="value good">AUTHORIZED</div>
</div>

<div class="row">
<div class="label">ACCESS TIME</div>
<div class="value" id="accessTime">—</div>
</div>

</div>


<div class="card">

<div class="title">SYSTEM</div>

<div class="row">
<div class="label">LANGUAGE</div>
<div class="value" id="language">—</div>
</div>

<div class="row">
<div class="label">TIME ZONE</div>
<div class="value" id="timezone">—</div>
</div>

<div class="row">
<div class="label">SCREEN</div>
<div class="value" id="screen">—</div>
</div>

</div>


<div class="card">

<div class="title">BATTERY</div>

<div class="row">
<div class="label">STATUS</div>
<div class="value" id="batteryStatus">Checking...</div>
</div>

<div class="row">
<div class="label">LEVEL</div>
<div class="value" id="batteryLevel">—</div>
</div>

</div>


<div class="card large">

<div class="title">BROWSER ENVIRONMENT</div>

<div class="row">
<div class="label">BROWSER</div>
<div class="value" id="browser">—</div>
</div>

<div class="row">
<div class="label">PLATFORM</div>
<div class="value" id="platformFull">—</div>
</div>

<div class="row">
<div class="label">CORES</div>
<div class="value" id="cores">—</div>
</div>

</div>


<div class="card full">

<div class="title">SERVICE LOG</div>

<div class="log" id="log">

<div>OK — Authorization confirmed</div>
<div>OK — Diagnostic session initialized</div>
<div>OK — Browser information received</div>
<div>OK — System status ready</div>

</div>

</div>

</div>

</div>


<script>

function detectDevice(){

    const ua = navigator.userAgent.toLowerCase();

    let type = "Desktop / Unknown";

    if (/android/.test(ua)){
        type = "Android Device";
    }
    else if (/iphone|ipad|ipod/.test(ua)){
        type = "Apple Mobile Device";
    }
    else if (/windows/.test(ua)){
        type = "Windows Computer";
    }
    else if (/macintosh|mac os/.test(ua)){
        type = "Mac Computer";
    }
    else if (/linux/.test(ua)){
        type = "Linux Computer";
    }

    document.getElementById("deviceType").textContent = type;

    document.getElementById("platform").textContent =
        navigator.platform || "Not available";

    document.getElementById("platformFull").textContent =
        navigator.platform || "Not available";

    document.getElementById("browser").textContent =
        navigator.userAgent;

    document.getElementById("cores").textContent =
        navigator.hardwareConcurrency
        ? navigator.hardwareConcurrency
        : "Not available";
}


function systemInfo(){

    document.getElementById("language").textContent =
        navigator.language || "Not available";

    document.getElementById("timezone").textContent =
        Intl.DateTimeFormat().resolvedOptions().timeZone
        || "Not available";

    document.getElementById("screen").textContent =
        window.screen.width + " × " + window.screen.height;

    document.getElementById("accessTime").textContent =
        new Date().toLocaleString();

}


async function batteryInfo(){

    const status =
        document.getElementById("batteryStatus");

    const level =
        document.getElementById("batteryLevel");

    if (!navigator.getBattery){

        status.textContent =
            "Not supported";

        level.textContent =
            "Not available";

        return;
    }

    try{

        const battery =
            await navigator.getBattery();

        status.textContent =
            battery.charging
            ? "Charging"
            : "Not charging";

        level.textContent =
            Math.round(battery.level * 100) + "%";

    }catch(error){

        status.textContent =
            "Unavailable";

        level.textContent =
            "Not available";
    }
}


detectDevice();
systemInfo();
batteryInfo();

</script>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def login():

    if session.get("authenticated"):
        if session.get("authorized"):
            return redirect(url_for("panel"))

        return redirect(url_for("authorize"))

    error = False

    if request.method == "POST":

        entered_key = request.form.get("key", "")

        if entered_key == ACCESS_KEY:

            session["authenticated"] = True
            session["authorized"] = False

            return redirect(url_for("authorize"))

        error = True

    return render_template_string(
        LOGIN_PAGE,
        error=error
    )


@app.route("/authorize", methods=["GET", "POST"])
def authorize():

    if not session.get("authenticated"):
        return redirect(url_for("login"))

    if request.method == "POST":

        session["authorized"] = True

        return redirect(url_for("panel"))

    return render_template_string(CONSENT_PAGE)


@app.route("/panel")
def panel():

    if not session.get("authenticated"):
        return redirect(url_for("login"))

    if not session.get("authorized"):
        return redirect(url_for("authorize"))

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
