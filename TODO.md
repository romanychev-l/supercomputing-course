# Задачи развития курса

Главная цель текущей версии — полный репозиторий существующих материалов. Перенос в LaTeX и дальнейшая переработка выполняются отдельными студенческими PR. GitHub Issues удобны для распределения работы; этот файл сохраняет обзор и работает офлайн. Исходные описания задач и критерии — в [tasks.json](docs/tasks.json).

## Уже подготовлено

- [x] Собраны теория, оригинальные PDF, все 15 практик, исходники, проверки и дополнения.
- [x] Оставлены расширенные версии первых пяти конспектов, краткие предшественники удалены, ссылки обновлены.
- [x] Добавлены инструкции участникам и агентам, шаблоны issues/PR, сборка LaTeX и GitHub Actions.
- [x] Сохранены происхождение и контрольные суммы оригиналов; бинарники и локальные настройки исключены из Git.

## Перенос исходников в LaTeX

Все темы пока имеют статус `planned`. Реестр: [materials.json](08_LaTeX/materials.json). Объём — страницы PDF, а не целевое число слайдов. Первые 8 — презентации, последние 2 — текстовые пособия. Внутри issue согласуйте диапазон 3–10 страниц; для нескольких авторов выделите подзадачи.

| ID задачи | Тема | Страниц |
| --- | --- | ---: |
| [#1](https://github.com/romanychev-l/supercomputing-course/issues/1) · `latex-01-history` | История и рейтинги | 96 |
| [#2](https://github.com/romanychev-l/supercomputing-course/issues/2) · `latex-02-architecture` | Архитектуры и память | 29 |
| [#3](https://github.com/romanychev-l/supercomputing-course/issues/3) · `latex-03-networks` | Сети и ускорение | 19 |
| [#4](https://github.com/romanychev-l/supercomputing-course/issues/4) · `latex-04-openmp` | OpenMP | 78 |
| [#5](https://github.com/romanychev-l/supercomputing-course/issues/5) · `latex-05-design` | Проектирование параллельных алгоритмов | 43 |
| [#6](https://github.com/romanychev-l/supercomputing-course/issues/6) · `latex-06-mpi-basics` | MPI: основы | 60 |
| [#7](https://github.com/romanychev-l/supercomputing-course/issues/7) · `latex-07-mpi-types` | MPI: обмены и типы | 50 |
| [#8](https://github.com/romanychev-l/supercomputing-course/issues/8) · `latex-08-mpi-topologies` | MPI: коммуникаторы и топологии | 33 |
| [#9](https://github.com/romanychev-l/supercomputing-course/issues/9) · `latex-09-openmp-handout` | Текстовое пособие OpenMP | 49 |
| [#10](https://github.com/romanychev-l/supercomputing-course/issues/10) · `latex-10-mpi-handout` | Текстовое пособие MPI | 35 |

См. [порядок переноса и приёмку](08_LaTeX/README.md). Завершённым считается содержательно и визуально проверенный редактируемый документ; пустой шаблон и набор картинок исходного PDF не закрывают задачу.

## Другие задачи для класса

- [ ] [#11](https://github.com/romanychev-l/supercomputing-course/issues/11) · `theory-audit` — Проверить формулы и ограничения моделей в теории.
- [ ] [#12](https://github.com/romanychev-l/supercomputing-course/issues/12) · `practice-portability` — Пройти все 15 практик с чистого компьютера и уточнить инструкции.
- [ ] [#13](https://github.com/romanychev-l/supercomputing-course/issues/13) · `practice-edge-cases` — Дополнить проверки практикума независимыми граничными случаями.
- [ ] [#14](https://github.com/romanychev-l/supercomputing-course/issues/14) · `intro-bsp` — Подготовить редактируемые слайды к дополнениям курса.
- [ ] [#15](https://github.com/romanychev-l/supercomputing-course/issues/15) · `onboarding-feedback` — Улучшить первый вход в Git, LaTeX и работу с агентом.
- [ ] [#16](https://github.com/romanychev-l/supercomputing-course/issues/16) · `course-coordination` — Преподавателю: согласовать лицензию, доступ и кластерные ограничения.

## Как выбрать работу

Для первого PR подойдёт одна найденная неоднозначность инструкции, один проверенный дефект или несколько слайдов. Напишите в issue, что берёте, и укажите ожидаемый объём. По большой теме используйте `Refs #N`, для полностью закрытой — `Closes #N`. Новую проблему оформляйте через issue с конкретным источником и способом проверки.

Для преподавателя: [организация работы и просмотр вклада](docs/Работа_с_группой.md). Самые полезные вклады — исправления с доказательствами, воспроизводимые проверки и содержательное ревью.
