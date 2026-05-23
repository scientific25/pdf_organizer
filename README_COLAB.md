# Preenchimento automático de Microsoft Forms no Google Colab

## Arquivos
- `fill_ms_forms_colab.py`
- `requirements.txt`
- `README_COLAB.md`

## Pré-requisitos
- Python 3.11+
- Arquivo `/content/planilha_preenchimento.xlsx`

## Passo a passo obrigatório (seguro)

1. **Upload da planilha** para `/content/planilha_preenchimento.xlsx`.

2. **Instalar dependências**:
```bash
!pip install -r requirements.txt
!playwright install --with-deps chromium
```

3. **Dry-run com 1 resposta (NÃO envia):**
```bash
!python fill_ms_forms_colab.py \
  --form-url "https://forms.cloud.microsoft/pages/responsepage.aspx?id=CNGXUrD61EeX80SeJ06ji9brJpCd4rRDlzGP3ZagAJ5UMVNXOTZDTFdCQVpQN0lNS0xaTlZNOThBQy4u&route=shorturl" \
  --xlsx "/content/planilha_preenchimento.xlsx" \
  --limit 1 \
  --dry-run \
  --headless \
  --screenshot-dir "/content/screenshots"
```

4. **Conferir screenshots** gerados em `/content/screenshots`.

5. **Enviar só 1 resposta de teste:**
```bash
!python fill_ms_forms_colab.py \
  --form-url "https://forms.cloud.microsoft/pages/responsepage.aspx?id=CNGXUrD61EeX80SeJ06ji9brJpCd4rRDlzGP3ZagAJ5UMVNXOTZDTFdCQVpQN0lNS0xaTlZNOThBQy4u&route=shorturl" \
  --xlsx "/content/planilha_preenchimento.xlsx" \
  --limit 1 \
  --submit \
  --headless \
  --submit-label "Enviar" \
  --screenshot-dir "/content/screenshots"
```

6. **Validar manualmente** no Microsoft Forms/Excel que a primeira resposta entrou corretamente.

7. **Enviar o restante**, começando na próxima resposta útil para evitar duplicação:
```bash
!python fill_ms_forms_colab.py \
  --form-url "https://forms.cloud.microsoft/pages/responsepage.aspx?id=CNGXUrD61EeX80SeJ06ji9brJpCd4rRDlzGP3ZagAJ5UMVNXOTZDTFdCQVpQN0lNS0xaTlZNOThBQy4u&route=shorturl" \
  --xlsx "/content/planilha_preenchimento.xlsx" \
  --start-index 2 \
  --submit \
  --headless \
  --submit-label "Enviar" \
  --screenshot-dir "/content/screenshots"
```

> `--start-index 2` = começa da **segunda resposta útil** da planilha (após a primeira já enviada no teste).

---

## Argumentos CLI
- `--form-url` (obrigatório)
- `--xlsx` (obrigatório)
- `--sheet-name` (opcional)
- `--start-row` (padrão `2`)
- `--limit` (opcional)
- `--dry-run` (opcional; padrão efetivo se `--submit` não for informado)
- `--submit` (habilita envio real)
- `--headless`
- `--screenshot-dir`
- `--delay-ms`
- `--submit-label` (padrão `Enviar`)
- `--start-index` (padrão `1`)
- `--mapping-file` (padrão `form_mapping.json`)
- `--suggested-mapping-file` (padrão `form_mapping_sugerido.json`)
- `--report-csv` (padrão `relatorio_execucao.csv`)

## Comportamentos de segurança e robustez
- Sem `--submit`, o script **nunca envia** (dry-run).
- Gera screenshots antes de envio, no final do dry-run, após envio e em erros.
- Gera relatório `relatorio_execucao.csv`.
- Gera `form_mapping_sugerido.json` para ajuste de mapeamento.
- Pode usar `form_mapping.json` para mapear manualmente cabeçalhos -> perguntas.
- Não chuta opção ambígua: se houver dúvida, marca erro e não envia.
- Detecta sinais de login/CAPTCHA e para com mensagem clara.

## Exemplo de `form_mapping.json`
```json
{
  "Nome completo": "Nome Completo",
  "Departamento": "Qual é o seu departamento?"
}
```

## Como testar rapidamente no Colab
1. Rode o comando de dry-run com `--limit 1`.
2. Verifique screenshot + `relatorio_execucao.csv` + `form_mapping_sugerido.json`.
3. Corrija mapeamento se necessário em `form_mapping.json`.
4. Rode envio de teste com `--submit --limit 1`.
5. Valide no Forms.
6. Rode lote com `--submit --start-index 2`.
