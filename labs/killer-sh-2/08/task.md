# killer-sh-2 / 08

*Тема: Kubernetes Components — Create static Pods*

- [ ] Check how the controlplane components kubelet, kube-apiserver, kube-scheduler, kube-controller-manager and etcd are started/
installed on the controlplane node.

Also find out the name of the DNS application and how it's started/installed in the cluster.

Write your findings into file /opt/course/8/controlplane-components.txt . The file should be structured like:
  # /opt/course/8/controlplane-components.txt
  kubelet: [TYPE]
  kube-apiserver: [TYPE]
  kube-scheduler: [TYPE]
  kube-controller-manager: [TYPE]
  etcd: [TYPE]
  dns: [TYPE] [NAME]

Choices of [TYPE] are: not-installed , process , static-pod , pod

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
