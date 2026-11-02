# PTOSS-2: testes unitários e TDD no wger

Branch: `ptoss2/testes-e-tdd`, criada a partir do `master`.

## Execução dos testes

```bash
uv sync   # instala as dependências na .venv

# Testes do trabalho
.venv/bin/python manage.py test \
  wger.nutrition.tests.test_ptoss2_serving_size \
  wger.nutrition.tests.test_ptoss2_sanity_checks \
  wger.nutrition.tests.test_ptoss2_search_name \
  wger.weight.tests.test_ptoss2_weight_csv \
  wger.nutrition.tests.test_ptoss2_tdd \
  wger.weight.tests.test_ptoss2_tdd \
  --settings=settings.ci

# Suíte completa
.venv/bin/python manage.py test wger --settings=settings.ci --parallel 4
```

## Cobertura

```bash
.venv/bin/coverage run --rcfile=/dev/null --branch \
  --include='wger/nutrition/models/ingredient.py,wger/nutrition/dataclasses.py,wger/nutrition/api/filtersets.py,wger/weight/helpers.py' \
  manage.py test wger.nutrition wger.weight --settings=settings.ci
.venv/bin/coverage report --rcfile=/dev/null -m
.venv/bin/coverage html --rcfile=/dev/null -d docs/ptoss2/cobertura/html
```

O ramo principal de `search_name_fulltext` só roda em Postgres. Para medi-lo, use um
settings que importe `settings.ci` e troque `DATABASES` por um Postgres com a extensão
`pg_trgm` criada no banco `template1`.

## Onde está cada coisa

- `cobertura/antes.txt` e `cobertura/depois.txt`: cobertura no SQLite antes e depois.
- `cobertura/postgres-filtersets.txt`: cobertura de `filtersets.py` no Postgres.
- `cobertura/html/`: relatório navegável.
- `evidencias/cicloN-red.txt`, `-green.txt` e `-refactor.txt`: saída real de cada etapa,
  ou a justificativa quando não houve refatoração.
- `git log --oneline master..HEAD`: um commit por etapa de cada ciclo.
- `PTOSS-2_Relatorio.docx`: relatório técnico.
