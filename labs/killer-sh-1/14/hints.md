Сравни openssl x509 -enddate и kubeadm certs check-expiration.
<!-- level -->
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate; в файл expiration записывается дата без notAfter=. В скрипт: kubeadm certs renew apiserver. Не запускай его.
<!-- level -->
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate; в файл expiration записывается дата без notAfter=. В скрипт: kubeadm certs renew apiserver. Не запускай его.
