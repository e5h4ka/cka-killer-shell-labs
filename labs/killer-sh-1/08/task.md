# killer-sh-1 / 08

*Тема: Upgrading kubeadm clusters — kubeadm join*

- [ ] Your coworker notified you that node cka3962-node1 is running an older Kubernetes version and is not even part of the cluster yet.

    1. Update the node's Kubernetes to the exact version of the controlplane

    2. Add the node to the cluster using kubeadm
         You can connect to the worker node using ssh cka3962-node1 from cka3962

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Отдельная свежая сессия. SSH root на worker и apt repositories с более старой и точной целевой версией kubelet/kubectl обязательны. Setup отсоединяет один worker, делает kubeadm reset и устанавливает старую доступную версию. Целевую версию показывает start. Если пакетов нет, BLOCKED до мутаций. Cleanup возвращает рабочий worker с целевой версией; при ошибке установки/сети может потребоваться свежая сессия.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
