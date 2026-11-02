# killer-sh-1 / 19

*Тема: Service — kube-proxy*

- [ ] You're asked to confirm that kube-proxy is running correctly. For this perform the following in Namespace project-hamster :

    1. Create Pod p2-pod with image nginx:1-alpine

    2. Create Service p2-service which exposes the Pod internally in the cluster on port 3000->80

    3. Write the iptables rules of node cka3962 belonging the created Service p2-service into file /opt/course/p2/iptables.txt

    4. Delete the Service and confirm that the iptables rules are gone again

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Пока Service и его правила существуют, зафиксируй этап: ./lab checkpoint --stage service. Затем удали Service и запускай ./lab check. Требуется kube-proxy iptables mode.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
