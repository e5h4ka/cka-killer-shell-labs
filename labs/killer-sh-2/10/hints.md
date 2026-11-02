WaitForFirstConsumer привязывает PV после создания потребителя. Job template immutable.
<!-- level -->
SC provisioner rancher.io/local-path, reclaimPolicy Retain. PVC 50Mi/class local-backup. В Job заменить emptyDir на persistentVolumeClaim и пересоздать Job.
<!-- level -->
SC provisioner rancher.io/local-path, reclaimPolicy Retain. PVC 50Mi/class local-backup. В Job заменить emptyDir на persistentVolumeClaim и пересоздать Job.
