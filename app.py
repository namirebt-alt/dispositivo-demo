from flask import Flask, request, session, redirect, url_for, render_template_string
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
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Device Service</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    background:
        radial-gradient(circle at 50% 35%, #15191d 0%, #090b0d 45%, #050607 100%);
    color: #e7eaed;
    font-family: Arial, Helvetica, sans-serif;

    display: flex;
    align-items: center;
    justify-content: center;
}

.login-wrapper {
    width: 92%;
    max-width: 430px;
}

.brand {
    text-align: center;
    margin-bottom: 28px;
}

.brand-title {
    font-size: 13px;
    letter-spacing: 4px;
    color: #9da5ad;
    margin-bottom: 10px;
}

.brand-subtitle {
    font-size: 11px;
    letter-spacing: 2px;
    color: #596169;
}

.login-card {
    background: rgba(15, 18, 21, 0.96);
    border: 1px solid #2a3036;
    border-radius: 8px;
    padding: 34px;
    box-shadow:
        0 25px 70px rgba(0,0,0,.55),
        inset 0 1px rgba(255,255,255,.025);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 28px;
}

.status-light {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #7fd49a;
    box-shadow: 0 0 10px rgba(127,212,154,.35);
}

.card-title {
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 1px;
}

label {
    display: block;
    color: #858d95;
    font-size: 11px;
    letter-spacing: 1.5px;
    margin-bottom: 9px;
}

input {
    width: 100%;
    background: #090b0d;
    border: 1px solid #30363c;
    border-radius: 5px;
    padding: 14px;
    color: #e8ebee;
    outline: none;
    font-size: 14px;
    transition: .2s;
}

input:focus {
    border-color: #707981;
    box-shadow: 0 0 0 3px rgba(255,255,255,.025);
}

button {
    width: 100%;
    margin-top: 18px;
    padding: 13px;
    border: 1px solid #4a5259;
    border-radius: 5px;
    background: #e8ebee;
    color: #101214;
    font-weight: 600;
    letter-spacing: 1px;
    cursor: pointer;
    transition: .2s;
}

button:hover {
    background: #ffffff;
}

.error {
    margin-top: 16px;
    padding: 10px;
    border: 1px solid #573333;
    background: #1b1010;
    color: #d98a8a;
    border-radius: 4px;
    font-size: 12px;
    text-align: center;
}

.footer {
    text-align: center;
    margin-top: 22px;
    color: #4f565d;
    font-size: 10px;
    letter-spacing: 1px;
}

</style>
</head>

<body>

<div class="login-wrapper">

    <div class="brand">
        <div class="brand-title">
            DEVICE SERVICE
        </div>

        <div class="brand-subtitle">
            SYSTEM DIAGNOSTICS PLATFORM
        </div>
    </div>

    <div class="login-card">

        <div class="card-header">
            <div class="status-light"></div>

            <div class="card-title">
                SERVICE ACCESS
            </div>
        </div>

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

            <button type="submit">
                CONTINUE
            </button>

        </form>

        {% if error %}
        <div class="error">
            ACCESS DENIED — INVALID KEY
        </div>
        {% endif %}

    </div>

    <div class="footer">
        AUTHORIZED SERVICE ENVIRONMENT
    </div>

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

<title>Device Service Panel</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #080a0c;
    color: #e5e8eb;
    font-family: Arial, Helvetica, sans-serif;
}

/* HEADER */

header {
    height: 68px;
    background: #0d1013;
    border-bottom: 1px solid #252a2f;

    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 0 32px;
}

.logo-area {
    display: flex;
    align-items: center;
    gap: 14px;
}

.logo-box {
    width: 30px;
    height: 30px;

    border: 1px solid #555d64;
    border-radius: 5px;

    display: flex;
    align-items: center;
    justify-content: center;

    color: #cbd0d4;
    font-size: 13px;
}

.logo-text {
    font-size: 13px;
    letter-spacing: 2px;
    font-weight: 600;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 20px;
}

.connection {
    color: #89929a;
    font-size: 11px;
    letter-spacing: 1px;
}

.connection span {
    color: #82c998;
}

.logout {
    text-decoration: none;
    color: #aeb5bb;
    border: 1px solid #30363c;
    border-radius: 4px;
    padding: 8px 13px;
    font-size: 10px;
    letter-spacing: 1px;
}

.logout:hover {
    background: #171b1f;
}

/* MAIN */

.container {
    width: 92%;
    max-width: 1200px;
    margin: 38px auto;
}

/* PAGE TITLE */

.page-title {
    margin-bottom: 28px;
}

.page-title h1 {
    margin: 0 0 8px;
    font-size: 24px;
    font-weight: 500;
}

.page-title p {
    margin: 0;
    color: #707980;
    font-size: 12px;
}

/* GRID */

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}

.card {
    background: #0e1114;
    border: 1px solid #242a2f;
    border-radius: 7px;
    padding: 22px;
}

.card-title {
    color: #737c84;
    font-size: 10px;
    letter-spacing: 1.8px;
    margin-bottom: 18px;
}

/* DEVICE CARD */

.device-card {
    grid-column: span 2;
}

.device-name {
    font-size: 22px;
    font-weight: 500;
    margin-bottom: 8px;
}

.device-id {
    color: #606970;
    font-size: 11px;
    letter-spacing: 1px;
}

