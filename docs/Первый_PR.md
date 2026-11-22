# Первый pull request

Установите [Git](https://git-scm.com/downloads) и заведите учётную запись GitHub. Сначала откройте репозиторий курса и проверьте, что у вас есть доступ. Для приватного репозитория преподаватель присылает приглашение; доступность форка зависит от его настроек. Если Fork недоступен, попросите преподавателя дать право на рабочую ветку.

## Вариант с форком

На странице курса нажмите Fork. Ниже замените `YOUR_LOGIN` своим логином; команды выполняются в терминале. На Windows используйте Git Bash или WSL.

```sh
git clone https://github.com/YOUR_LOGIN/supercomputing-course.git
cd supercomputing-course
git remote add upstream https://github.com/romanychev-l/supercomputing-course.git
git switch -c fix/openmp-reduction
```

Отредактируйте нужные файлы, затем:

```sh
python3 tools/check_materials.py
git diff
git add путь/к/изменённому_файлу.md
git diff --staged
git commit -m "Уточнить объяснение редукции OpenMP"
git push -u origin fix/openmp-reduction
```

`путь/к/изменённому_файлу.md` — пример, замените реальным путём. GitHub предложит Compare & pull request. Проверьте base: `romanychev-l/supercomputing-course`, ветка `main`; head: ваша ветка в форке. Заполните шаблон PR. Для загрузки GitHub может запросить вход через браузер или менеджер учётных данных; пароль аккаунта вместо токена Git не принимает. Токен никому не отправляйте.

Для следующих правок в рамках того же PR делайте новые коммиты и `git push` в эту же ветку. После принятия PR следующую задачу начинайте от свежего `upstream/main`:

```sh
git fetch upstream
git switch -c docs/next-task upstream/main
```

## Вариант с доступом к общей ветке

Если преподаватель дал право записи, клонируйте основной репозиторий, создайте собственную ветку, отправьте её в origin и откройте PR в main. Не отправляйте коммиты прямо в main.

```sh
git clone https://github.com/romanychev-l/supercomputing-course.git
cd supercomputing-course
git switch -c fix/your-login-topic
```

Остальные шаги такие же. Записывайте имя автора в Git под своим аккаунтом; можно использовать GitHub noreply email из настроек, если не хотите раскрывать личный адрес.

## Перед отправкой

Прочитайте [CONTRIBUTING](../CONTRIBUTING.md), выполните подходящие проверки и изучите diff. В PR укажите issue, что изменили, почему это верно и что проверили. Не добавляйте личный отчёт по практике в общий курс, если преподаватель явно не попросил об этом; улучшения условий, проверок и примеров обсуждаются отдельно.

Официальные инструкции: [работа с форками](https://docs.github.com/en/pull-requests/working-with-forks/fork-a-repo), [PR из форка](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).
