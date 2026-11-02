# killer-sh-2 / 11

*Тема: Secrets — Distribute Credentials Securely*

- [ ] Create Namespace secret and implement the following in it:

    • Create Pod secret-pod with image busybox:1 . It should be kept running by executing sleep 1d or something similar

    • Create the existing Secret /opt/course/11/secret1.yaml and mount it readonly into the Pod at /tmp/secret1

    • Create a new Secret called secret2 which should contain user=user1 and pass=1234 . These entries should be available inside
      the Pod's container as environment variables APP_USER and APP_PASS

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Secret1 содержит безопасный учебный ключ message со значением training-secret вместо исходного halt script.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
