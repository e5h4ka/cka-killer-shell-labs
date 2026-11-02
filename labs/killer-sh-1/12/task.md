# killer-sh-1 / 12

*Тема: Deployments — Assigning Pods to Nodes*

- [ ] Implement the following in Namespace project-tiger :

     • Create a Deployment named deploy-important with 3 replicas

     • The Deployment and its Pods should have label id=very-important

     • First container named container1 with image nginx:1-alpine

     • Second container named container2 with image registry.k8s.io/pause:3.10
    • There should only ever be one Pod of that Deployment running on one worker node, use topologyKey: kubernetes.io/
      hostname for this

       Because there are two worker nodes and the Deployment has three replicas the result should be that the third Pod won't
    be scheduled. In a way this scenario simulates the behaviour of a DaemonSet, but using a Deployment with a fixed number of
    replicas

There are two possible ways, one using podAntiAffinity and one using topologySpreadConstraint .

The idea here is that we create a "Inter-pod anti-affinity" which allows us to say a Pod should only be scheduled on a node where
another Pod of a specific label (here the same label) is not already running.

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Число replicas = число worker узлов + 1. На стандартном двухузловом playground: 2 replicas, один Ready и один Pending из-за hard placement constraint. Не меняй labels/taints узлов.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
