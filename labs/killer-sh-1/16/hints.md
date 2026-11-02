CoreDNS хранит Corefile в ConfigMap kube-system/coredns. Сначала сделай backup.
<!-- level -->
Добавь custom-domain к зонам kubernetes plugin рядом с cluster.local. Перезапусти CoreDNS и проверь nslookup из Pod для обеих зон.
<!-- level -->
Добавь custom-domain к зонам kubernetes plugin рядом с cluster.local. Перезапусти CoreDNS и проверь nslookup из Pod для обеих зон.
