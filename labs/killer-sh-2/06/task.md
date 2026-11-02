# killer-sh-2 / 06

*Тема: Troubleshooting kubeadm*

- [ ] There seems to be an issue with the kubelet on controlplane node cka1024 , it's not running.

Fix the kubelet and confirm that the node is available in Ready state.

Create a Pod called success in default Namespace of image nginx:1-alpine .

        The node has no taints and can schedule Pods without additional tolerations

The procedure on scenarios like these is to first check if the kubelet is running. If it isn't start it, check its logs and fix issues if there are
some. It could also be helpful to look at the config files of other clusters and diff/compare.

Check node status:

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Отдельная одноразовая сессия. Setup создаёт неисправный kubelet systemd drop-in. При необходимости аварийно восстанови: ./lab recover. Pod success может использовать toleration для control-plane; labels/taints менять не требуется.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
