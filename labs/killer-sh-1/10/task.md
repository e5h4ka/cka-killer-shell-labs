# killer-sh-1 / 10

*Тема: Using RBAC Authorization — Configure Service Accounts for Pods*

- [ ] Create a new ServiceAccount processor in Namespace project-hamster . Create a Role and RoleBinding, both named processor as
well. These should allow the new SA to only create Secrets and ConfigMaps in that Namespace.

A ClusterRole|Role defines a set of permissions and where it is available, in the whole cluster or just a single Namespace.

A ClusterRoleBinding|RoleBinding connects a set of permissions with an account and defines where it is applied, in the whole cluster
or just a single Namespace.

Because of this there are 4 different RBAC combinations and 3 valid ones:

    1. Role + RoleBinding (available in single Namespace, applied in single Namespace)

    2. ClusterRole + ClusterRoleBinding (available cluster-wide, applied cluster-wide)

    3. ClusterRole + RoleBinding (available cluster-wide, applied in single Namespace)

    4. Role + ClusterRoleBinding (NOT POSSIBLE: available in single Namespace, applied cluster-wide)

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
