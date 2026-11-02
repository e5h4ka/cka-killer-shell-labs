# killer-sh-1 / 05

*Тема: Horizontal Pod Autoscaling — Kustomize*

- [ ] Previously the application api-gateway used some external autoscaler which should now be replaced with a HorizontalPodAutoscaler
(HPA). The application has been deployed to Namespaces api-gateway-staging and api-gateway-prod like this:

  kubectl kustomize /opt/course/5/api-gateway/staging | kubectl apply -f -
  kubectl kustomize /opt/course/5/api-gateway/prod | kubectl apply -f -

Using the Kustomize config at /opt/course/5/api-gateway do the following:

    1. Remove the ConfigMap horizontal-scaling-config completely

    2. Add HPA named api-gateway for the Deployment api-gateway with min 2 and max 4 replicas. It should scale at 50% average
      CPU utilisation

    3. In prod the HPA should have max 6 replicas
    4. Apply your changes for staging and prod so they're reflected in the cluster

Kustomize is a standalone tool to manage K8s Yaml files, but it also comes included with kubectl. The common idea is to have a base
set of K8s Yaml and then override or extend it for different overlays, like here done for staging and prod:

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Metrics API должен работать до start. Base/overlays создаются в /opt/course/5/api-gateway. Удаление ConfigMap из YAML не удаляет объект из API.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
