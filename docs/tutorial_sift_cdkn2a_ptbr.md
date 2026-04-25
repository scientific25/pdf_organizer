# Tutorial (pt-BR): Análise de mutações missense no SIFT para CDKN2A

Este tutorial mostra um fluxo completo para rodar o programa `sift-cdkn2a` com foco no seu projeto:

> **Análise In Silico de Mutações Missense Patogênicas no Gene CDKN2A: Uma Abordagem Comparativa entre SIFT e AlphaMissense**

## 1) Instalação do projeto

No diretório do projeto:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

## 2) Gerar um CSV modelo automaticamente

O programa já consegue criar um template pronto:

```bash
sift-cdkn2a --input variantes_cdkn2a.csv --write-template
```

Esse comando cria `variantes_cdkn2a.csv` com colunas:
- `id`
- `hgvs`
- `protein_change`
- `transcript`

## 3) Preencher suas variantes

Você pode trabalhar de 2 formas:

### Opção A (mais precisa): preencher `hgvs`
Exemplo:
```csv
id,hgvs,protein_change,transcript
v1,ENST00000380151:p.Gly101Trp,,
v2,ENST00000380151:p.Arg24Pro,,
```

### Opção B (mais rápida): preencher `protein_change`
Nesse caso o programa monta HGVS com o transcript padrão informado em `--default-transcript`.

Exemplo:
```csv
id,hgvs,protein_change,transcript
v1,,R24P,ENST00000380151
v2,,p.Asp84Asn,ENST00000380151
```

## 4) Rodar a análise

```bash
sift-cdkn2a \
  --input variantes_cdkn2a.csv \
  --output resultados_sift_cdkn2a.csv \
  --workers 12 \
  --retries 4 \
  --timeout 20
```

### Parâmetros importantes
- `--workers`: paralelismo (mais rápido para lotes grandes)
- `--retries`: tentativas extras para erros temporários de rede/servidor
- `--timeout`: limite por requisição
- `--default-transcript`: transcript usado quando só existe `protein_change`

## 5) Entender o arquivo de saída

`resultados_sift_cdkn2a.csv` traz:
- `variant_id`: identificador da variante
- `hgvs`: variante HGVS usada na consulta
- `sift_prediction`: ex. `deleterious` / `tolerated`
- `sift_score`: escore numérico do SIFT
- `consequence_terms`: termos de consequência (ex.: missense_variant)
- `transcript_id`: transcript retornado
- `biotype`: tipo do transcript
- `status`: `ok`, `no_sift`, `not_found`, `error`
- `note`: detalhe de erro (se houver)

## 6) Dicas práticas para comparar com AlphaMissense

1. Use IDs estáveis das variantes (`variant_id`) para facilitar merge entre tabelas.
2. Mantenha o mesmo transcript/referência para ambos os métodos.
3. Filtre primeiro por `status == ok` antes de comparação quantitativa.
4. Guarde os casos `no_sift` e `not_found` como análise de cobertura do método.

## 7) Exemplo mínimo fim-a-fim

```bash
# 1) criar modelo
sift-cdkn2a --input variantes_cdkn2a.csv --write-template

# 2) editar variantes no CSV

# 3) executar
sift-cdkn2a --input variantes_cdkn2a.csv --output resultados_sift_cdkn2a.csv
```

## 8) Cruzar SIFT com AlphaMissense automaticamente

Agora você também pode fazer o merge dos resultados com um CLI dedicado:

```bash
compare-sift-alphamissense \
  --sift resultados_sift_cdkn2a.csv \
  --alpha examples/alphamissense_exemplo.csv \
  --output comparativo_sift_alphamissense.csv \
  --summary resumo_comparativo.csv
```

### Formato esperado do CSV AlphaMissense
Colunas mínimas:
- `variant_id` (mesmo ID usado no arquivo do SIFT)
- `am_class` (classe textual, ex.: `pathogenic`, `likely_pathogenic`, `benign`)
- `am_score` (score numérico do AlphaMissense)

Você pode customizar os nomes com:
- `--alpha-class-column`
- `--alpha-score-column`
- `--alpha-pathogenic-labels` (ex.: `pathogenic,likely_pathogenic`)

### Saídas do comparador
- `comparativo_sift_alphamissense.csv`: tabela linha a linha com classes binárias e concordância.
- `resumo_comparativo.csv`: métricas globais (`concordance_rate`, `tp`, `tn`, `fp`, `fn`).
