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
