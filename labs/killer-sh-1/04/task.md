# killer-sh-1 / 04

*Тема: Pod Quality of Service Classes — Node-pressure Eviction*

- [ ] Check all available Pods in the Namespace project-c13 and find the names of those that would probably be terminated first if the
nodes run out of resources (cpu or memory).

Write the Pod names into /opt/course/4/pods-terminated-first.txt .

When available cpu or memory resources on the nodes reach their limit, Kubernetes will look for Pods that are using more resources
than they requested. These will be the first candidates for termination. If some Pods containers have no resource requests/limits set,
then by default those are considered to use more than requested. Kubernetes assigns Quality of Service classes to Pods based on the
defined resources and limits.

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
