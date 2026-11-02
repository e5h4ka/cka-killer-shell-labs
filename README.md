# cka-killer-shell-labs

Статус: разработка в ветке `dev`. Реализована первая лаборатория killer-sh-1/01 (kubeconfig); остальные 36 задач пока planned.

В текущей версии доступны каталог и диагностика окружения:

```bash
bash lab list
bash lab doctor
```

`doctor` требует доступный Kubernetes API и административный kubeconfig.
Для первой задачи: bash lab start killer-sh-1 01; затем validate, hint или cleanup с теми же suite/id. Остальные задачи возвращают BLOCKED.
Проверки на настоящем Kubernetes-кластере не выполнялись.

Архитектура и ход реализации: [PLAN.md](PLAN.md).
