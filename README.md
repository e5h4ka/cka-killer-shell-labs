# Killer Shell Labs

Два набора: **killer-sh-1 (20 задач)** и **killer-sh-2 (17 задач)**.
Ветка разработки: `dev`. На настоящем Killercoda подтверждён полный цикл только 1/01.
Остальные задачи — новая реализация для проверки пользователем; 1/20 экспериментальная.

## Быстрый запуск

В свежем Killercoda kubeadm playground, из терминала controlplane:

```bash
git clone --branch dev https://github.com/e5h4ka/cka-killer-shell-labs.git
cd cka-killer-shell-labs
./lab 3
```

Если репозиторий уже скачан:

```bash
git pull --ff-only origin dev
./lab 3
```

`./lab 3` начинает задачу 3 первого набора. `./lab 2/11` — задачу 11 второго.

```bash
./lab check                 # проверить текущую задачу
./lab hint                  # первая подсказка
./lab hint --level 2        # подробная подсказка
./lab clean                 # очистить перед следующей задачей
./lab                       # список всех задач
./lab doctor                # проверить подключение и версии
```

Одна активная задача на кластер. Если при обновлении осталась первая задача, сначала `./lab clean`.
Для задач с промежуточными этапами команды checkpoint указаны в условии:

```bash
./lab checkpoint --stage pending
./lab recover
```

Полные команды `bash lab start killer-sh-1 03`, `validate`, `hint`, `cleanup` также работают.

## Окружение

Linux, Python 3, Bash, root, административный kubectl, один control-plane; для некоторых задач worker и SSH root без пароля.
Работай в отдельном учебном playground. Никакой установки всего набора одновременно.

| Задачи | Дополнительные зависимости |
|---|---|
| 1/02 | Helm и доступ к charts.jetstack.io/registry; cert-manager не должен быть заранее установлен |
| 1/05, 1/07 | Работающий Metrics API (metrics-server) |
| 1/08 | Worker с SSH root; apt repositories содержат старую и точную версию controlplane; reset worker выполняется setup |
| 1/13 | Уже установлен настоящий Gateway API controller с Accepted GatewayClass и доступным Gateway address |
| 1/15 | CNI с NetworkPolicy enforcement; все необходимые listeners создаёт setup |
| 1/17, 2/09, 2/15 | containerd/crictl; для удалённого worker SSH root |
| 1/19 | kube-proxy именно iptables mode, iptables-save |
| 2/07 | Совместимые с etcd утилиты etcdctl и etcdutl на controlplane |
| 2/10 | Уже установлен rancher.io/local-path provisioner |
| 2/17 | Доступен образ python:3.12-alpine |

Зависимости не устанавливаются автоматически. Если они отсутствуют, `start` выдаёт BLOCKED с причиной.
Установка Helm/Gateway/metrics/local-path зависит от текущей версии playground и выполняется отдельно.
Образы учебных workloads используют tags исходных задач; digest-lock и проверка всех версионных комбинаций ещё не выполнены.

## Системные задачи и данные

1/08, 2/06, 2/09 и 2/15 выполняй в отдельных сессиях. 2/06 намеренно ломает kubelet override;
2/09 останавливает scheduler сам ученик. `./lab recover` восстанавливает сохранённые host files даже без API.
Worker rejoin в 1/08 требует работающего API; после сетевой/пакетной ошибки может понадобиться новая сессия.

**1/20 — отдельная экспериментальная сессия.** Автоматического rollback primary ServiceCIDR нет.
После cleanup пересоздай playground. Если API недоступен — сразу пересоздай playground.

Ответы остальных задач при cleanup архивируются в `/var/lib/cka-killer-shell-labs/answers-<attempt>`.
Данные hostPath и Retain PV намеренно сохраняются. Не публикуй snapshots, токены и SecretList.

## Проверки

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q lib tests
```

Это offline-проверки с fixtures/mocks. Они не заменяют проверку задач на настоящем Kubernetes.
`FAIL` означает несоответствие ответа, `BLOCKED` — препятствие окружения/недостающий этап.
Валидаторы файлов shell проверяют структуру команд и не исполняют ответы ученика как root.
Финальное состояние не доказывает историю ручных команд; checkpoints проверяют только предусмотренные этапы.

Архитектура и статусы: [PLAN.md](PLAN.md), [матрица задач](docs/TASK_MATRIX.md), [ограничения проверки](docs/RELEASE_STATUS.md).
