import sqlite3
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import bcrypt

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

DB_PATH = "acessos.db"
MASTER_PASSWORD = "gtcon@2026"

MASTER_HASH = bcrypt.hashpw(MASTER_PASSWORD.encode(), bcrypt.gensalt())


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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
    "ACESSOS SERVIDOR": "server",
    "VAGOS": "person-fill-slash",
    "ENCAMINHADOS": "forward",
    "NIT": "laptop",
    "DIRETORIA": "people",
    "DP": "person-badge",
    "FISCAL": "file-earmark-text",
    "CONTABIL": "calculator",
    "IMPLANTAÇÃO": "gear",
    "COMPLIANCE": "shield-check",
    "LEGALIZAÇÃO": "file-earmark-check",
    "TRIBUTÁRIO": "bank",
    "CS": "headset",
    "MARKETING": "megaphone",
    "COMERCIAL": "graph-up-arrow",
    "DIVERSOS": "folder",
    "TROCA DE E-MAILS": "envelope-arrow-left",
    "INF NOTEBOOK": "pc-display",
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
    "usuario_exact": "Usuário Exact",
    "usuario_gtcon": "Usuário GTCON",
    "senha_padrao": "Senha Padrão",
    "departamento": "Departamento",
    "email": "E-mail",
    "onedrive": "OneDrive",
    "anydesk": "AnyDesk",
    "senha_anydesk": "Senha AnyDesk",
    "maquina": "Máquina",
    "colaborador": "Colaborador",
    "senha_padrao_anydesk": "Senha AnyDesk",
    "certificado_gtcon": "Certificado",
    "responsavel": "Responsável",
    "descricao": "Descrição",
    "senha_maquina": "Senha Máquina",
    "de_email": "De (E-mail)",
    "para_email": "Para (E-mail)",
    "novo_email": "Novo E-mail",
    "dispositivo": "Dispositivo",
    "modelo": "Modelo",
    "serie": "Série",
    "nome_dispositivo": "Nome do Dispositivo",
    "processador": "Processador",
    "id_dispositivo": "ID Dispositivo",
    "id_produto": "ID Produto",
    "instalado_por": "Instalado Por",
    "dia": "Dia",
    "observacao": "Observação",
}


def get_sheet_key(sheet_name):
    name = sheet_name.strip().upper()
    name = name.replace(" ", "_").replace("Ç", "C").replace("Ã", "A")
    name = name.replace("Á", "A").replace("É", "E").replace("Í", "I")
    name = name.replace("Ó", "O").replace("Ú", "U").replace("Â", "A")
    name = name.replace("Ê", "E").replace("Õ", "O")
    return name


def get_sheet_id_by_name(sheet_name):
    conn = get_db()
    key = get_sheet_key(sheet_name)
    sheet = conn.execute("SELECT id FROM sheets WHERE sheet_key = ?", (key,)).fetchone()
    conn.close()
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
        password = request.form.get("password", "")
        if password == MASTER_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
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
        sheet = conn.execute("SELECT id, sheet_name FROM sheets WHERE sheet_key = ?", (key,)).fetchone()
        if sheet:
            count = conn.execute("SELECT COUNT(*) as cnt FROM records WHERE sheet_id = ?", (sheet["id"],)).fetchone()
            counts[sheet_name] = count["cnt"]
        else:
            counts[sheet_name] = 0
    conn.close()
    return render_template("dashboard.html", sheets=SHEET_NAMES, counts=counts, icons=SHEET_ICONS)


