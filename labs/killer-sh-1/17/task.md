# killer-sh-1 / 17

*Тема: Debug with crictl*

- [ ] In Namespace project-tiger create a Pod named tigers-reunite of image httpd:2-alpine with labels pod=container and
container=pod . Find out on which node the Pod is scheduled. Ssh into that node and find the containerd container belonging to that
Pod.

Using command crictl :

       1. Write the ID of the container and the info.runtimeType into /opt/course/17/pod-container.txt

       2. Write the logs of the container into /opt/course/17/pod-container.log

          You can connect to a worker node using ssh cka2556-node1 or ssh cka2556-node2 from cka2556

          In this environment crictl can be used for container management. In the real exam this could also be docker . Both
    commands can be used with the same arguments.

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
