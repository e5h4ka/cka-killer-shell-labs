emptyDir живёт вместе с Pod и доступен нескольким контейнерам.
<!-- level -->
c1 MY_NODE_NAME через fieldRef spec.nodeName. c2 пишет date в общий volume каждую секунду. c3 ждёт файл и делает tail -f. Все три монтируют один emptyDir.
<!-- level -->
c1 MY_NODE_NAME через fieldRef spec.nodeName. c2 пишет date в общий volume каждую секунду. c3 ждёт файл и делает tail -f. Все три монтируют один emptyDir.
