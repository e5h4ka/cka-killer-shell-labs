# killer-sh-2 / 04

*Тема: Configure Probes*

- [ ] Do the following in Namespace default :

    • Create a Pod named ready-if-service-ready of image nginx:1-alpine

    • Configure a LivenessProbe which simply executes command true
    • Configure a ReadinessProbe which does check if the url http://service-am-i-ready:80 is reachable, you can use wget -T2
        -O- http://service-am-i-ready:80 for this

    • Start the Pod and confirm it isn't ready because of the ReadinessProbe.

Then:

    • Create a second Pod named am-i-ready of image nginx:1-alpine with label id: cross-server-ready

    • The already existing Service service-am-i-ready should now have that second Pod as endpoint

    • Now the first Pod should be in ready state, check that

It's a bit of an anti-pattern for one Pod to check another Pod for being ready using probes, hence the normally available
readinessProbe.httpGet doesn't work for absolute remote urls. Still the workaround requested in this task should show how probes
and Pod<->Service communication works.

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

До создания am-i-ready, когда первый Pod NotReady, выполни ./lab checkpoint --stage not-ready. Затем создай backend и дождись Ready.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
