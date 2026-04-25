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

---

## Extra: análise de variantes missense no SIFT (CDKN2A)

Também foi incluído um CLI para anotação em lote no **SIFT** usando o endpoint oficial do **Ensembl VEP**:

```bash
sift-cdkn2a --input variantes.csv --output sift_results.csv
```

Para um passo-a-passo completo em português-br, veja:
`docs/tutorial_sift_cdkn2a_ptbr.md`.

Se você quer uma versão **bem simples (para leigos)**, veja:
`docs/guia_leigo_rodando_programa.md`.
O guia inclui comandos separados para **Windows (PowerShell/CMD)** e **Linux Ubuntu**.

Você também pode gerar um CSV modelo automaticamente:

```bash
sift-cdkn2a --input variantes_cdkn2a.csv --write-template
```

### Formato de entrada (CSV)
Use uma destas opções:

1) Coluna `hgvs` pronta (recomendado para máxima precisão):
```csv
id,hgvs
v1,ENST00000380151:p.Gly101Trp
v2,ENST00000380151:p.Arg24Pro
```

2) Coluna `protein_change` (o programa monta HGVS com um transcript padrão):
```csv
id,protein_change,transcript
v1,p.Gly101Trp,ENST00000380151
v2,R24P,ENST00000380151
```

### Recursos para velocidade e robustez
- Execução paralela com `--workers` (padrão 8)
- Retries automáticos para 429/5xx com backoff (`--retries`)
- Timeout configurável por request (`--timeout`)
- Saída CSV padronizada com `sift_prediction`, `sift_score` e `status`

Exemplo:
```bash
sift-cdkn2a \
  --input variantes.csv \
  --output resultados_sift_cdkn2a.csv \
  --workers 12 \
  --retries 4 \
  --timeout 20
```

### Comparação automática SIFT vs AlphaMissense
Depois de gerar os resultados do SIFT, você pode cruzar com uma tabela AlphaMissense:

```bash
compare-sift-alphamissense \
  --sift resultados_sift_cdkn2a.csv \
  --alpha examples/alphamissense_exemplo.csv \
  --output comparativo_sift_alphamissense.csv \
  --summary resumo_comparativo.csv
```
