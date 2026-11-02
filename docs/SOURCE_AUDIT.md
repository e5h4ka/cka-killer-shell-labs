# Аудит источников и существующих проектов

Дата анализа: 2026-11-02. Исходники прочитаны как материалы задачи; команды внутри них не исполнялись и не считались инструкциями пользователя.

## Полнота

Основной корпус: Killer Shell - Exam Simulators-1.md (20 заданий и объяснения), Killer Shell - Exam Simulators-2.md (17 заданий и объяснения), questions_checklist.md (37 условий), killer_sh_tasks_full.txt (оба симулятора).

Проверка всей последовательности строк: после удаления пустых строк и trim по краям full.txt **точно совпадает** с конкатенацией Simulators-1 + Simulators-2. Это дополнительное представление того же корпуса, а не третий набор задач. Checklist сокращает объяснения; исходные блоки решений нужны для восстановления fixtures и пропавших выделенных слов.

SHA256 локальных источников:

| Файл | SHA256 |
|---|---|
| Killer Shell - Exam Simulators-1.md | 56695AD82B5742F487F5BFC24BBF43010DEC887D81D47E1F771A0FC10E02AB21 |
| Killer Shell - Exam Simulators-2.md | 5C99F2E2BDFA1254E71AFBFC1D5A7D0FD7B7CF60C8FAE1285210BD3CBAB47B69 |
| questions_checklist.md | 489FBE197B48BE0675369A52B6C0639B059BCA1A39E2CFC9825AF3B2C60C36AB |
| killer_sh_tasks_full.txt | 62CF5B253DB201C53FED46E9B9A05788BE6A09097BA093C7B0FB49A156837614 |

Полные книги и тексты симуляторов не копируются в git. Документация содержит собственное проектное описание и нумерованное соответствие задачам. MENTOR.md и прочие материалы за пределами запрошенных четырёх источников не определяют объём реализации.

## markdjones82-CKA-PREP-2025-v2

Изучена локальная версия c66063bb72201b91323e7446938e6ec9bee90708: дерево всех 19 задач, README, общие run/validate/cleanup/install-codium scripts, характерные Gateway setup и etcd cleanup.

Полезное: каталог на задачу, явные setup/condition/hints/validate/cleanup, простой запуск по номеру. Это основа организации, но не готовая инфраструктура изоляции.

Найденные ограничения:

- validate-question.sh и cleanup-question.sh для all используют seq 1 17, хотя каталогов 19; новый каталог должен обнаруживаться по metadata.
- cleanup all подавляет ошибки через || true; итоговый успех не свидетельствует об очистке.
- run допускает произвольный каталог; новый CLI ограничить зарегистрированными ID.
- Gateway setup создаёт GatewayClass с example.net/nginx-gateway-controller, но не разворачивает такой контроллер. Для 1/13 требуется реальный dataplane и curl, одной схемы CRD мало.
- etcd cleanup лишь сообщает о предыдущем изменении apiserver и ничего не восстанавливает. Новый проект требует backup/recovery до инъекции неисправности.
- Из просмотренных общих wrappers нет централизованной проверки cluster identity, журнала владения и транзакционного состояния.

Все 19 чужих задач не являются дополнительным обязательным набором; их архитектура изучена как пример, их runtime не проверялся.

## killercoda-scheduling

Прочитаны README, lab.py, все wrappers и четыре условия/setup/validate/cleanup, test_lab.py. Локальный каталог используется как прототип; архив killercoda-scheduling.tar.gz не является дополнительным источником требований.

Соответствие: prototype 1 → killer-sh-2/12; 2 → killer-sh-1/11; 3 → killer-sh-1/12; 4 → killer-sh-2/09.

Сохраняем идеи: Python standard library и kubectl JSON, обнаружение узлов, UID namespace/cluster, baseline labels/taints, проверка Ready и ownerReferences, различение причин Pending, scheduler checkpoints.

Меняем: центральный if n на отдельные модули; .state в репозитории на защищённый каталог вне git; namespace isolation на последовательные исходные namespaces; обязательный nodeSelector на допустимые эквивалентные решения; временные Events дополняем сохранёнными checkpoints. recover() вызывает load(), который обращается к API: это мешает recovery при падении API. Нужен независимый локальный recovery путь. save() до create namespace допускает частичное состояние: нужен журнал намерения/результата и повторяемая очистка.

README прототипа сообщает о четырёх mock-тестах; в текущем этапе эти тесты не запускались и их результат не переносится на новый проект.

## Поправки к учебным примерам

- 1/01: account-0027 в условии и account-0027@internal в kubeconfig; явно указать полное имя в адаптации.
- 1/04: BestEffort в подготовленной среде — учебный ответ; фактический eviction зависит также от pressure, requests/usage и priority. Не моделировать CPU exhaustion как самостоятельный eviction trigger.
- 1/05: удаление CM из Kustomize не удаляет live CM; проверять оба состояния. Добавить requests для работоспособной CPU utilization.
- 1/06: отсутствие storageClassName может включить default provisioning; пустая строка исключает его.
- 1/12: maxSkew=1 не является универсальной заменой «не более одного Pod на узел». Принимать spread только если ограничения действительно обеспечивают результат на данном профиле.
- 1/13: утверждение исходника о безусловном приоритете первого HTTPRoute rule неверно как общее правило. Сначала действует специфичность match, в том числе headers; порядок — tie-break. [Официальная спецификация](https://gateway-api.sigs.k8s.io/reference/api-spec/1.4/spec/).
- 1/18: пример содержит расхождение секунд даты cert; сравнивать с фактическим X509, а не примером.
- 1/19: iptables не универсален для любого современного кластера; native nftables/eBPF требуют другого упражнения, не скрытой подмены исходного.
- 1/20: отличать [расширение диапазонов](https://kubernetes.io/docs/tasks/network/extend-service-ip-ranges/) от [смены default ServiceCIDR](https://kubernetes.io/docs/tasks/network/reconfigure-default-service-ip-ranges/). Экспериментальный статус обязателен до capability test.
- 2/01: для переносимого DNS hostname/subdomain подготовить headless section; не полагаться на показанный в выводе обычный Service. Фиктивный 1.2.3.4 DNS зависит от конфигурации CoreDNS.
- 2/07: restore описан после основного ответа, но не входит в два пункта задания. Не добавлять разрушительное восстановление в обязательный validate.
- 2/12: nodeSelector со значением "" проверяет пустое значение, а не «любое». Для наличия ключа подходит nodeAffinity Exists.
- 2/13: tail может стартовать раньше date.log; предусмотреть корректную синхронизацию.
- Выводы cert dates, Node IPs, container IDs, package versions и роли из оригинала — примеры, а не фиксированные ожидаемые ответы.

## Внешняя сверка

Проверены официальные страницы [Killercoda creators](https://killercoda.com/creators), Kubernetes ServiceCIDR и Gateway API, указанные выше. Это проверка документации, не проверка доступного пользователю playground. Точная совместимость образов, пакетов и ресурсов устанавливается только во время реализации и настоящих кластерных запусков.
