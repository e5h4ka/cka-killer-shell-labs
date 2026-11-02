# killer-sh-1 / 14

*Тема: Certificate Management with kubeadm*

- [ ] Perform some tasks on cluster certificates:

     1. Check how long the kube-apiserver server certificate is valid using openssl or cfssl. Write the expiration date into /opt/
       course/14/expiration . Run the kubeadm command to list the expiration dates and confirm both methods show the same one

     2. Write the kubeadm command that would renew the kube-apiserver certificate into /opt/course/14/kubeadm-renew-certs.sh

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
