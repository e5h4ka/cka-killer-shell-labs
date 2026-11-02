# killer-sh-1 / 13

*Тема: Gateway API — Gateway API Documentation*

- [ ] The team from Project r500 wants to replace their Ingress (networking.k8s.io) with a Gateway Api (gateway.networking.k8s.io) solution.
The old Ingress is available at /opt/course/13/ingress.yaml .

Perform the following in Namespace project-r500 and for the already existing Gateway:

    1. Create a new HTTPRoute named traffic-director which replicates the routes from the old Ingress
    2. Extend the new HTTPRoute with path /auto which forwards to mobile backend if the User-Agent is exactly mobile and to
      desktop backend otherwise

The existing Gateway is reachable at http://r500.gateway:30080 which means your implementation should work for these
commands:

  curl r500.gateway:30080/desktop
  curl r500.gateway:30080/mobile
  curl r500.gateway:30080/auto -H "User-Agent: mobile"
  curl r500.gateway:30080/auto

Comparing for example the older Ingress (networking.k8s.io/v1) and newer HTTPRoute (gateway.networking.k8s.io/v1) CRDs then they
look quite similar in what they offer. They have a different config structure but provide the same idea of functionality.

The magic of the Gateway Api comes more to shine because of further resources (GRPCRoute, TCPRoute) and the architecture which is
designed to be more flexible and extendable. This will provide better integration into existing cloud infrastructure and providers like
GCP or AWS will be able to develop their own Gateway Api implementations.

It was mentioned that a Gateway already exists, let's verify this:

## Адаптация Killercoda

Имена cka* заменены на реальные controlplane/worker. Узлы показаны при start. Один активный вопрос на кластер. Всегда используй свой административный kubectl context.

Перед start нужен настоящий Gateway controller с Accepted GatewayClass. Setup создаёт Gateway main. Адрес смотри: kubectl -n project-r500 get gateway main. Для запросов используй Host: r500.gateway; порт и адрес зависят от контроллера, исходный NodePort 30080 не фиксируется.

Проверка: ./lab check | Подсказка: ./lab hint | Очистка: ./lab clean