@app.route("/sheet/<sheet_name>")
@login_required
def view_sheet(sheet_name):
    if sheet_name not in SHEET_NAMES:
        flash("Aba não encontrada!", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db()
    sheet_id = get_sheet_id_by_name(sheet_name)
    if not sheet_id:
        conn.close()
        flash("Aba não encontrada!", "danger")
        return redirect(url_for("dashboard"))

    page = request.args.get("page", 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page

    total = conn.execute("SELECT COUNT(*) as cnt FROM records WHERE sheet_id = ?", (sheet_id,)).fetchone()["cnt"]
    records = conn.execute(
        "SELECT * FROM records WHERE sheet_id = ? ORDER BY id LIMIT ? OFFSET ?",
        (sheet_id, per_page, offset)
    ).fetchall()
    conn.close()

    columns = SHEET_COLUMNS.get(sheet_name, [])
    total_pages = max(1, (total + per_page - 1) // per_page)

    return render_template(
        "sheet.html",
        sheet_name=sheet_name,
        columns=columns,
        labels=COLUMN_LABELS,
        records=records,
        page=page,
        total_pages=total_pages,
        total=total,
        icons=SHEET_ICONS,
        sheets=SHEET_NAMES,
    )


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

        field_map = {
            "departamento": request.form.get("departamento", ""),
            "colaborador": request.form.get("colaborador", ""),
            "anydesk": request.form.get("anydesk", ""),
            "email": request.form.get("email", ""),
            "senha_padrao_anydesk": request.form.get("senha_padrao_anydesk", ""),
            "onedrive": request.form.get("onedrive", ""),
            "certificado_gtcon": request.form.get("certificado_gtcon", ""),
            "maquina": request.form.get("maquina", ""),
            "senha_maquina": request.form.get("senha_maquina", ""),
            "usuario_exact": request.form.get("usuario_exact", ""),
            "usuario_gtcon": request.form.get("usuario_gtcon", ""),
            "senha_padrao": request.form.get("senha_padrao", ""),
            "responsavel": request.form.get("responsavel", ""),
            "dispositivo": request.form.get("dispositivo", ""),
            "modelo": request.form.get("modelo", ""),
            "serie": request.form.get("serie", ""),
            "nome_dispositivo": request.form.get("nome_dispositivo", ""),
            "processador": request.form.get("processador", ""),
            "id_dispositivo": request.form.get("id_dispositivo", ""),
            "id_produto": request.form.get("id_produto", ""),
            "instalado_por": request.form.get("instalado_por", ""),
            "dia": request.form.get("dia", ""),
            "descricao": request.form.get("descricao", ""),
            "de_email": request.form.get("de_email", ""),
            "para_email": request.form.get("para_email", ""),
            "novo_email": request.form.get("novo_email", ""),
            "observacao": request.form.get("observacao", ""),
        }

        conn.execute("""
            INSERT INTO records (
                sheet_id, departamento, colaborador, anydesk, email,
                senha_padrao_anydesk, onedrive, certificado_gtcon, maquina,
                senha_maquina, usuario_exact, usuario_gtcon, senha_padrao,
                responsavel, dispositivo, modelo, serie, nome_dispositivo,
                processador, id_dispositivo, id_produto, instalado_por, dia,
                descricao, de_email, para_email, novo_email, observacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sheet_id,
            field_map["departamento"], field_map["colaborador"], field_map["anydesk"],
            field_map["email"], field_map["senha_padrao_anydesk"], field_map["onedrive"],
            field_map["certificado_gtcon"], field_map["maquina"], field_map["senha_maquina"],
            field_map["usuario_exact"], field_map["usuario_gtcon"], field_map["senha_padrao"],
            field_map["responsavel"], field_map["dispositivo"], field_map["modelo"],
            field_map["serie"], field_map["nome_dispositivo"], field_map["processador"],
            field_map["id_dispositivo"], field_map["id_produto"], field_map["instalado_por"],
            field_map["dia"], field_map["descricao"], field_map["de_email"],
            field_map["para_email"], field_map["novo_email"], field_map["observacao"],
        ))
        conn.commit()
        conn.close()
        flash("Registro adicionado com sucesso!", "success")
        return redirect(url_for("view_sheet", sheet_name=sheet_name))

    active_fields = [c for c in columns if c in COLUMN_LABELS]
    return render_template(
        "add_edit.html", sheet_name=sheet_name, columns=active_fields,
        labels=COLUMN_LABELS, record=None, action="Adicionar",
        icons=SHEET_ICONS, sheets=SHEET_NAMES,
    )


@app.route("/sheet/<sheet_name>/edit/<int:record_id>", methods=["GET", "POST"])
@login_required
def edit_record(sheet_name, record_id):
    if sheet_name not in SHEET_NAMES:
        flash("Aba não encontrada!", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db()
    record = conn.execute("SELECT * FROM records WHERE id = ?", (record_id,)).fetchone()
    if not record:
        conn.close()
        flash("Registro não encontrado!", "danger")
        return redirect(url_for("view_sheet", sheet_name=sheet_name))

    columns = SHEET_COLUMNS.get(sheet_name, [])

    if request.method == "POST":
        field_map = {
            "departamento": request.form.get("departamento", ""),
            "colaborador": request.form.get("colaborador", ""),
            "anydesk": request.form.get("anydesk", ""),
            "email": request.form.get("email", ""),
            "senha_padrao_anydesk": request.form.get("senha_padrao_anydesk", ""),
            "onedrive": request.form.get("onedrive", ""),
            "certificado_gtcon": request.form.get("certificado_gtcon", ""),
            "maquina": request.form.get("maquina", ""),
            "senha_maquina": request.form.get("senha_maquina", ""),
            "usuario_exact": request.form.get("usuario_exact", ""),
            "usuario_gtcon": request.form.get("usuario_gtcon", ""),
            "senha_padrao": request.form.get("senha_padrao", ""),
            "responsavel": request.form.get("responsavel", ""),
            "dispositivo": request.form.get("dispositivo", ""),
            "modelo": request.form.get("modelo", ""),
            "serie": request.form.get("serie", ""),
            "nome_dispositivo": request.form.get("nome_dispositivo", ""),
            "processador": request.form.get("processador", ""),
            "id_dispositivo": request.form.get("id_dispositivo", ""),
            "id_produto": request.form.get("id_produto", ""),
            "instalado_por": request.form.get("instalado_por", ""),
            "dia": request.form.get("dia", ""),
            "descricao": request.form.get("descricao", ""),
            "de_email": request.form.get("de_email", ""),
            "para_email": request.form.get("para_email", ""),
            "novo_email": request.form.get("novo_email", ""),
            "observacao": request.form.get("observacao", ""),
        }

        conn.execute("""
            UPDATE records SET
                departamento=?, colaborador=?, anydesk=?, email=?,
                senha_padrao_anydesk=?, onedrive=?, certificado_gtcon=?, maquina=?,
                senha_maquina=?, usuario_exact=?, usuario_gtcon=?, senha_padrao=?,
                responsavel=?, dispositivo=?, modelo=?, serie=?, nome_dispositivo=?,
                processador=?, id_dispositivo=?, id_produto=?, instalado_por=?, dia=?,
                descricao=?, de_email=?, para_email=?, novo_email=?, observacao=?
            WHERE id = ?
        """, (
            field_map["departamento"], field_map["colaborador"], field_map["anydesk"],
            field_map["email"], field_map["senha_padrao_anydesk"], field_map["onedrive"],
            field_map["certificado_gtcon"], field_map["maquina"], field_map["senha_maquina"],
            field_map["usuario_exact"], field_map["usuario_gtcon"], field_map["senha_padrao"],
            field_map["responsavel"], field_map["dispositivo"], field_map["modelo"],
            field_map["serie"], field_map["nome_dispositivo"], field_map["processador"],
            field_map["id_dispositivo"], field_map["id_produto"], field_map["instalado_por"],
            field_map["dia"], field_map["descricao"], field_map["de_email"],
            field_map["para_email"], field_map["novo_email"], field_map["observacao"],
            record_id,
        ))
        conn.commit()
        conn.close()
        flash("Registro atualizado com sucesso!", "success")
        return redirect(url_for("view_sheet", sheet_name=sheet_name))

    conn.close()
    active_fields = [c for c in columns if c in COLUMN_LABELS]
    return render_template(
        "add_edit.html", sheet_name=sheet_name, columns=active_fields,
        labels=COLUMN_LABELS, record=record, action="Editar",
        icons=SHEET_ICONS, sheets=SHEET_NAMES,
    )


@app.route("/sheet/<sheet_name>/delete/<int:record_id>", methods=["POST"])
@login_required
def delete_record(sheet_name, record_id):
    conn = get_db()
    conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
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
        records = conn.execute("""
            SELECT r.*, s.sheet_name as sheet_display_name
            FROM records r
            JOIN sheets s ON r.sheet_id = s.id
            WHERE r.colaborador LIKE ?
               OR r.email LIKE ?
               OR r.responsavel LIKE ?
               OR r.usuario_gtcon LIKE ?
               OR r.dispositivo LIKE ?
               OR r.descricao LIKE ?
               OR r.de_email LIKE ?
               OR r.para_email LIKE ?
               OR r.novo_email LIKE ?
               OR r.instalado_por LIKE ?
               OR r.anydesk LIKE ?
            ORDER BY s.display_order, r.id
            LIMIT 100
        """, (term, term, term, term, term, term, term, term, term, term, term)).fetchall()
        conn.close()
        results = records

    return render_template(
        "search.html", results=results, query=q,
        labels=COLUMN_LABELS, icons=SHEET_ICONS, sheets=SHEET_NAMES,
    )


@app.route("/api/search")
@login_required
def api_search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        conn = get_db()
        term = f"%{q}%"
        records = conn.execute("""
            SELECT r.*, s.sheet_name as sheet_display_name
            FROM records r
            JOIN sheets s ON r.sheet_id = s.id
            WHERE r.colaborador LIKE ?
               OR r.email LIKE ?
               OR r.responsavel LIKE ?
               OR r.usuario_gtcon LIKE ?
            ORDER BY s.display_order, r.id
            LIMIT 20
        """, (term, term, term, term)).fetchall()
        conn.close()
        for r in records:
            results.append({
                "id": r["id"],
                "sheet_name": r["sheet_display_name"],
                "colaborador": r["colaborador"],
                "email": r["email"],
                "anydesk": r["anydesk"],
            })
    return jsonify(results)


if __name__ == "__main__":
    print("=" * 60)
    print("  GTCON - Sistema de Controle de Acessos")
    print("  Senha mestra: gtcon@2026")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print("\n[INFO] Banco de dados não encontrado. Importando dados do Excel...")
        try:
            from import_data import import_all
            import_all()
            print("[OK] Importação concluída!\n")
        except Exception as e:
            print(f"[ERRO] Falha ao importar dados: {e}")
            print("[INFO] Certifique-se de que o arquivo 'Acessos GTCON.xlsx' está no diretório.")

    app.run(host="0.0.0.0", port=5000, debug=True)
