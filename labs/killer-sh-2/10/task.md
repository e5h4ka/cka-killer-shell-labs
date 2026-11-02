# killer-sh-2 / 10

*Тема: Storage Classes — Dynamic Volume Provisioning*

- [ ] There is a backup Job which needs to be adjusted to use a PVC to store backups.

Create a StorageClass named local-backup which uses provisioner: rancher.io/local-path and volumeBindingMode:
WaitForFirstConsumer . To prevent possible data loss the StorageClass should keep a PV retained even if a bound PVC is deleted.

Adjust the Job at /opt/course/10/backup.yaml to use a PVC which request 50Mi storage and uses the new StorageClass.

Deploy your changes, verify the Job completed once and the PVC was bound to a newly created PV.

         To re-run a Job, delete it and create it again

         The abbreviation PV stands for PersistentVolume and PVC for PersistentVolumeClaim

The StorageClass should use provider rancher.io/local-path , which is of the project Local Path Provisioner. This project works with
Dynamic Volume Provisioning, but instead of creating actual volumes it uses local storage on the node where the Pod runs, by default
at path /opt/local-path-provisioner .

Cloud companies like AWS or GCP provide their own StorageClasses and providers, which if used for PVCs create PVs backed by actual
volumes in the cloud account.

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Нужен работающий rancher.io/local-path provisioner. Setup выдаёт backup.yaml с emptyDir. Данные Retain PV после cleanup намеренно сохраняются; удаляй их вручную только после проверки.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
