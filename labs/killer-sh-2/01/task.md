# killer-sh-2 / 01

*Тема: DNS for Services and Pods — Service*

- [ ] The Deployment controller in Namespace lima-control communicates with various cluster internal endpoints by using their DNS
FQDN values.

Update the ConfigMap used by the Deployment with the correct FQDN values for:

    1. DNS_1 : Service kubernetes in Namespace default

    2. DNS_2 : Headless Service department in Namespace lima-workload

    3. DNS_3 : Pod section100 in Namespace lima-workload . It should work even if the Pod IP changes

    4. DNS_4 : A Pod with IP 1.2.3.4 in Namespace kube-system

Ensure the Deployment works with the updated values.

        You can use nslookup or dig inside a Pod of the controller Deployment
For this question we need to understand how cluster internal DNS works in Kubernetes. The most common use is
SERVICE.NAMESPACE.svc.cluster.local which will resolve to the IP address of the Kubernetes Service. Note that we're asked to
specify the FQDNs here so short values like SERVICE.NAMESPACE are not possible even if they would work.

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

section — headless Service. Если CoreDNS не использует pods insecure, фиктивный 1.2.3.4 DNS может не разрешаться. В этом случае требуется совместимый свежий playground.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
