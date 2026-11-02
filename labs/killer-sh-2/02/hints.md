Static Pod создаёт kubelet по файлу, а не Deployment. Service использует labels mirror Pod.
<!-- level -->
Manifest в /etc/kubernetes/manifests/my-static-pod.yaml. Requests 10m/20Mi. Service NodePort с port 80 и selector Pod; проверь curl на InternalIP:nodePort.
<!-- level -->
Manifest в /etc/kubernetes/manifests/my-static-pod.yaml. Requests 10m/20Mi. Service NodePort с port 80 и selector Pod; проверь curl на InternalIP:nodePort.
