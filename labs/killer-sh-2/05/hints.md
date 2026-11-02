Сортируй по полям объекта, а не текстовым AGE колонкам.
<!-- level -->
find_pods.sh: kubectl get pod -A --sort-by=.metadata.creationTimestamp; find_pods_uid.sh: kubectl get pod -A --sort-by=.metadata.uid
<!-- level -->
find_pods.sh: kubectl get pod -A --sort-by=.metadata.creationTimestamp; find_pods_uid.sh: kubectl get pod -A --sort-by=.metadata.uid
