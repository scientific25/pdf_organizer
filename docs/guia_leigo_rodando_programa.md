# Guia para leigos: como rodar o programa (passo a passo)

Este guia é para quem **nunca programou** e quer apenas executar as análises.

---

## O que você vai conseguir fazer

1. Rodar SIFT para suas variantes do gene **CDKN2A**.
2. Comparar o resultado com uma tabela do **AlphaMissense**.
3. Receber arquivos `.csv` prontos para abrir no Excel.

---

## 1) Instalar o Python

1. Entre em: https://www.python.org/downloads/
2. Baixe o Python 3.10 ou superior.
3. Durante a instalação no Windows, marque a opção:
   - **Add Python to PATH**
4. Finalize a instalação.

### Como conferir se deu certo
Abra o terminal e rode:

```bash
python --version
```

Se aparecer algo como `Python 3.11.x`, está ok.

---

## 2) Abrir a pasta do projeto no terminal

Você precisa entrar na pasta onde está este projeto.

Exemplo (ajuste para sua pasta real):

```bash
cd /caminho/para/pdf_organizer
```

---

## 3) Preparar o ambiente (Windows e Linux Ubuntu)

### Linux (Ubuntu)
Rode, nessa ordem:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

### Windows (PowerShell)
Rode, nessa ordem:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -U pip
py -m pip install -e .
```

### Windows (Prompt de Comando / CMD)
Rode, nessa ordem:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install -U pip
py -m pip install -e .
```

---

## 4) Criar planilha modelo das variantes

Digite:

```bash
sift-cdkn2a --input variantes_cdkn2a.csv --write-template
```

Isso cria o arquivo `variantes_cdkn2a.csv`.

Abra esse arquivo no Excel e preencha suas variantes.

---

## 5) Rodar análise SIFT

Com o arquivo preenchido, rode:

```bash
sift-cdkn2a \
  --input variantes_cdkn2a.csv \
  --output resultados_sift_cdkn2a.csv
```

No final, você terá `resultados_sift_cdkn2a.csv`.

---

## 6) Preparar arquivo do AlphaMissense

Crie (ou use) um CSV com estas colunas mínimas:

- `variant_id` (igual ao ID da variante usado no SIFT)
- `am_class` (exemplo: `pathogenic`, `likely_pathogenic`, `benign`)
- `am_score`

Você pode usar como modelo:

- `examples/alphamissense_exemplo.csv`

---

## 7) Comparar SIFT vs AlphaMissense

Rode:

```bash
compare-sift-alphamissense \
  --sift resultados_sift_cdkn2a.csv \
  --alpha examples/alphamissense_exemplo.csv \
  --output comparativo_sift_alphamissense.csv \
  --summary resumo_comparativo.csv
```

Você receberá:

- `comparativo_sift_alphamissense.csv` (comparação linha a linha)
- `resumo_comparativo.csv` (resumo geral da concordância)

---

## 8) Onde abrir os resultados

Você pode abrir os arquivos `.csv` em:

- Excel
- Google Sheets
- LibreOffice Calc

---

## 9) Erros comuns (e como resolver)

### Erro: `command not found: sift-cdkn2a` (Linux) ou `'sift-cdkn2a' não é reconhecido` (Windows)
Você provavelmente não ativou o ambiente virtual.

Solução Linux:

```bash
source .venv/bin/activate
```

Solução Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Solução Windows (CMD):

```bat
.venv\Scripts\activate
```

### Erro: `CSV ... inválido`
O caminho do arquivo está errado ou o arquivo não existe.

Solução: confirme o nome e se está na pasta certa.

### Erro de internet
A consulta SIFT usa internet (Ensembl VEP).

Solução: verifique conexão e tente novamente.

---

## 10) Resumo ultra-rápido (cola)

### Linux (Ubuntu)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
sift-cdkn2a --input variantes_cdkn2a.csv --write-template
# (edite o CSV)
sift-cdkn2a --input variantes_cdkn2a.csv --output resultados_sift_cdkn2a.csv
compare-sift-alphamissense --sift resultados_sift_cdkn2a.csv --alpha examples/alphamissense_exemplo.csv --output comparativo_sift_alphamissense.csv --summary resumo_comparativo.csv
```

### Windows (PowerShell)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -U pip
py -m pip install -e .
sift-cdkn2a --input variantes_cdkn2a.csv --write-template
# (edite o CSV)
sift-cdkn2a --input variantes_cdkn2a.csv --output resultados_sift_cdkn2a.csv
compare-sift-alphamissense --sift resultados_sift_cdkn2a.csv --alpha examples/alphamissense_exemplo.csv --output comparativo_sift_alphamissense.csv --summary resumo_comparativo.csv
```
