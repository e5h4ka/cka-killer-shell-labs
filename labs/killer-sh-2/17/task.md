# killer-sh-2 / 17

*Тема: Using RBAC Authorization — Kustomize*

- [ ] There is Kustomize config available at /opt/course/17/operator . It installs an operator which works with different CRDs. It has been
deployed like this:

  kubectl kustomize /opt/course/17/operator/prod | kubectl apply -f -

Perform the following changes in the Kustomize base config:

    1. The operator needs to list certain CRDs. Check the logs to find out which ones and adjust the permissions for Role operator-
      role

    2. Add a new Student resource called student4 with any name and description

Deploy your Kustomize config changes to prod.

Kustomize is a standalone tool to manage K8s Yaml files, but it also comes included with kubectl. The common idea is to have a base
set of K8s Yaml and then override or extend it for different overlays, like done here for prod:

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Operator — настоящий Python API client, ошибки Forbidden берутся из API. Входные Kustomize файлы в /opt/course/17/operator/base и prod.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
