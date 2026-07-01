import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import bcrypt

USE_PG = "DATABASE_URL" in os.environ

if USE_PG:
    import psycopg2
    import psycopg2.extras

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")

MASTER_PASSWORD = os.environ.get("MASTER_PASSWORD", "gtcon@2026")

PLACEHOLDER = "%s" if USE_PG else "?"
LIMIT_SYNTAX = "LIMIT %s OFFSET %s" if USE_PG else "LIMIT ? OFFSET ?"


def get_db():
    if USE_PG:
        conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
        conn.autocommit = False
        return conn
    conn = sqlite3.connect("acessos.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def db_execute(conn, query, params=None):
    if USE_PG:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params or ())
        return cur
    cur = conn.execute(query, params or ())
    return cur


def db_commit(conn):
    conn.commit()


def db_close(conn):
    conn.close()


def init_db():
    conn = get_db()
    if USE_PG:
        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS sheets (
                id SERIAL PRIMARY KEY,
                sheet_name TEXT NOT NULL,
                sheet_key TEXT NOT NULL UNIQUE,
                display_order INTEGER DEFAULT 0
            )
        """)
        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS records (
                id SERIAL PRIMARY KEY,
                sheet_id INTEGER NOT NULL REFERENCES sheets(id),
                departamento TEXT DEFAULT '',
                colaborador TEXT DEFAULT '',
                anydesk TEXT DEFAULT '',
                email TEXT DEFAULT '',
                senha_padrao_anydesk TEXT DEFAULT '',
                onedrive TEXT DEFAULT '',
                certificado_gtcon TEXT DEFAULT '',
                maquina TEXT DEFAULT '',
                senha_maquina TEXT DEFAULT '',
                usuario_exact TEXT DEFAULT '',
                usuario_gtcon TEXT DEFAULT '',
                senha_padrao TEXT DEFAULT '',
                responsavel TEXT DEFAULT '',
                dispositivo TEXT DEFAULT '',
                modelo TEXT DEFAULT '',
                serie TEXT DEFAULT '',
                nome_dispositivo TEXT DEFAULT '',
                processador TEXT DEFAULT '',
                id_dispositivo TEXT DEFAULT '',
                id_produto TEXT DEFAULT '',
                instalado_por TEXT DEFAULT '',
                dia TEXT DEFAULT '',
                descricao TEXT DEFAULT '',
                de_email TEXT DEFAULT '',
                para_email TEXT DEFAULT '',
                novo_email TEXT DEFAULT '',
                observacao TEXT DEFAULT ''
            )
        """)
    else:
        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS sheets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sheet_name TEXT NOT NULL,
                sheet_key TEXT NOT NULL UNIQUE,
                display_order INTEGER DEFAULT 0
            )
        """)
        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sheet_id INTEGER NOT NULL,
                departamento TEXT DEFAULT '',
                colaborador TEXT DEFAULT '',
                anydesk TEXT DEFAULT '',
                email TEXT DEFAULT '',
                senha_padrao_anydesk TEXT DEFAULT '',
                onedrive TEXT DEFAULT '',
                certificado_gtcon TEXT DEFAULT '',
                maquina TEXT DEFAULT '',
                senha_maquina TEXT DEFAULT '',
                usuario_exact TEXT DEFAULT '',
                usuario_gtcon TEXT DEFAULT '',
                senha_padrao TEXT DEFAULT '',
                responsavel TEXT DEFAULT '',
                dispositivo TEXT DEFAULT '',
                modelo TEXT DEFAULT '',
                serie TEXT DEFAULT '',
                nome_dispositivo TEXT DEFAULT '',
                processador TEXT DEFAULT '',
                id_dispositivo TEXT DEFAULT '',
                id_produto TEXT DEFAULT '',
                instalado_por TEXT DEFAULT '',
                dia TEXT DEFAULT '',
                descricao TEXT DEFAULT '',
                de_email TEXT DEFAULT '',
                para_email TEXT DEFAULT '',
                novo_email TEXT DEFAULT '',
                observacao TEXT DEFAULT '',
                FOREIGN KEY (sheet_id) REFERENCES sheets(id)
            )
        """)
    db_commit(conn)
    db_close(conn)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


SHEET_NAMES = [
    "ACESSOS SERVIDOR", "VAGOS", "ENCAMINHADOS", "NIT", "DIRETORIA",
    "DP", "FISCAL", "CONTABIL", "IMPLANTAÇÃO", "COMPLIANCE",
    "LEGALIZAÇÃO", "TRIBUTÁRIO", "CS", "MARKETING", "COMERCIAL",
    "DIVERSOS", "TROCA DE E-MAILS", "INF NOTEBOOK", "CERTIFICADO NAYRA"
]

