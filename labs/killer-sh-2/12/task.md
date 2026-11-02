# killer-sh-2 / 12

*Тема: Assigning Pods to Nodes — Taints and Tolerations*

- [ ] Create a Pod of image httpd:2-alpine in Namespace default .

The Pod should be named pod1 and the container should be named pod1-container .

This Pod should only be scheduled on controlplane nodes.

Do not add new labels to any nodes.

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
