# 📄 PDF Merge Automation

Script em Python para processar, filtrar páginas e consolidar múltiplos resumos em PDF em um único arquivo unificado, com ordenação inteligente e geração automática de marcadores (bookmarks/sumário).

---

## 🎯 Objetivo e Regras de Negócio

1. **Prioridade Customizada:** O arquivo principal (`1_TI TOTAL - Aula 26 - ISO 27002 - Resumo.pdf`) é colocado como o primeiro da fila e mantém **todas** as suas páginas.
2. **Descarte da Primeira Página:** Os demais PDFs têm sua primeira página (capa/introdução padrão) descartada, aproveitando apenas da página 2 em diante.
3. **Ordenação Natural:** Organiza os arquivos por ordenação natural (ex: Aula 2 antes de Aula 10), garantindo a sequência correta das aulas.
4. **Navegação Integrada:** Gera marcadores interativos (sumário/outline) no leitor de PDF apontando diretamente para o início de cada aula.
5. **Robustez:** Tratamento seguro para arquivos de página única e relatórios detalhados no terminal.

---

## 📁 Estrutura do Projeto

```text
.
├── merge_pdfs.py           # Script principal de automação
├── requirements.txt        # Dependências do projeto (pypdf)
├── .gitignore             # Ignora ambiente virtual (.venv) e arquivos PDF
├── README.md               # Documentação do projeto
└── pdfs/                   # Diretório com os arquivos PDF locais (ignorado no git)
```

---

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.

### 2. Configurar o Ambiente Virtual

No terminal (PowerShell ou Bash):

```powershell
# Criação do ambiente virtual
python -m venv .venv

# Ativação no Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Instalação das dependências
pip install -r requirements.txt
```

### 3. Execução

Coloque os arquivos `.pdf` na pasta `pdfs/` (ou na raiz do projeto) e execute:

```powershell
python merge_pdfs.py
```

O arquivo consolidado `TI_TOTAL_Compilado.pdf` será gerado automaticamente.

### 4. Parâmetros Opcionais

O script conta com interface CLI configurável:

```powershell
# Especificar uma pasta personalizada de entrada
python merge_pdfs.py --dir "caminho/para/pasta"

# Definir um nome de arquivo de saída customizado
python merge_pdfs.py -o "Meu_Resumo_Completo.pdf"

# Desativar a inclusão de marcadores/sumário
python merge_pdfs.py --no-bookmarks
```

---

## 🛠️ Tecnologias

- [Python 3](https://www.python.org/)
- [pypdf](https://pypdf.readthedocs.io/)
