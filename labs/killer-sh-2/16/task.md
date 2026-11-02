# killer-sh-2 / 16

*Тема: kubectl Quick Reference — Namespaces*

- [ ] Write the names of all namespaced Kubernetes resources (like Pod, Secret, ConfigMap...) into /opt/course/16/resources.txt .

Find the project-* Namespace with the highest number of Roles defined in it and write its name and amount of Roles into /opt/
course/16/crowded-namespace.txt .

We can get a list of all resources:

  k api-resources            # shows all

  k api-resources -h         # a bit of help is always good

So we write them into the requested location:

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

В fixtures project-miami содержит 30 Roles вместо 300. Ответ вычисляй по реальному API.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
