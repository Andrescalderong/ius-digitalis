#!/usr/bin/env python3
"""Actualiza dashboard con datos reales del blockchain"""
import json
from pathlib import Path

# Leer datos reales
blockchain_data = json.loads(Path("blockchain_registry/outputs/anchors.json").read_text())

# Template HTML
html_template = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IUS-DIGITALIS Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #00ff41;
            padding: 40px 20px;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            text-align: center;
            border: 3px solid #00ff41;
            padding: 30px;
            margin-bottom: 40px;
            background: rgba(26, 31, 58, 0.8);
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.3);
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { box-shadow: 0 0 20px rgba(0, 255, 65, 0.3); }
            to { box-shadow: 0 0 40px rgba(0, 255, 65, 0.6); }
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        }
        .subtitle { font-size: 1.2em; color: #4ecdc4; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: #1a1f3a;
            border: 2px solid #00ff41;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0, 255, 65, 0.3);
        }
        .stat-number {
            font-size: 3em;
            font-weight: bold;
            color: #ff6b35;
            margin: 10px 0;
        }
        .stat-label { font-size: 1.1em; color: #4ecdc4; }
        .section-title {
            font-size: 1.8em;
            margin: 30px 0 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #00ff41;
            color: #00ff41;
        }
        .transaction {
            background: #0f1729;
            border-left: 5px solid #00ff41;
            padding: 25px;
            margin: 20px 0;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .transaction:hover {
            background: #1a1f3a;
            transform: translateX(10px);
        }
        .transaction h3 {
            color: #4ecdc4;
            margin-bottom: 15px;
            font-size: 1.4em;
        }
        .tx-row { margin: 8px 0; padding: 5px 0; }
        .tx-label {
            color: #00ff41;
            font-weight: bold;
            display: inline-block;
            width: 120px;
        }
        .tx-value { color: #ffffff; }
        .hash {
            color: #ff6b35;
            font-size: 0.9em;
            word-break: break-all;
            font-family: 'Monaco', 'Courier New', monospace;
        }
        .timestamp { color: #4ecdc4; }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #00ff41;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #4ecdc4;
            border-top: 2px solid #00ff41;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⛓️ IUS-DIGITALIS BLOCKCHAIN REGISTRY</h1>
            <p class="subtitle">Sistema de Verificación de Integridad Documental</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">📄 Documentos Procesados</div>
                <div class="stat-number">%%TOTAL%%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">⛓️ Transacciones Ancladas</div>
                <div class="stat-number">%%TOTAL%%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">🔐 Estado del Sistema</div>
                <div class="stat-number" style="font-size: 2em;">✅</div>
            </div>
        </div>

        <h2 class="section-title">
            <span class="status-indicator"></span>
            Anclajes Blockchain
        </h2>

        <div id="transactions">%%TRANSACTIONS%%</div>

        <div class="footer">
            <p>🏛️ IUS-DIGITALIS © 2025 | Sistema de Gestión Documental con Blockchain</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Network: Ethereum Mainnet (Simulated)</p>
        </div>
    </div>
</body>
</html>'''

# Generar HTML de transacciones
transactions_html = ""
for i, anchor in enumerate(blockchain_data['anchors'], 1):
    from datetime import datetime
    date = datetime.fromtimestamp(anchor['timestamp'])
    date_str = date.strftime('%d/%m/%Y, %H:%M:%S')
    
    transactions_html += f'''
        <div class="transaction">
            <h3>📄 Transacción #{i}</h3>
            <div class="tx-row">
                <span class="tx-label">Expediente:</span>
                <span class="tx-value">{anchor['expediente_id']}</span>
            </div>
            <div class="tx-row">
                <span class="tx-label">Categoría:</span>
                <span class="tx-value">{anchor['categoria']}</span>
            </div>
            <div class="tx-row">
                <span class="tx-label">SHA-256:</span>
                <span class="hash">{anchor['sha256']}</span>
            </div>
            <div class="tx-row">
                <span class="tx-label">TX ID:</span>
                <span class="hash">{anchor['txid']}</span>
            </div>
            <div class="tx-row">
                <span class="tx-label">Network:</span>
                <span class="tx-value">{anchor['network']}</span>
            </div>
            <div class="tx-row">
                <span class="tx-label">Timestamp:</span>
                <span class="timestamp">{date_str}</span>
            </div>
        </div>
    '''

# Reemplazar placeholders
html_final = html_template.replace('%%TOTAL%%', str(blockchain_data['total']))
html_final = html_final.replace('%%TRANSACTIONS%%', transactions_html)

# Guardar
Path("dashboard_live.html").write_text(html_final, encoding='utf-8')
print("✅ Dashboard actualizado: dashboard_live.html")
