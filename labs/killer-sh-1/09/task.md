# killer-sh-1 / 09

*Тема: Accessing the Kubernetes API from a Pod — Configure Service Accounts for Pods*

- [ ] There is ServiceAccount secret-reader in Namespace project-swan . Create a Pod of image nginx:1-alpine named api-contact
which uses this ServiceAccount.

Exec into the Pod and use curl to manually query all Secrets from the Kubernetes Api.

Write the result into file /opt/course/9/result.json .

https://kubernetes.io/docs/tasks/run-application/access-api-from-pod

You can find information in the K8s Docs by searching for "curl api" for example.

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
