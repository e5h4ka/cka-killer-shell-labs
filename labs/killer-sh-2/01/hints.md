Для hostname Pod нужен subdomain и соответствующий headless Service. Env из ConfigMap обновляется после rollout.
<!-- level -->
DNS_1 kubernetes.default.svc.cluster.local; DNS_2 department.lima-workload.svc.cluster.local; DNS_3 section100.section.lima-workload.svc.cluster.local; DNS_4 1-2-3-4.kube-system.pod.cluster.local.
<!-- level -->
DNS_1 kubernetes.default.svc.cluster.local; DNS_2 department.lima-workload.svc.cluster.local; DNS_3 section100.section.lima-workload.svc.cluster.local; DNS_4 1-2-3-4.kube-system.pod.cluster.local.
