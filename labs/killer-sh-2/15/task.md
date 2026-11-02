# killer-sh-2 / 15

*Тема: Debug with crictl — kubectl Quick Reference*

- [ ]       1. Write a kubectl command into /opt/course/15/cluster_events.sh which shows the latest events in the whole cluster,
        ordered by time ( metadata.creationTimestamp )

      2. Delete the kube-proxy Pod and write the events this caused into /opt/course/15/pod_kill.log on cka6016

      3. Manually kill the containerd container of the kube-proxy Pod and write the events into /opt/course/15/container_kill.log

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Работай с kube-proxy на controlplane. После удаления Pod и появления нового Ready Pod: ./lab checkpoint --stage pod-deleted. После ручного перезапуска его контейнера: ./lab checkpoint --stage container-restarted.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
