Toleration разрешает control-plane, но не ограничивает размещение только им.
<!-- level -->
Добавь nodeSelector node-role.kubernetes.io/control-plane: пустая строка либо required nodeAffinity Exists; toleration NoSchedule; не меняй узлы.
<!-- level -->
Добавь nodeSelector node-role.kubernetes.io/control-plane: пустая строка либо required nodeAffinity Exists; toleration NoSchedule; не меняй узлы.
