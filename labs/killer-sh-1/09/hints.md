Токен и CA находятся в /var/run/secrets/kubernetes.io/serviceaccount внутри Pod.
<!-- level -->
Создай Pod с serviceAccountName secret-reader. Внутри: curl --cacert CA -H "Authorization: Bearer TOKEN" https://kubernetes.default/api/v1/secrets. Сохрани JSON на host в /opt/course/9/result.json.
<!-- level -->
Создай Pod с serviceAccountName secret-reader. Внутри: curl --cacert CA -H "Authorization: Bearer TOKEN" https://kubernetes.default/api/v1/secrets. Сохрани JSON на host в /opt/course/9/result.json.
