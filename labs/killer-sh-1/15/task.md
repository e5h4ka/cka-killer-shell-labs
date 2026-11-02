# killer-sh-1 / 15

*Тема: Network Policies — Declare Network Policy*

- [ ] There was a security incident where an intruder was able to access the whole cluster from a single hacked backend Pod.

To prevent this create a NetworkPolicy called np-backend in Namespace project-snake . It should allow the backend-* Pods only to:

    • Connect to db1-* Pods on port 1111

    • Connect to db2-* Pods on port 2222

Use the app Pod labels in your policy.

        All Pods in the Namespace run plain Nginx images. This allows simple connectivity tests like: k -n project-snake exec
    POD_NAME -- curl POD_IP:PORT
         For example, connections from backend-* Pods to vault-* Pods on port 3333 should no longer work

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Все targets имеют реальные слушатели, в том числе на перекрёстных запрещённых портах. Ожидается CNI с NetworkPolicy enforcement.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
