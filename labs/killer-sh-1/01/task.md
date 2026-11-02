# killer-sh-1 / 01 — kubeconfig

Из файла /opt/course/1/kubeconfig извлеки:

1. Все имена contexts, по одному на строку, в /opt/course/1/contexts.
2. Текущий context в /opt/course/1/current-context.
3. Client certificate пользователя account-0027@internal, декодированный из base64, в /opt/course/1/cert.

Используй kubectl с явным --kubeconfig /opt/course/1/kubeconfig.
Это отдельная учебная конфигурация; подключения к её API не требуется.
Не меняй административный kubeconfig.

Проверка: bash lab validate killer-sh-1 01
Очистка: bash lab cleanup killer-sh-1 01
