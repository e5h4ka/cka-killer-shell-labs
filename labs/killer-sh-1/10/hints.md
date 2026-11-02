Разрешение и его привязка — разные ресурсы. Не используй wildcard.
<!-- level -->
kubectl -n project-hamster create sa processor; create role processor --verb=create --resource=secrets,configmaps; create rolebinding processor --role=processor --serviceaccount=project-hamster:processor
<!-- level -->
kubectl -n project-hamster create sa processor; create role processor --verb=create --resource=secrets,configmaps; create rolebinding processor --role=processor --serviceaccount=project-hamster:processor
