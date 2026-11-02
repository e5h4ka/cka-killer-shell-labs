# killer-sh-1 / 11

*Тема: DaemonSet — Taints and Tolerations*

- [ ] Use Namespace project-tiger for the following. Create a DaemonSet named ds-important with image httpd:2-alpine and labels
id=ds-important and uuid=18426a0b-5f59-4e10-923f-c0e078e82462 . The Pods it creates should request 10 millicore cpu and 10
mebibyte memory. The Pods of that DaemonSet should run on all nodes, also controlplanes.

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