SHEET_ICONS = {
    "ACESSOS SERVIDOR": "server", "VAGOS": "person-fill-slash",
    "ENCAMINHADOS": "forward", "NIT": "laptop", "DIRETORIA": "people",
    "DP": "person-badge", "FISCAL": "file-earmark-text", "CONTABIL": "calculator",
    "IMPLANTAÇÃO": "gear", "COMPLIANCE": "shield-check", "LEGALIZAÇÃO": "file-earmark-check",
    "TRIBUTÁRIO": "bank", "CS": "headset", "MARKETING": "megaphone",
    "COMERCIAL": "graph-up-arrow", "DIVERSOS": "folder",
    "TROCA DE E-MAILS": "envelope-arrow-left", "INF NOTEBOOK": "pc-display",
    "CERTIFICADO NAYRA": "award",
}

SHEET_COLUMNS = {
    "ACESSOS SERVIDOR": ["usuario_exact", "usuario_gtcon", "senha_padrao", "observacao"],
    "VAGOS": ["departamento", "email", "onedrive", "anydesk", "senha_anydesk", "maquina", "observacao"],
    "ENCAMINHADOS": ["de_email", "para_email", "observacao"],
    "NIT": ["responsavel", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "senha_maquina", "observacao"],
    "DIRETORIA": ["colaborador", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "senha_maquina", "observacao"],
    "DP": ["colaborador", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina", "departamento", "observacao"],
    "FISCAL": ["colaborador", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina", "observacao"],
    "CONTABIL": ["colaborador", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina", "observacao"],
    "IMPLANTAÇÃO": ["colaborador", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina", "observacao"],
    "COMPLIANCE": ["colaborador", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina", "observacao"],
    "LEGALIZAÇÃO": ["colaborador", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina", "observacao"],
    "TRIBUTÁRIO": ["colaborador", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina", "observacao"],
    "CS": ["colaborador", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina", "observacao"],
    "MARKETING": ["colaborador", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina", "observacao"],
    "COMERCIAL": ["colaborador", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina", "observacao"],
    "DIVERSOS": ["descricao", "anydesk", "email", "senha_padrao_anydesk", "onedrive", "senha_maquina", "observacao"],
    "TROCA DE E-MAILS": ["responsavel", "email", "novo_email", "departamento", "observacao"],
    "INF NOTEBOOK": ["dispositivo", "modelo", "serie", "nome_dispositivo", "processador", "id_dispositivo", "id_produto", "colaborador", "anydesk", "observacao"],
    "CERTIFICADO NAYRA": ["instalado_por", "dia", "observacao"],
}

COLUMN_LABELS = {
    "usuario_exact": "Usuário Exact", "usuario_gtcon": "Usuário GTCON",
    "senha_padrao": "Senha Padrão", "departamento": "Departamento",
    "email": "E-mail", "onedrive": "OneDrive", "anydesk": "AnyDesk",
    "senha_anydesk": "Senha AnyDesk", "maquina": "Máquina",
    "colaborador": "Colaborador", "senha_padrao_anydesk": "Senha AnyDesk",
    "certificado_gtcon": "Certificado", "responsavel": "Responsável",
    "descricao": "Descrição", "senha_maquina": "Senha Máquina",
    "de_email": "De (E-mail)", "para_email": "Para (E-mail)",
    "novo_email": "Novo E-mail", "dispositivo": "Dispositivo",
    "modelo": "Modelo", "serie": "Série", "nome_dispositivo": "Nome do Dispositivo",
    "processador": "Processador", "id_dispositivo": "ID Dispositivo",
    "id_produto": "ID Produto", "instalado_por": "Instalado Por",
    "dia": "Dia", "observacao": "Observação",
}


def get_sheet_key(sheet_name):
    name = sheet_name.strip().upper()
    for ch in "ÇÃÁÉÍÓÚÂÊÕ":
        name = name.replace(ch, {"Ç": "C", "Ã": "A", "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Â": "A", "Ê": "E", "Õ": "O"}[ch])
    return name.replace(" ", "_")


def get_sheet_id_by_name(sheet_name):
    conn = get_db()
    key = get_sheet_key(sheet_name)
    cur = db_execute(conn, f"SELECT id FROM sheets WHERE sheet_key = {PLACEHOLDER}", (key,))
    sheet = cur.fetchone()
    db_close(conn)
    return sheet["id"] if sheet else None


@app.route("/")
def root():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    error = ""
    if request.method == "POST":
        if request.form.get("password", "") == MASTER_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        error = "Senha incorreta!"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    counts = {}
    for sheet_name in SHEET_NAMES:
        key = get_sheet_key(sheet_name)
        cur = db_execute(conn, f"SELECT id, sheet_name FROM sheets WHERE sheet_key = {PLACEHOLDER}", (key,))
        sheet = cur.fetchone()
        if sheet:
            cur2 = db_execute(conn, f"SELECT COUNT(*) as cnt FROM records WHERE sheet_id = {PLACEHOLDER}", (sheet["id"],))
            counts[sheet_name] = cur2.fetchone()["cnt"]
        else:
            counts[sheet_name] = 0
    db_close(conn)
    return render_template("dashboard.html", sheets=SHEET_NAMES, counts=counts, icons=SHEET_ICONS)


@app.route("/sheet/<sheet_name>")
@login_required
def view_sheet(sheet_name):
    if sheet_name not in SHEET_NAMES:
        flash("Aba não encontrada!", "danger")
        return redirect(url_for("dashboard"))

    sheet_id = get_sheet_id_by_name(sheet_name)
    if not sheet_id:
        flash("Aba não encontrada!", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db()
    page = request.args.get("page", 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page

    cur = db_execute(conn, f"SELECT COUNT(*) as cnt FROM records WHERE sheet_id = {PLACEHOLDER}", (sheet_id,))
    total = cur.fetchone()["cnt"]
    cur = db_execute(conn, f"SELECT * FROM records WHERE sheet_id = {PLACEHOLDER} ORDER BY id {LIMIT_SYNTAX}", (sheet_id, per_page, offset))
    records = cur.fetchall()
    db_close(conn)

    columns = SHEET_COLUMNS.get(sheet_name, [])
    total_pages = max(1, (total + per_page - 1) // per_page)

    return render_template("sheet.html", sheet_name=sheet_name, columns=columns,
        labels=COLUMN_LABELS, records=records, page=page,
        total_pages=total_pages, total=total, icons=SHEET_ICONS, sheets=SHEET_NAMES)


def get_field_map():
    fields = ["departamento", "colaborador", "anydesk", "email",
        "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina",
        "senha_maquina", "usuario_exact", "usuario_gtcon", "senha_padrao",
        "responsavel", "dispositivo", "modelo", "serie", "nome_dispositivo",
        "processador", "id_dispositivo", "id_produto", "instalado_por", "dia",
        "descricao", "de_email", "para_email", "novo_email", "observacao"]
    return {f: request.form.get(f, "") for f in fields}


RECORD_FIELDS = ["departamento", "colaborador", "anydesk", "email",
    "senha_padrao_anydesk", "onedrive", "certificado_gtcon", "maquina",
    "senha_maquina", "usuario_exact", "usuario_gtcon", "senha_padrao",
    "responsavel", "dispositivo", "modelo", "serie", "nome_dispositivo",
    "processador", "id_dispositivo", "id_produto", "instalado_por", "dia",
    "descricao", "de_email", "para_email", "novo_email", "observacao"]

RECORD_INSERT_SQL = f"""
    INSERT INTO records (
        sheet_id, {', '.join(RECORD_FIELDS)}
    ) VALUES ({PLACEHOLDER}, {', '.join([PLACEHOLDER] * len(RECORD_FIELDS))})
"""

RECORD_UPDATE_SQL = f"""
    UPDATE records SET
        {', '.join(f'{f}={PLACEHOLDER}' for f in RECORD_FIELDS)}
    WHERE id = {PLACEHOLDER}
"""


@app.route("/sheet/<sheet_name>/add", methods=["GET", "POST"])
@login_required
def add_record(sheet_name):
    if sheet_name not in SHEET_NAMES:
        flash("Aba não encontrada!", "danger")
        return redirect(url_for("dashboard"))

    columns = SHEET_COLUMNS.get(sheet_name, [])
    if request.method == "POST":
        conn = get_db()
        sheet_id = get_sheet_id_by_name(sheet_name)
        fm = get_field_map()
        values = [sheet_id] + [fm[f] for f in RECORD_FIELDS]
        db_execute(conn, RECORD_INSERT_SQL, tuple(values))
        db_commit(conn)
        db_close(conn)
        flash("Registro adicionado com sucesso!", "success")
        return redirect(url_for("view_sheet", sheet_name=sheet_name))

    active_fields = [c for c in columns if c in COLUMN_LABELS]
    return render_template("add_edit.html", sheet_name=sheet_name,
        columns=active_fields, labels=COLUMN_LABELS, record=None,
        action="Adicionar", icons=SHEET_ICONS, sheets=SHEET_NAMES)


@app.route("/sheet/<sheet_name>/edit/<int:record_id>", methods=["GET", "POST"])
@login_required
def edit_record(sheet_name, record_id):
    if sheet_name not in SHEET_NAMES:
        flash("Aba não encontrada!", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db()
    cur = db_execute(conn, f"SELECT * FROM records WHERE id = {PLACEHOLDER}", (record_id,))
    record = cur.fetchone()
    if not record:
        db_close(conn)
        flash("Registro não encontrado!", "danger")
        return redirect(url_for("view_sheet", sheet_name=sheet_name))

    columns = SHEET_COLUMNS.get(sheet_name, [])

    if request.method == "POST":
        fm = get_field_map()
        values = [fm[f] for f in RECORD_FIELDS] + [record_id]
        db_execute(conn, RECORD_UPDATE_SQL, tuple(values))
        db_commit(conn)
        db_close(conn)
        flash("Registro atualizado com sucesso!", "success")
        return redirect(url_for("view_sheet", sheet_name=sheet_name))

    db_close(conn)
    active_fields = [c for c in columns if c in COLUMN_LABELS]
    return render_template("add_edit.html", sheet_name=sheet_name,
        columns=active_fields, labels=COLUMN_LABELS, record=record,
        action="Editar", icons=SHEET_ICONS, sheets=SHEET_NAMES)


@app.route("/sheet/<sheet_name>/delete/<int:record_id>", methods=["POST"])
@login_required
def delete_record(sheet_name, record_id):
    conn = get_db()
    db_execute(conn, f"DELETE FROM records WHERE id = {PLACEHOLDER}", (record_id,))
    db_commit(conn)
    db_close(conn)
    flash("Registro excluído com sucesso!", "success")
    return redirect(url_for("view_sheet", sheet_name=sheet_name))


@app.route("/search")
@login_required
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        conn = get_db()
        term = f"%{q}%"
        cur = db_execute(conn, f"""
            SELECT r.*, s.sheet_name as sheet_display_name
            FROM records r
            JOIN sheets s ON r.sheet_id = s.id
            WHERE r.colaborador LIKE {PLACEHOLDER}
               OR r.email LIKE {PLACEHOLDER}
               OR r.responsavel LIKE {PLACEHOLDER}
               OR r.usuario_gtcon LIKE {PLACEHOLDER}
               OR r.dispositivo LIKE {PLACEHOLDER}
               OR r.descricao LIKE {PLACEHOLDER}
               OR r.de_email LIKE {PLACEHOLDER}
               OR r.para_email LIKE {PLACEHOLDER}
               OR r.novo_email LIKE {PLACEHOLDER}
               OR r.instalado_por LIKE {PLACEHOLDER}
               OR r.anydesk LIKE {PLACEHOLDER}
            ORDER BY s.display_order, r.id
            LIMIT 100
        """, tuple([term] * 11))
        results = cur.fetchall()
        db_close(conn)

    return render_template("search.html", results=results, query=q,
        labels=COLUMN_LABELS, icons=SHEET_ICONS, sheets=SHEET_NAMES)


@app.route("/api/search")
@login_required
def api_search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        conn = get_db()
        term = f"%{q}%"
        cur = db_execute(conn, f"""
            SELECT r.*, s.sheet_name as sheet_display_name
            FROM records r
            JOIN sheets s ON r.sheet_id = s.id
            WHERE r.colaborador LIKE {PLACEHOLDER}
               OR r.email LIKE {PLACEHOLDER}
               OR r.responsavel LIKE {PLACEHOLDER}
               OR r.usuario_gtcon LIKE {PLACEHOLDER}
            ORDER BY s.display_order, r.id
            LIMIT 20
        """, tuple([term] * 4))
        for r in cur.fetchall():
            results.append({
                "id": r["id"], "sheet_name": r["sheet_display_name"],
                "colaborador": r["colaborador"], "email": r["email"],
                "anydesk": r["anydesk"],
            })
        db_close(conn)
    return jsonify(results)


if __name__ == "__main__":
    print("=" * 60)
    print("  GTCON - Sistema de Controle de Acessos")
    print("  Banco:", "PostgreSQL" if USE_PG else "SQLite")
    print("  Senha mestra:", MASTER_PASSWORD)
    print("=" * 60)

    init_db()

    conn = get_db()
    cur = db_execute(conn, f"SELECT COUNT(*) as cnt FROM sheets")
    sheet_count = cur.fetchone()["cnt"]
    db_close(conn)

    if sheet_count == 0:
        print("\n[INFO] Banco vazio. Importando dados do Excel...")
        try:
            from import_data import import_all
            import_all()
            print("[OK] Importação concluída!\n")
        except Exception as e:
            print(f"[ERRO] Falha ao importar dados: {e}")
            print("[INFO] Certifique-se de que o arquivo 'Acessos GTCON.xlsx' está no diretório.")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
