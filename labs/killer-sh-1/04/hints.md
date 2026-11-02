Сравни status.qosClass у Pods. Никакую реальную нехватку памяти создавать не нужно.
<!-- level -->
kubectl -n project-c13 get pods -o jsonpath="{range .items[?(@.status.qosClass==\"BestEffort\")]}{.metadata.name}{\"\n\"}{end}"
<!-- level -->
kubectl -n project-c13 get pods -o jsonpath="{range .items[?(@.status.qosClass==\"BestEffort\")]}{.metadata.name}{\"\n\"}{end}"
