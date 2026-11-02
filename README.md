# cka-killer-shell-labs

Статус: разработка в ветке `dev`. Лаборатории пока не реализованы и не готовы
к прохождению в Killercoda. Все 37 записей каталога имеют статус `planned`.

В текущей версии доступны каталог и диагностика окружения:

```bash
bash lab list
bash lab doctor
```

`doctor` требует доступный Kubernetes API и административный kubeconfig.
`start`, `validate` и `cleanup` пока возвращают `BLOCKED` (код 2).
Проверки на настоящем Kubernetes-кластере не выполнялись.

Архитектура и ход реализации: [PLAN.md](PLAN.md).
