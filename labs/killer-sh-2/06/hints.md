systemctl status kubelet и journalctl -u kubelet помогут найти неправильный ExecStart.
<!-- level -->
Изучи systemctl cat kubelet. Удали/исправь 99-cka-labs.conf override, systemctl daemon-reload и restart kubelet; создай success. Аварийный откат: ./lab recover.
<!-- level -->
Изучи systemctl cat kubelet. Удали/исправь 99-cka-labs.conf override, systemctl daemon-reload и restart kubelet; создай success. Аварийный откат: ./lab recover.
