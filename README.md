# Traffic Expert System

Курсовой MVP: масштабируемая экспертная система адаптивного управления светофором.

## Возможности

- конфигурации перекрестков и потоков в JSON;
- фиксированный и экспертный контроллеры;
- продукционные правила с приоритетами и объяснениями;
- дискретная имитация транспорта;
- CSV-результаты и PNG-графики;
- интерактивная визуализация Pygame (опционально).

## Быстрый запуск

```powershell
cd <папка-проекта>
python -m pip install -r requirements.txt
$env:PYTHONPATH = "$PWD\src"
python -m traffic_expert_system.main --experiment
```

Результаты будут сохранены в `outputs/`. Для анимации добавьте `--visual`:

```powershell
python -m traffic_expert_system.main --intersection four_way --scenario morning_peak --visual
```

Управление в окне: `Space` — пауза, `R` — перезапуск, `1`, `5`, `0` — скорости x1/x5/x10, `Esc` — выход.

## Проверка

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m unittest discover -s tests -v
```
