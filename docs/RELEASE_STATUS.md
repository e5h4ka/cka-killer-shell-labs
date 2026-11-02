# Статус реализации и проверки

Дата: 2026-11-02. Реализованы маршруты start/validate/hint/cleanup для всех 37 записей.
1/20 помечена experimental: исходный диапазон нельзя универсально откатить, нужна новая сессия.
Полный цикл 1/01 подтверждён отчётом пользователя на Killercoda. Остальные 36 задач на кластере ещё не запускались.

## Ограничения первой реализации

- Зависимости устанавливаются отдельно (таблица в README). Автоматический installer, dependency digest-lock и выбор поддерживаемых minors ещё не реализованы.
- Вместо 36 однотипных wrappers используется общий engine.py и exercises.py; каталог, условия и hints остаются отдельными для каждой задачи.
- Для scripted answers проверяется структура команд; произвольные скрипты не исполняются с admin kubeconfig. Эквивалентный сложный shell syntax может быть отклонён.
- Проверки 1/04 не создают реального memory pressure. 1/09 не доказывает, что SecretList получен именно ручным curl из Pod.
- 1/06 проверяет spec/mount и Bound/availability, но пока не проверяет фактическую запись в volume. HostPath permissions/path создаёт ученик.
- 1/13 использует controller-provided Gateway address вместо фиксированного NodePort/hosts entry; внешний LB без адреса приводит к BLOCKED.
- 1/16 validator создаёт временный диагностический namespace/Pod, которые удаляются cleanup. Backup проверяется по исходному Corefile.
- 2/02 проверяет mirror Pod/NodePort HTTP, но не отдельное число EndpointSlice entries.
- 2/03 предполагает стандартные kubelet PKI paths; serving TLS bootstrap с другим расположением требует адаптации.
- 2/04 проверяет наличие remote Service URL в exec readiness; полная семантика произвольной exec-команды не анализируется.
- 2/08 ожидает стандартный kubeadm/systemd/CoreDNS профиль.
- 2/10 проверяет class/PVC/PV/Job completion, но пока не читает созданный backup-файл из volume. Retain PV/data остаются после cleanup.
- 2/14 подтверждает путь CNI config, но пока не сопоставляет имя всех plugins внутри conflist.
- 2/15 проверяет UID/containerID переходы и наличие логов; точный набор Events зависит от kubelet, TTL и агрегации.
- 2/17 ждёт успешный цикл оператора по логам; после решения может потребоваться подождать 10–15 секунд. Python API client обращается к namespaced education.killer.sh/v1 через SA token и CA.
- Recovery проверяет machine-id и state identity, но не обнаруживает все возможные сторонние изменения сохранённых host files. Использовать только отдельные учебные сессии.

Эти ограничения означают, что первая реализация ещё не является полностью принятой по всем критериям исходной матрицы. Они не скрываются за PASS.

## Что проверить пользователю

Для каждого ID: fresh session → start → validate до решения (FAIL) → решение → validate → cleanup → повторный start.
Для namespaces убедиться, что удалены только учебные ресурсы. Для системных задач проверить recover до окончания сессии.
В отчёте: ID, git SHA, doctor output, команды, PASS/FAIL/BLOCKED, cleanup/recover результат.
