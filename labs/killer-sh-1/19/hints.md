Сохрани правила до удаления Service и зафиксируй checkpoint.
<!-- level -->
iptables-save | grep project-hamster/p2-service > /opt/course/p2/iptables.txt; ./lab checkpoint --stage service; затем удали Service и дождись исчезновения правил.
<!-- level -->
iptables-save | grep project-hamster/p2-service > /opt/course/p2/iptables.txt; ./lab checkpoint --stage service; затем удали Service и дождись исчезновения правил.
