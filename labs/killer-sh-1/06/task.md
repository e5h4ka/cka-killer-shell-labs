# killer-sh-1 / 06

*Тема: Persistent Volumes — Configure a Pod to use storage*

- [ ] Create a new PersistentVolume named safari-pv . It should have a capacity of 2Gi, accessMode ReadWriteOnce, hostPath /Volumes/
Data and no storageClassName defined.

Next create a new PersistentVolumeClaim in Namespace project-t230 named safari-pvc . It should request 2Gi storage,
accessMode ReadWriteOnce and should not define a storageClassName. The PVC should bound to the PV correctly.

Finally create a new Deployment safari in Namespace project-t230 which mounts that volume at /tmp/safari-data . The Pods of
that Deployment should be of image httpd:2-alpine .

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Для PV/PVC явно используй storageClassName: "". Каталог hostPath /Volumes/Data должен быть доступен на узле Pod. Данные hostPath после cleanup сохраняются.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
