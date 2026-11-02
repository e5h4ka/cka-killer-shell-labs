# Архитектура двух наборов

Проект для утверждения. Все команды ниже — будущий интерфейс, сейчас они не реализованы.

## Модель запуска

Репозиторий клонируется на controlplane свежего учебного kubeadm playground. Наборы killer-sh-1 и killer-sh-2 имеют независимую нумерацию. Один активный вопрос на кластер исключает конфликты /opt/course/N, повторных namespaces и системных изменений. Для нового вопроса предыдущий должен быть очищен; автоматическое удаление чужой работы запрещено.

Базовый профиль: Linux, Bash, Python 3 standard library, kubectl, root/sudo. Дополнительные требования задаёт вопрос: worker, SSH, crictl/containerd, kubeadm, openssl, Helm, metrics API, NetworkPolicy, Gateway controller, local-path. Не устанавливать все дополнения сразу. По [документации Killercoda](https://killercoda.com/creators) двухузловое окружение содержит controlplane и один worker, а версии окружений меняются. Конкретная версия, CNI, proxy mode и доступность скачиваний определяются при запуске, не предполагаются по имени playground.

## Интерфейс

```text
./lab start killer-sh-1 01
./lab validate killer-sh-1 01
./lab hint killer-sh-1 01 --level 1
./lab cleanup killer-sh-1 01
./lab list killer-sh-2
./lab doctor
./lab checkpoint killer-sh-2 09 --stage pending
./lab checkpoint killer-sh-2 09 --stage manual
./lab recover killer-sh-2 09
```

start проверяет возможности и конфликты, фиксирует baseline, готовит только предпосылки и печатает адаптированное условие. Повторный start активной задачи показывает состояние без сброса. Ошибка установки оставляет журнал для cleanup/recover.

validate проверяет результат, не решает задачу, не исправляет файлы и не перезапускает workloads. Допускаются заранее описанные диагностические exec/curl и краткоживущие probe-ресурсы с собственным журналом удаления. hint печатает текст уровня 1 (направление), 2 (диагностика), 3 (подробная подсказка), не исполняет его. cleanup повторяем, удаляет только ресурсы данной попытки и восстанавливает зарегистрированные изменения; чужие namespaces, CRDs и каталоги не удаляет.

Коды: 0 PASS/успешная операция; 1 FAIL по условию; 2 BLOCKED (окружение/недостающие доказательства); 3 ERROR (ошибка инструмента); 64 неверные аргументы. Нет all для start. validate all выдаёт сохранённые результаты попыток с датой/cluster identity, а не объявляет удалённые задачи проверенными в текущем состоянии.

## Предлагаемая структура

```text
lab                         # тонкая Bash-точка входа
lib/                        # Python: catalog, process, state, inventory, checks, recovery
profiles/                   # описания возможностей и закреплённых зависимостей
labs/killer-sh-1/01-.../     # 20 каталогов
labs/killer-sh-2/01-.../     # 17 каталогов
  task.json                 # метаданные и требования
  task.md                   # условие + явно перечисленные адаптации
  hints.md
  setup.bash
  validate.py
  cleanup.bash
  assets/                   # исходные незавершённые manifests/configs
tests/                      # offline fixtures и проверки ошибочных решений
docs/
PLAN.md
```

task.json: schema_version, suite, id, title, source_question, profile, capabilities, risk, owned_resources, input_files, output_files, checkpoints, timeout_seconds, recovery_strategy. Каталог обнаруживается по metadata, номера уникальны, наборы строго 01–20 и 01–17. Произвольные пути вместо ID не принимаются.

Python отвечает за JSON Kubernetes, сравнение UID, таймауты subprocess, нормализацию quantities и отчёт. Bash используется для понятных действий на узле; set -euo pipefail, LF, явная обработка ожидаемых ошибок. Нет зависимости от pip и от разбора колонок kubectl через grep. Ошибка запроса API отличается от пустого списка.

## Состояние, владение и восстановление

Состояние вне git: /var/lib/cka-killer-shell-labs/<cluster-id>/<attempt-id>, права 0700. В нём baseline, checksums резервных копий, журнал намерений и выполненных действий, UID созданных объектов, outputs и checkpoints. Перед изменением — атомарная запись намерения и резервной копии; после — запись результата. flock на общий lock препятствует параллельному start/cleanup. Фазы: preparing → active → cleaning → cleaned; отдельные failed/recovery-required, validated — запись результата, а не запрет дальнейших действий.

Identity: context, API endpoint, CA fingerprint, UID kube-system, имена/UID узлов. При смене кластера validate/cleanup отказываются изменять его. Файлы host-level дополнительно связаны с machine-id и fingerprint локального CA. Offline recover проверяет эти локальные признаки и пути, работает без API, после восстановления отдельно проверяет API и исходный cluster UID.

Namespace создаётся только если отсутствует, сохраняется UID. В default/kube-system удаляются только конкретные объекты из allowlist, с проверкой UID. Объекты решения ученика регистрируются по заранее объявленным имени/типу/namespace только если baseline подтверждает их отсутствие; чужой объект того же имени не усыновляется. В созданном лабораторией namespace cleanup удаляет весь namespace с проверкой UID.

Сохранять только изменяемые keys labels/taints/hosts и исходные файлы. Если обнаружены посторонние изменения того же поля/файла — recovery сообщает конфликт; не перезаписывает вслепую. Бэкапы static manifests хранятся вне watched manifest directory. Восстановление системных файлов идёт до API cleanup. Не удалять состояние, пока health checks и очистка не закончены. Если отсутствует API, после offline recovery повторить cleanup.

Общие дополнения: журнал владения по install/reuse; удалять только установленное данной попыткой, включая созданные ею cluster-scoped ресурсы. При чужих CRDs/Helm releases сначала проверка совместимости; при невозможности безопасно переиспользовать — BLOCKED. Никакого удаления всех CRDs или сброса CNI. Для hostPath/PV удаляются только зарегистрированные пути после проверки canonical path и принадлежности; Retain-данные сохраняются по умолчанию, полное удаление учебных данных — явный cleanup --purge-data.

## Системные профили

- 1/08: отдельная сессия; один выбранный worker выводится из кластера и получает старые совместимые kubelet/kubectl. До reset проверить наличие старых и целевых пакетов, SSH/root, CNI/runtime. Недоступные пакеты → BLOCKED до мутаций. cleanup возвращает worker к исходной версии и рабочему join, не обещает побайтовую идентичность VM.
- 2/06: сохранить действующие unit/drop-ins, внести один неправильный ExecStart в отдельный drop-in, остановить kubelet. Нельзя считать, что остановка kubelet сама останавливает уже работающий API. Проверять именно fault kubelet; success должен оказаться на controlplane (это уточняется в адаптации).
- 2/09: setup только сохраняет scheduler; останавливает его ученик. Checkpoints подтверждают отсутствие контейнера, Pending без nodeName и ручное назначение. Restore должен работать без API.
- 1/16: резервная копия CoreDNS, восстановление Corefile с rollout и DNS smoke-check.
- 1/20: отдельная экспериментальная сессия, ServiceCIDR API и совместимый allocator обязательны. Исходник смешивает расширение диапазона и смену primary CIDR. Простое добавление CIDR не гарантирует выдачу следующего IP из него. Сначала capability spike с проверкой нового IP, старого Service, DNS и API; не выдавать этот сценарий как обычный. Удалённый default ServiceCIDR с finalizer нельзя «отменить» записью старого YAML. Для этой задачи cleanup удаляет учебные ресурсы, помечает сессию требующей пересоздания; свежий playground — предусмотренный способ полного сброса. [Обоснование Kubernetes](https://kubernetes.io/docs/tasks/network/reconfigure-default-service-ip-ranges/).

## Зависимости и воспроизводимость

До реализации составить lock-описание: URL, версия/chart version, digest образа, SHA256 скачиваемых файлов, поддерживаемые Kubernetes minors. Не использовать latest или curl | bash. В условиях сохранить учебные image tags, в окружении фиксировать их разрешённые digest и проверять необходимые curl/wget/sh. Для Helm заранее предоставить repo и chart, но не выполнять требуемую учеником установку cert-manager. Для 1/13 выбрать настоящий NGINX Gateway Fabric с совместимыми CRDs; версии утвердить по результатам capability smoke-test. Сетевая недоступность и нехватка памяти — BLOCKED, не ошибка решения.

Две полные экзаменационные среды и таймер не входят в первую версию. Сессии одноразовые, результаты и отчёты пользователь сохраняет перед завершением playground.
