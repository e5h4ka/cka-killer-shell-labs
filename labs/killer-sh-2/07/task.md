# killer-sh-2 / 07

*Тема: Operating etcd clusters for Kubernetes*

- [ ] You have been tasked to perform the following etcd operations:

    1. Run etcd --version and store the output at /opt/course/7/etcd-version
    2. Make a snapshot of etcd and save it at /opt/course/7/etcd-snapshot.db

Here we simply need to execute a command, shouldn't be that hard:

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Это snapshot-only упражнение. Restore не требуется. etcdctl и etcdutl должны быть установлены заранее и совместимы с etcd. Используй явный https endpoint и сертификаты.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
