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

## Gerador de Horários de Aula (Faculdade - Noturno)

Também há uma CLI para montar grade automaticamente minimizando choques de horário de professor/turma e reduzindo dias de ida do professor.

### Instalação
Após `pip install -e .`, use:

```bash
class-scheduler --professors-csv professores.csv --disciplines-csv disciplinas.csv --output grade.csv
```

### Regras usadas
- Período noturno fixo: `18:30-19:20`, `19:20-20:10`, `20:10-21:00`, `21:00-21:50`.
- Dias: segunda a sexta (`Seg` a `Sex`).
- Evita choque de professor no mesmo dia/horário.
- Evita choque de turma (curso+turma) no mesmo dia/horário.
- Prefere dias de preferência do professor.
- Tenta concentrar aulas no menor número de dias por professor.

### Formato CSV ideal

#### `professores.csv`
Colunas obrigatórias:
- `professor`: nome do professor
- `preferred_days`: dias preferidos separados por `;` ou `,` (ex.: `Seg;Ter`)

Exemplo:
```csv
professor,preferred_days
Ana,Seg;Ter
Bruno,Qua;Qui
Carlos,Seg
```

#### `disciplinas.csv`
Colunas obrigatórias:
- `discipline`: nome da disciplina
- `course`: curso
- `turma`: turma
- `weekly_classes`: quantidade de aulas semanais
- `professor`: professor responsável

Exemplo:
```csv
discipline,course,turma,weekly_classes,professor
Calculo I,Engenharia,1A,2,Ana
Fisica I,Engenharia,1A,2,Bruno
Banco de Dados,ADS,2A,2,Carlos
Redes,ADS,3A,2,Carlos
```

### Saída
Arquivo `grade.csv` com colunas:
- `day`, `slot`, `course`, `turma`, `discipline`, `professor`.
