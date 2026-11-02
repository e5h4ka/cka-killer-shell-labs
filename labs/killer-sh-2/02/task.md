# killer-sh-2 / 02

*Тема: Create static Pods — Service*

- [ ] Create a Static Pod named my-static-pod in Namespace default on the controlplane node. It should be of image nginx:1-
alpine and have resource requests for 10m CPU and 20Mi memory.

Create a NodePort Service named static-pod-service which exposes that static Pod on port 80 .

        For verification check if the new Service has one Endpoint. It should also be possible to access the Pod via the cka2560
   internal IP address, like using curl 192.168.100.31:NODE_PORT

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
