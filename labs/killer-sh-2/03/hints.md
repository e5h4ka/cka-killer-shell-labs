Открой worker /var/lib/kubelet/pki. Client cert и serving cert имеют разное назначение.
<!-- level -->
openssl x509 -in FILE -noout -issuer -ext extendedKeyUsage; файлы kubelet-client-current.pem и kubelet.crt. Запиши обе пары Issuer/EKU.
<!-- level -->
openssl x509 -in FILE -noout -issuer -ext extendedKeyUsage; файлы kubelet-client-current.pem и kubelet.crt. Запиши обе пары Issuer/EKU.
