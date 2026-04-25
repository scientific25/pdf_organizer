# PDF Organizer (Books) — por tema

CLI em Python para **organizar PDFs (livros)** em pastas por **tema/categoria**, baseado em:
- metadados (título do PDF, quando existir)
- texto extraído das **primeiras páginas**

## Instalação (Ubuntu / Linux / macOS / Windows)

Requer Python 3.10+.

### Opção A (recomendada): venv + pip
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### Opção B: pip direto
```bash
pip install -e .
```

## Uso

### Organizar (copiar) PDFs em pastas por categoria
```bash
pdf-organizer --input "/caminho/pdfs" --output "/caminho/saida" --mode copy
```

### Mover em vez de copiar
```bash
pdf-organizer --input "/caminho/pdfs" --output "/caminho/saida" --mode move
```

### Simular (não copia/move) — só report
```bash
pdf-organizer --input "/caminho/pdfs" --output "/caminho/saida" --dry-run
```

### Classificar só pelo nome do arquivo (sem abrir PDFs)
```bash
pdf-organizer --input "/caminho/pdfs" --output "/caminho/saida" --classify-by filename
```

### Customizar categorias/palavras-chave
Edite `categories.yaml` ou use outro arquivo:
```bash
pdf-organizer --input "/caminho/pdfs" --output "/caminho/saida" --config "/caminho/meu.yaml"
```

## Saídas
- Pastas por categoria em `OUTPUT_DIR/<Categoria>/`
- Relatório `catalogo.csv` no `OUTPUT_DIR/` com:
  - original_path, source_folder, new_path, category, confidence, matched_keywords, title

## Observações importantes
- PDF **escaneado** (sem texto) pode cair em categoria com baixa confiança ou "Outros".
- O classificador do MVP é baseado em **palavras-chave** (rápido e transparente).
  Depois você pode evoluir para embeddings/LLM se quiser.

## Automação de Microsoft Forms (Windows) — passo a passo

### Arquivos já prontos
- `respostas_modelo_60_linhas.csv`: tabela modelo com 12 colunas e 60 linhas para você preencher.
- `form_mapping.example.json`: exemplo de mapeamento entre colunas e perguntas.

### 1) Instale o programa
No Windows (PowerShell):
```powershell
cd C:\caminho\para\pdf_organizer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
playwright install chromium
```

### 2) Gere um mapeamento inicial automaticamente
Esse comando abre o formulário e tenta detectar os títulos das perguntas, criando um JSON inicial:
```powershell
ms-form-bot \
  --form-url "https://forms.cloud.microsoft/pages/responsepage.aspx?id=..." \
  --init-mapping "C:\dados\form_mapping.json"
```

### 3) Ajuste manualmente o `form_mapping.json`
- Revise cada item `question` para corresponder exatamente ao título da pergunta no formulário.
- Defina o tipo correto: `text`, `radio`, `checkbox` ou `dropdown`.
- Para `checkbox`, pode usar `separator` (`;` por padrão).

### 4) Preencha sua planilha com as 60 respostas
Use `respostas_modelo_60_linhas.csv` como base:
- 12 colunas (cada coluna = 1 pergunta)
- 60 linhas (cada linha = 1 submissão completa)

### 5) Execute o envio automático
```powershell
ms-form-bot \
  --form-url "https://forms.cloud.microsoft/pages/responsepage.aspx?id=..." \
  --sheet "C:\dados\respostas_modelo_60_linhas.csv" \
  --mapping "C:\dados\form_mapping.json" \
  --limit 60 \
  --skip-header
```

### Dicas úteis
- Remova `--headless` para ver o navegador em ação.
- Use `--submit-label "Enviar"` se o botão final não for detectado automaticamente.
- Cada linha da planilha gera **uma submissão completa** do formulário.
- Linhas totalmente vazias são ignoradas.
