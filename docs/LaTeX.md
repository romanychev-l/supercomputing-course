# Установка LaTeX и сборка курса

Для `.tex` используем XeLaTeX и latexmk: они собирают кириллицу и шрифты из общего файла. Обычные Markdown-конспекты продолжают читаться без TeX. Для сборки нужен также make; команды выполняются из корня репозитория.

## macOS

Установите полный [MacTeX](https://tug.org/mactex/) по инструкции разработчиков. Он занимает заметно больше места, чем BasicTeX, зато избавляет от ручного поиска пакетов шаблона. После установки откройте новый терминал. Путь к программам TeX на Mac — `/Library/TeX/texbin`; если команды не найдены, проверьте PATH по инструкции установщика.

BasicTeX допустим, если вы готовы самостоятельно установить недостающие пакеты: beamer, fontspec, polyglossia, latexmk, dejavu, geometry, amsmath и hyperref. Не смешивайте системные менеджеры пакетов TeX; используйте способ обновления выбранного дистрибутива.

## Ubuntu/Debian и Windows/WSL

Для Linux и Ubuntu внутри WSL:

```sh
sudo apt update
sudo apt install make latexmk texlive-xetex texlive-latex-recommended texlive-latex-extra texlive-lang-cyrillic texlive-fonts-recommended fonts-dejavu-core
```

В WSL выполняйте сборку в терминале Ubuntu. Нативный Windows также может использовать [TeX Live для Windows](https://tug.org/texlive/windows.html), но команды Makefile проще выполнять в WSL. Не требуется локальный Docker.

## Проверка установки

```sh
xelatex --version
latexmk -v
make latex
```

Откройте `08_LaTeX/build/template/main.pdf` и `08_LaTeX/build/template-handout/main.pdf`. Должны отображаться русский текст, дроби и индексы. Проверьте журнал на missing glyph и переполнения. Файлы DejaVu ищутся TeX/fontspec по имени; если шрифт отсутствует в минимальной установке, установите пакет `dejavu` средствами своего TeX Live либо соответствующие системные шрифты. Не подставляйте шрифт с личным абсолютным путём.

Если latexmk не запускает XeLaTeX или пакет не найден, приложите версию ОС, версии команд и первую содержательную ошибку из журнала. Не добавляйте весь build в PR. Для нового документа см. [порядок переноса](../08_LaTeX/README.md).

На этом этапе обязательны только XeLaTeX и latexmk; редактор выбирайте любой. Исходники можно редактировать обычным текстовым редактором. Официальная документация: [TeX Live](https://tug.org/texlive/), [latexmk](https://ctan.org/pkg/latexmk), [Beamer](https://ctan.org/pkg/beamer).
