Проверь helm repo list и kubectl explain clusterissuer.spec.selfSigned.
<!-- level -->
helm install cert-manager jetstack/cert-manager -n cert-manager --create-namespace --set crds.enabled=true; добавь CRL в предоставленный файл и примени его.
<!-- level -->
helm install cert-manager jetstack/cert-manager -n cert-manager --create-namespace --set crds.enabled=true; добавь CRL в предоставленный файл и примени его.