/* STATUS */

.status-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.status {
    display: flex;
    align-items: center;
    gap: 10px;
}

.status-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #82c998;
    box-shadow: 0 0 12px rgba(130,201,152,.25);
}

.status-text {
    color: #9bc7a8;
    font-size: 13px;
}

/* INFORMATION */

.info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}

.info-item label {
    display: block;
    color: #626a72;
    font-size: 9px;
    letter-spacing: 1.5px;
    margin-bottom: 7px;
}

.info-item div {
    color: #d0d5d9;
    font-size: 13px;
}

/* DIAGNOSTICS */

.diagnostic-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.diagnostic {
    display: flex;
    justify-content: space-between;
    align-items: center;

    padding-bottom: 12px;
    border-bottom: 1px solid #1c2125;
}

.diagnostic:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.diagnostic-name {
    color: #9ca4ab;
    font-size: 12px;
}

.diagnostic-result {
    color: #82c998;
    font-size: 10px;
    letter-spacing: 1px;
}

/* PROGRESS */

.progress {
    height: 5px;
    background: #1d2226;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 18px;
}

.progress-bar {
    height: 100%;
    width: 100%;
    background: #7e898f;
}

/* LOG */

.log {
    font-family: "Courier New", monospace;
    font-size: 11px;
    line-height: 2;
    color: #6f787f;
}

.log .ok {
    color: #87a992;
}

/* FULL WIDTH */

.full {
    grid-column: 1 / -1;
}

/* RESPONSIVE */

@media (max-width: 800px) {

    header {
        padding: 0 18px;
    }

    .connection {
        display: none;
    }

    .container {
        width: 94%;
        margin: 25px auto;
    }

    .grid {
        grid-template-columns: 1fr;
    }

    .device-card,
    .full {
        grid-column: span 1;
    }

    .info-grid {
        grid-template-columns: 1fr;
    }

}

</style>

</head>

<body>

<header>

    <div class="logo-area">

        <div class="logo-box">
            DS
        </div>

        <div class="logo-text">
            DEVICE SERVICE
        </div>

    </div>

    <div class="header-right">

        <div class="connection">
            SYSTEM STATUS:
            <span>READY</span>
        </div>

        <a class="logout" href="/logout">
            LOG OUT
        </a>

    </div>

</header>


<div class="container">

    <div class="page-title">

        <h1>System Diagnostics</h1>

        <p>
            Authorized device service and diagnostic environment
        </p>

    </div>


    <div class="grid">


        <!-- DEVICE -->

        <div class="card device-card">

            <div class="card-title">
                DEVICE
            </div>

            <div class="device-name">
                Demo Device
            </div>

            <div class="device-id">
                DEVICE ID / DEMO-DEVICE-001
            </div>

        </div>


        <!-- STATUS -->

        <div class="card status-card">

            <div class="card-title">
                SERVICE STATUS
            </div>

            <div class="status">

                <div class="status-dot"></div>

                <div class="status-text">
                    Device ready
                </div>

            </div>

        </div>


        <!-- SYSTEM INFORMATION -->

        <div class="card device-card">

            <div class="card-title">
                SYSTEM INFORMATION
            </div>

            <div class="info-grid">

                <div class="info-item">
                    <label>OPERATING SYSTEM</label>
                    <div>Demo Operating System</div>
                </div>

                <div class="info-item">
                    <label>DEVICE TYPE</label>
                    <div>Diagnostic Demo Unit</div>
                </div>

                <div class="info-item">
                    <label>SERVICE MODE</label>
                    <div>Authorized</div>
                </div>

                <div class="info-item">
                    <label>SESSION</label>
                    <div>Active</div>
                </div>

            </div>

        </div>


        <!-- DIAGNOSTICS -->

        <div class="card">

            <div class="card-title">
                DIAGNOSTIC CHECK
            </div>

            <div class="diagnostic-list">

                <div class="diagnostic">
                    <div class="diagnostic-name">
                        System integrity
                    </div>

                    <div class="diagnostic-result">
                        PASSED
                    </div>
                </div>

                <div class="diagnostic">
                    <div class="diagnostic-name">
                        Storage check
                    </div>

                    <div class="diagnostic-result">
                        PASSED
                    </div>
                </div>

                <div class="diagnostic">
                    <div class="diagnostic-name">
                        Service environment
                    </div>

                    <div class="diagnostic-result">
                        READY
                    </div>
                </div>

            </div>

        </div>


        <!-- SERVICE PROGRESS -->

        <div class="card">

            <div class="card-title">
                SERVICE READINESS
            </div>

            <div style="font-size:24px;">
                100%
            </div>

            <div class="progress">
                <div class="progress-bar"></div>
            </div>

        </div>


        <!-- LOG -->

        <div class="card full">

            <div class="card-title">
                SERVICE LOG
            </div>

            <div class="log">

                <div>
                    <span class="ok">OK</span>
                    — Diagnostic environment initialized
                </div>

                <div>
                    <span class="ok">OK</span>
                    — Authorization verified
                </div>

                <div>
                    <span class="ok">OK</span>
                    — Demo device recognized
                </div>

                <div>
                    <span class="ok">OK</span>
                    — System ready for authorized service
                </div>

            </div>

        </div>

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

    return render_template_string(
        LOGIN_PAGE,
        error=error
    )


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
