# killer-sh-2 / 03

*Тема: TLS bootstrapping — Certificates best practices*

- [ ] Node cka5248-node1 has been added to the cluster using kubeadm and TLS bootstrapping.

Find the Issuer and Extended Key Usage values on cka5248-node1 for:

    1. Kubelet Client Certificate, the one used for outgoing connections to the kube-apiserver

    2. Kubelet Server Certificate, the one used for incoming connections from the kube-apiserver

Write the information into file /opt/course/3/certificate-info.txt .

        You can connect to the worker node using ssh cka5248-node1 from cka5248

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
