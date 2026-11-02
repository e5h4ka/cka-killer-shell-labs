# killer-sh-2 / 09

*Тема: Assigning Pods to Nodes — Kubernetes Scheduler*

- [ ] Temporarily stop the kube-scheduler, this means in a way that you can start it again afterwards.

Create a single Pod named manual-schedule of image httpd:2-alpine , confirm it's created but not scheduled on any node.

Now you're the scheduler and have all its power, manually schedule that Pod on node cka5248 . Make sure it's running.

Start the kube-scheduler again and confirm it's running correctly by creating a second Pod named manual-schedule2 of image
httpd:2-alpine and check if it's running on cka5248-node1 .

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Setup сохраняет scheduler manifest, но не останавливает его. После остановки и создания Pending Pod: ./lab checkpoint --stage pending. После ручного назначения, пока scheduler ещё остановлен: ./lab checkpoint --stage manual. Восстановление: ./lab recover.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
