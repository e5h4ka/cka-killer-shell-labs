# killer-sh-1 / 02

*Тема: Helm Docs — Custom Resources*

- [ ] Install cert-manager using Helm in Namespace cert-manager . Then configure and create the ClusterIssuer CRD:

    1. Create Namespace cert-manager

    2. Install Helm chart jetstack/cert-manager (with crds.enabled=true ) into the new Namespace. The Helm Release should be
       called cert-manager

    3. Update the ClusterIssuer resource in /opt/course/2/cluster-issuer.yaml to include crlDistributionPoints:
       ["http://example.com/crl"] under spec.selfSigned

    4. Create the ClusterIssuer resource from /opt/course/2/cluster-issuer.yaml

        It is not required for cert-manager to issue real certificates. Installing the Helm Chart and the ClusterIssuer resource as
    requested is enough
Helm Chart: Kubernetes YAML template-files combined into a single package, Values allow customisation

Helm Release: Installed instance of a Chart

Helm Values: Allow to customise the YAML template-files in a Chart when creating a Release

Operator: Pod that communicates with the Kubernetes API and might work with CRDs

CRD: Custom Resources are extensions of the Kubernetes API

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Используй официальный Helm repo https://charts.jetstack.io. Версию chart выбирай совместимую с текущим Kubernetes. После начала задачи создай cert-manager namespace, release cert-manager и ClusterIssuer course-issuer.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
