# killer-sh-1 / 20

*Тема: Extend Service IP Ranges — Service*

- [ ]     1. Create a Pod named check-ip in Namespace default using image httpd:2-alpine

    2. Expose it on port 80 as a ClusterIP Service named check-ip-service . Remember/output the IP of that Service

    3. Change the Service CIDR to 11.96.0.0/12 for the cluster

    4. Create a second Service named check-ip-service2 pointing to the same Pod

       The second Service should get an IP address from the new CIDR range

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Экспериментальная задача: используй отдельный одноразовый playground. После создания первого Service, до смены CIDR: ./lab checkpoint --stage old-ip. Для modern allocator нужен дополнительный ServiceCIDR svc-cidr-new с 11.96.0.0/12 и прекращение новых аллокаций из старого диапазона. Следуй официальной Kubernetes Default ServiceCIDR Reconfiguration. Cleanup удаляет учебные ресурсы, но НЕ откатывает primary CIDR; после задачи обязательно пересоздай playground. При неработающем API пересоздай сессию.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
