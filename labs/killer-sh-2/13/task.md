# killer-sh-2 / 13

*Тема: Shared Volume Between Containers — Pod Info via Env*

- [ ] Create a Pod with multiple containers named multi-container-playground in Namespace default :

    • It should have a volume attached and mounted into each container. The volume shouldn't be persisted or shared with other
       Pods

    • Container c1 with image nginx:1-alpine should have the name of the node where its Pod is running on available as
       environment variable MY_NODE_NAME

    • Container c2 with image busybox:1 should write the output of the date command every second in the shared volume into
       file date.log . You can use while true; do date >> /your/vol/path/date.log; sleep 1; done for this.

    • Container c3 with image busybox:1 should constantly write the content of file date.log from the shared volume to stdout.
       You can use tail -f /your/vol/path/date.log for this.

         Check the logs of container c3 to confirm correct setup

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Чтобы tail не упал до появления date.log, добавь ожидание файла или touch перед tail. Допускаются разные пути mounts общего emptyDir.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
