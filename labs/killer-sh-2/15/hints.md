Удаление Pod меняет UID; перезапуск контейнера сохраняет UID Pod и меняет container ID.
<!-- level -->
Запиши Events с --sort-by=.metadata.creationTimestamp. Удали kube-proxy на controlplane, checkpoint --stage pod-deleted; crictl stop его нового контейнера, затем checkpoint --stage container-restarted.
<!-- level -->
Запиши Events с --sort-by=.metadata.creationTimestamp. Удали kube-proxy на controlplane, checkpoint --stage pod-deleted; crictl stop его нового контейнера, затем checkpoint --stage container-restarted.
