# GTCON - Sistema de Controle de Acessos

Sistema web para gerenciamento centralizado de acessos, colaboradores, dispositivos e credenciais da GTCON.

## Funcionalidades

- **19 abas** organizadas por departamento (DP, FISCAL, CONTÁBIL, COMERCIAL, etc.)
- **Dashboard** com visão geral de todos os setores
- **Busca global** por colaborador, e-mail, AnyDesk
- **CRUD completo** (criar, editar, excluir registros)
- **Proteção por senha mestra**
- **Interface moderna** com tema escuro, responsiva
- **Exportação** integrada (visualização de senhas com copy-paste)

## Requisitos

- Python 3.10+
- Windows, Linux ou macOS

## Instalação

```bash
pip install flask openpyxl bcrypt
```

## Como usar

1. Coloque o arquivo `Acessos GTCON.xlsx` na mesma pasta do sistema
2. Execute:

```bash
python app.py
```

3. Acesse no navegador: `http://localhost:5000`
4. Senha mestra: `gtcon@2026`

O banco de dados é criado automaticamente na primeira execução.

## Estrutura

```
├── app.py              # Aplicação Flask principal
├── import_data.py      # Importador de dados do Excel
├── acessos.db          # Banco SQLite (gerado automaticamente)
├── templates/          # Templates HTML
│   ├── layout.html     # Layout base com sidebar
│   ├── login.html      # Tela de login
│   ├── dashboard.html  # Dashboard principal
│   ├── sheet.html      # Visualização de aba
│   ├── add_edit.html   # Formulário de cadastro/edição
│   └── search.html     # Resultados da busca
└── static/
    └── style.css       # Estilos personalizados
```
