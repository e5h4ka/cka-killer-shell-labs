# killer-sh-2 / 05

*Тема: Look at these Pods working together! kubectl Quick Reference*

- [ ] Create two bash script files which use kubectl sorting to:

    1. Write a command into /opt/course/5/find_pods.sh which lists all Pods in all Namespaces sorted by their AGE
      ( metadata.creationTimestamp )

    2. Write a command into /opt/course/5/find_pods_uid.sh which lists all Pods in all Namespaces sorted by field metadata.uid

A good resources here (and for many other things) is the kubectl-cheat-sheet. You can reach it fast when searching for "cheat sheet" in
the Kubernetes docs.

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
