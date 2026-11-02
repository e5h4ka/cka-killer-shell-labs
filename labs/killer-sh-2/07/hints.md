etcd работает в static Pod. Для snapshot нужны endpoint и клиентские TLS credentials.
<!-- level -->
etcd --version исполни в etcd Pod. etcdctl --endpoints=https://127.0.0.1:2379 --cacert=... --cert=... --key=... snapshot save /opt/course/7/etcd-snapshot.db. Restore не нужен.
<!-- level -->
etcd --version исполни в etcd Pod. etcdctl --endpoints=https://127.0.0.1:2379 --cacert=... --cert=... --key=... snapshot save /opt/course/7/etcd-snapshot.db. Restore не нужен.
