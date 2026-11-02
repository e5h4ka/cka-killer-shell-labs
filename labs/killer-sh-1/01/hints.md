Используй kubectl config get-contexts, current-context и view. Указывай учебный --kubeconfig.
<!-- level -->
Для списка имён нужен -o name. Для сертификата: config view --raw и выбор пользователя по имени; затем base64 -d.
<!-- level -->
kubectl --kubeconfig /opt/course/1/kubeconfig config get-contexts -o name > /opt/course/1/contexts
kubectl --kubeconfig /opt/course/1/kubeconfig config current-context > /opt/course/1/current-context
kubectl --kubeconfig /opt/course/1/kubeconfig config view --raw -o 'jsonpath={.users[?(@.name=="account-0027@internal")].user.client-certificate-data}' | base64 -d > /opt/course/1/cert
