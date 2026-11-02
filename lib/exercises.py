"""Fixtures and semantic assertions for sequential kubeadm practice exercises."""
import base64
from datetime import datetime
from decimal import Decimal
import json
import ipaddress
from pathlib import Path
import re
import shlex
import time

from core import Blocked, kubectl, owned, ready, run

NGINX = 'nginx:1-alpine'
HTTPD = 'httpd:2-alpine'
BUSYBOX = 'busybox:1'


def key(s):
    return int(s.task['suite'][-1]), int(s.task['id'])


def obj(kind, name, ns=None, **fields):
    versions = {'Deployment': 'apps/v1', 'StatefulSet': 'apps/v1', 'DaemonSet': 'apps/v1',
        'Role': 'rbac.authorization.k8s.io/v1', 'RoleBinding': 'rbac.authorization.k8s.io/v1',
        'ClusterRole': 'rbac.authorization.k8s.io/v1', 'ClusterRoleBinding': 'rbac.authorization.k8s.io/v1',
        'CustomResourceDefinition': 'apiextensions.k8s.io/v1'}
    result = dict(apiVersion=versions.get(kind, 'v1'), kind=kind, metadata={'name': name}, **fields)
    if ns:
        result['metadata']['namespace'] = ns
    return result


def pod(name, ns, image=NGINX, labels=None, **spec):
    result = obj('Pod', name, ns, spec={'containers': [{'name': name, 'image': image}], **spec})
    result['metadata']['labels'] = labels or {'app': name}
    return result


def deployment(name, ns, image=NGINX, replicas=1):
    p = pod(name, ns, image)
    return obj('Deployment', name, ns, spec={'replicas': replicas,
        'selector': {'matchLabels': {'app': name}},
        'template': {'metadata': {'labels': {'app': name}}, 'spec': p['spec']}})


def service(name, ns, label, port=80, target=80, headless=False):
    spec = {'selector': label, 'ports': [{'port': port, 'targetPort': target}]}
    if headless:
        spec['clusterIP'] = 'None'
    return obj('Service', name, ns, spec=spec)


def preflight(s):
    k = key(s)
    if k in [(1, 8), (1, 12), (2, 3), (2, 9), (2, 12)] and not s.data['workers']:
        raise Blocked('This task requires a worker node.')
    if k in [(1, 12), (2, 9), (2, 12)]:
        cp_taints = s.data['nodes'][s.data['cp']]['taints']
        if not any(t['key'] == 'node-role.kubernetes.io/control-plane' and t['effect'] == 'NoSchedule' for t in cp_taints):
            raise Blocked('Requires the standard control-plane NoSchedule taint; use a fresh playground.')
        if any(s.data['nodes'][w]['taints'] for w in s.data['workers']):
            raise Blocked('Workers must have no custom taints for this exercise.')
    if k in [(1, 7), (1, 5)]:
        kubectl('get', '--raw', '/apis/metrics.k8s.io/v1beta1/nodes')
    if k == (1, 2):
        run('helm', 'version', '--short')
        for crd in s.items('crd'):
            if crd['metadata']['name'].endswith('cert-manager.io'):
                raise Blocked('cert-manager CRDs already installed; use a fresh session.')
    if k in [(1, 17), (2, 9), (2, 15)]:
        run('crictl', 'ps', '-o', 'json')
    if k == (1, 19):
        config = s.get('configmap', 'kube-proxy', 'kube-system')
        text = config.get('data', {}).get('config.conf', '')
        if not re.search(r'mode:\s*[\"\x27]?iptables', text):
            raise Blocked('Requires explicit kube-proxy iptables mode. Do not change proxy mode for this lab.')
        run('iptables-save')
    if k == (1, 13):
        classes = s.items('gatewayclasses.gateway.networking.k8s.io')
        if not any(any(c.get('type') == 'Accepted' and c.get('status') == 'True'
                       for c in x.get('status', {}).get('conditions', [])) for x in classes):
            raise Blocked('Install a real Gateway API controller first; no Accepted GatewayClass found.')
    if k == (2, 10):
        if not any(x.get('provisioner') == 'rancher.io/local-path' for x in s.items('storageclass')):
            raise Blocked('Install rancher local-path provisioner first.')
    if k in [(1, 14), (1, 18), (2, 7), (2, 8), (2, 14)]:
        if not Path('/etc/kubernetes/manifests/kube-apiserver.yaml').is_file():
            raise Blocked('Requires kubeadm static manifests on this host.')
    if k == (2, 7):
        run('etcdctl', 'version')
        run('etcdutl', 'version')
    if k == (1, 8):
        node = s.data['workers'][0]
        workloads = [p for p in s.items('pods', 'default') if p.get('spec', {}).get('nodeName') == node]
        if workloads:
            raise Blocked('Use a fresh playground: worker has default namespace workloads.')
        target = s.get('node', s.data['cp'])['status']['nodeInfo']['kubeletVersion'].lstrip('v')
        versions = remote(s, node, 'apt-cache', 'madison', 'kubelet')
        candidates = [line.split('|')[1].strip() for line in versions.splitlines() if '|' in line]
        def semver(v):
            return tuple(int(n) for n in re.match(r'(\d+)\.(\d+)\.(\d+)', v).groups())
        targets = [v for v in candidates if v.split('-')[0] == target]
        older = [v for v in candidates if semver(v) < semver(target)]
        if not targets or not older:
            raise Blocked('Worker apt repositories need both an older kubelet version and the exact control-plane version. No nodes changed.')
        old = max(older, key=semver)
        current = targets[0]
        for package, version in [('kubectl', old), ('kubectl', current), ('kubeadm', current)]:
            if version not in remote(s, node, 'apt-cache', 'madison', package):
                raise Blocked(f'Worker repository lacks {package}={version}. No nodes changed.')
        if remote(s, node, 'id', '-u').strip() != '0':
            raise Blocked('Worker SSH must provide root access for package installation/reset.')
        s.data['join_worker'] = node
        s.data['join_target'] = current
        s.data['join_old'] = old
    if k == (1, 20):
        ranges = s.items('servicecidrs.networking.k8s.io')
        if not any(x['metadata']['name'] == 'kubernetes' for x in ranges):
            raise Blocked('Requires the default kubernetes ServiceCIDR and the modern allocator.')
        target = ipaddress.ip_network('11.96.0.0/12')
        existing = [ipaddress.ip_network(c) for x in ranges for c in x['spec']['cidrs']]
        routes = json.loads(run('ip', '-j', 'route'))
        existing += [ipaddress.ip_network(r['dst'], strict=False) for r in routes if r.get('dst', 'default') != 'default']
        if any(n.version == 4 and target.overlaps(n) for n in existing):
            raise Blocked('New range overlaps an existing ServiceCIDR or host route.')
        if any(x['metadata'].get('deletionTimestamp') for x in ranges):
            raise Blocked('Use a fresh playground: ServiceCIDR deletion already in progress.')


def prepare(s):
    k = key(s)
    namespaces = {
        (1, 2): [], (1, 3): ['project-h800'], (1, 4): ['project-c13'],
        (1, 5): ['api-gateway-staging', 'api-gateway-prod'], (1, 6): ['project-t230'],
        (1, 9): ['project-swan'], (1, 10): ['project-hamster'],
        (1, 11): ['project-tiger'], (1, 12): ['project-tiger'], (1, 13): ['project-r500'],
        (1, 15): ['project-snake'], (1, 17): ['project-tiger'], (1, 19): ['project-hamster'],
        (2, 1): ['lima-control', 'lima-workload'], (2, 10): ['project-bern'],
        (2, 11): [], (2, 16): ['project-jinan', 'project-miami', 'project-seoul'],
        (2, 17): ['operator-prod']}
    for ns in namespaces.get(k, []):
        s.namespace(ns)
    if k == (1, 2):
        s.target('namespace', 'cert-manager')
        s.target('clusterissuer.cert-manager.io', 'course-issuer') if s.get('crd', 'clusterissuers.cert-manager.io') else None
        s.file('cluster-issuer.yaml', 'apiVersion: cert-manager.io/v1\nkind: ClusterIssuer\nmetadata:\n  name: course-issuer\nspec:\n  selfSigned: {}\n')
        run('helm', 'repo', 'add', 'jetstack', 'https://charts.jetstack.io', '--force-update')
        run('helm', 'repo', 'update', 'jetstack', timeout=120)
    elif k == (1, 3):
        ns = 'project-h800'
        s.put(service('o3db', ns, {'app': 'o3db'}, headless=True))
        d = deployment('o3db', ns, replicas=2)
        d['kind'] = 'StatefulSet'
        d['spec']['serviceName'] = 'o3db'
        s.put(d)
    elif k == (1, 4):
        for n, resources in [('api', {'requests': {'cpu': '20m', 'memory': '10Mi'}}),
                             ('heavy', {}), ('fixed', {'requests': {'cpu': '20m', 'memory': '32Mi'},
                                                        'limits': {'cpu': '20m', 'memory': '32Mi'}})]:
            p = pod(n, 'project-c13')
            p['spec']['containers'][0]['resources'] = resources
            s.put(p)
    elif k == (1, 5):
        prepare_hpa(s)
    elif k == (1, 6):
        s.target('pv', 'safari-pv')
    elif k == (1, 8):
        node = s.data['join_worker']
        # All changes are journaled before drain/reset. Only the selected worker is touched.
        kubectl('drain', node, '--ignore-daemonsets', '--delete-emptydir-data', '--timeout=90s')
        s.data['worker_detached'] = True
        s.save()
        remote(s, node, 'kubeadm', 'reset', '-f')
        kubectl('delete', 'node', node)
        remote(s, node, 'apt-get', 'install', '-y', '--allow-downgrades', '--allow-change-held-packages',
            'kubelet=' + s.data['join_old'], 'kubectl=' + s.data['join_old'], 'kubeadm=' + s.data['join_target'])
        print('Worker:', node, '| installed older version:', s.data['join_old'], '| target:', s.data['join_target'])
    elif k == (1, 9):
        ns = 'project-swan'
        s.put(obj('ServiceAccount', 'secret-reader', ns))
        s.put(obj('Secret', 'read-me', ns, stringData={'token': 'training-only'}))
        s.put(obj('ClusterRole', 'ks-secret-reader', rules=[{'apiGroups': [''], 'resources': ['secrets'], 'verbs': ['list']}]))
        s.put(obj('ClusterRoleBinding', 'ks-secret-reader', roleRef={'apiGroup': 'rbac.authorization.k8s.io',
            'kind': 'ClusterRole', 'name': 'ks-secret-reader'}, subjects=[{'kind': 'ServiceAccount', 'name': 'secret-reader', 'namespace': ns}]))
    elif k == (1, 13):
        prepare_gateway(s)
    elif k == (1, 15):
        for name, ports in [('backend', [80]), ('db1', [1111, 2222]), ('db2', [1111, 2222]), ('vault', [3333])]:
            conf = 'events {}\nhttp {\n' + '\n'.join(f'server {{ listen {port}; location / {{ return 200 "{name}\\n"; }} }}' for port in ports) + '\n}'
            ns = 'project-snake'
            s.put(obj('ConfigMap', name, ns, data={'nginx.conf': conf}))
            p = pod(name + '-0', ns, labels={'app': name})
            p['spec']['volumes'] = [{'name': 'config', 'configMap': {'name': name}}]
            p['spec']['containers'][0]['volumeMounts'] = [{'name': 'config', 'mountPath': '/etc/nginx/nginx.conf', 'subPath': 'nginx.conf'}]
            s.put(p)
    elif k == (1, 16):
        s.data['coredns'] = s.get('configmap', 'coredns', 'kube-system')['data']
        s.save()
    elif k == (1, 20):
        for kind, name in [('pod', 'check-ip'), ('service', 'check-ip-service'), ('service', 'check-ip-service2')]:
            s.target(kind, name, 'default')
        s.target('servicecidr', 'svc-cidr-new')
        s.data['cidr_original'] = s.items('servicecidrs.networking.k8s.io')
        s.save()
        print('EXPERIMENTAL: use a separate session. Cleanup requires a fresh playground afterwards.')
    elif k == (2, 1):
        prepare_dns(s)
    elif k == (2, 2):
        manifest = Path('/etc/kubernetes/manifests/my-static-pod.yaml')
        if manifest.exists():
            raise Blocked('Static pod manifest already exists.')
        s.snapshot_file(manifest)
        s.target('service', 'static-pod-service', 'default')
    elif k == (2, 4):
        for name in ['ready-if-service-ready', 'am-i-ready']:
            s.target('pod', name, 'default')
        s.put(service('service-am-i-ready', 'default', {'id': 'cross-server-ready'}))
    elif k == (2, 5):
        s.namespace('ks-sort-fixtures')
        s.put(deployment('sort-fixture', 'ks-sort-fixtures', replicas=3))
    elif k == (2, 6):
        path = Path('/etc/systemd/system/kubelet.service.d/99-cka-labs.conf')
        s.snapshot_file(path)
        s.target('pod', 'success', 'default')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('[Service]\nExecStart=\nExecStart=/nonexistent/cka-labs-kubelet\n')
        run('systemctl', 'daemon-reload')
        try:
            run('systemctl', 'restart', 'kubelet')
        except Blocked:
            # ExecStart intentionally points to a missing binary in this exercise.
            pass
    elif k == (2, 9):
        s.snapshot_file('/etc/kubernetes/manifests/kube-scheduler.yaml')
        for name in ['manual-schedule', 'manual-schedule2']:
            s.target('pod', name, 'default')
    elif k == (2, 10):
        s.target('storageclass', 'local-backup')
        job = obj('Job', 'backup', 'project-bern', spec={'backoffLimit': 0, 'template': {'spec': {
            'restartPolicy': 'Never', 'volumes': [{'name': 'backup', 'emptyDir': {}}], 'containers': [{
                'name': 'bash', 'image': 'bash:5', 'command': ['bash', '-c', 'touch /backup/backup-$(date +%s).tar.gz; sleep 5'],
                'volumeMounts': [{'name': 'backup', 'mountPath': '/backup'}]}]}}})
        job['apiVersion'] = 'batch/v1'
        s.file('backup.yaml', json.dumps(job, indent=2))
    elif k == (2, 11):
        s.target('namespace', 'secret')
        s.file('secret1.yaml', json.dumps(obj('Secret', 'secret1', stringData={'message': 'training-secret'}), indent=2))
    elif k == (2, 12):
        s.target('pod', 'pod1', 'default')
    elif k == (2, 13):
        s.target('pod', 'multi-container-playground', 'default')
    elif k == (2, 15):
        p = next((p for p in s.items('pods', 'kube-system') if p['metadata'].get('labels', {}).get('k8s-app') == 'kube-proxy'
            and p['spec']['nodeName'] == s.data['cp']), None)
        if not p:
            raise Blocked('No kube-proxy Pod on control-plane.')
        s.data['proxy_initial'] = p['metadata']['uid']
        s.save()
    elif k == (2, 16):
        for ns, count in [('project-miami', 30), ('project-seoul', 10)]:
            for i in range(count):
                s.put(obj('Role', f'role-{i}', ns, rules=[]))
    elif k == (2, 17):
        prepare_operator(s)


def qty(value):
    value = str(value)
    suffixes = {'Ki': 1024, 'Mi': 1024**2, 'Gi': 1024**3, 'm': Decimal('.001')}
    for suffix, factor in suffixes.items():
        if value.endswith(suffix):
            return Decimal(value[:-len(suffix)]) * factor
    return Decimal(value)


def containers(p):
    return p.get('spec', {}).get('containers', [])


def validate(s):
    k = key(s)
    check = s.check
    if k == (1, 2):
        releases = json.loads(run('helm', 'list', '-n', 'cert-manager', '-o', 'json'))
        check('cert-manager release deployed', any(x['name'] == 'cert-manager' and x['status'] == 'deployed' for x in releases))
        values = json.loads(run('helm', 'get', 'values', 'cert-manager', '-n', 'cert-manager', '-o', 'json'))
        check('CRDs enabled', values.get('crds', {}).get('enabled') is True)
        issuer = s.get('clusterissuer', 'course-issuer')
        check('ClusterIssuer selfSigned CRL', issuer.get('spec', {}).get('selfSigned', {}).get('crlDistributionPoints') == ['http://example.com/crl'])
    elif k == (1, 3):
        sts = s.get('statefulset', 'o3db', 'project-h800')
        pods = [p for p in s.items('pods', 'project-h800') if owned(p, sts.get('metadata', {}).get('uid'))]
        check('One desired and Ready StatefulSet replica', sts.get('spec', {}).get('replicas') == 1 and len(pods) == 1 and ready(pods[0]))
    elif k == (1, 4):
        expected = {p['metadata']['name'] for p in s.items('pods', 'project-c13') if p.get('status', {}).get('qosClass') == 'BestEffort'}
        check('BestEffort Pod names', bool(expected) and set(s.text('pods-terminated-first.txt').splitlines()) == expected)
    elif k == (1, 5):
        validate_hpa(s)
    elif k == (1, 6):
        ns = 'project-t230'
        pv = s.get('pv', 'safari-pv')
        pvc = s.get('pvc', 'safari-pvc', ns)
        check('PV capacity/access/path/class', qty(pv.get('spec', {}).get('capacity', {}).get('storage', 0)) == qty('2Gi')
            and pv.get('spec', {}).get('accessModes') == ['ReadWriteOnce'] and pv.get('spec', {}).get('hostPath', {}).get('path') == '/Volumes/Data'
            and pv.get('spec', {}).get('storageClassName', '') == '')
        check('PVC bound to safari-pv', pvc.get('status', {}).get('phase') == 'Bound' and pvc.get('spec', {}).get('volumeName') == 'safari-pv'
            and qty(pvc.get('spec', {}).get('resources', {}).get('requests', {}).get('storage', 0)) == qty('2Gi'))
        dep = s.get('deployment', 'safari', ns)
        template = dep.get('spec', {}).get('template', {})
        vols = {v['name'] for v in template.get('spec', {}).get('volumes', []) if v.get('persistentVolumeClaim', {}).get('claimName') == 'safari-pvc'}
        check('Deployment volume mount and image', any(c['image'] == HTTPD and any(v['name'] in vols and v['mountPath'] == '/tmp/safari-data'
            for v in c.get('volumeMounts', [])) for c in containers(template)))
        check('Deployment available', dep.get('status', {}).get('availableReplicas', 0) >= 1)
    elif k in [(1, 7), (2, 5)]:
        expected = [('node.sh', ['top', 'node']), ('pod.sh', ['top', 'pod', '--containers'])] if k == (1, 7) else [
            ('find_pods.sh', ['get', 'pod', '-A', '--sort-by=.metadata.creationTimestamp']),
            ('find_pods_uid.sh', ['get', 'pod', '-A', '--sort-by=.metadata.uid'])]
        for name, tokens in expected:
            script_check(s, name, tokens)
    elif k == (1, 8):
        node = s.data['join_worker']
        target = s.data['join_target'].split('-')[0]
        n = s.get('node', node)
        check('Worker joined and Ready at target version', node_ready(s, node) and n.get('status', {}).get('nodeInfo', {}).get('kubeletVersion') == 'v' + target)
        check('kubectl updated', json.loads(remote(s, node, 'kubectl', 'version', '--client', '-o', 'json'))['clientVersion']['gitVersion'] == 'v' + target)
        check('kubeadm updated', remote(s, node, 'kubeadm', 'version', '-o', 'short').strip() == 'v' + target)
    elif k == (1, 9):
        p = s.pod('api-contact', 'project-swan')
        check('Pod Ready with secret-reader', ready(p) and p.get('spec', {}).get('serviceAccountName') == 'secret-reader'
            and any(c['image'] == NGINX for c in containers(p)))
        result = s.jsonfile('result.json')
        check('SecretList contains training secret', result.get('kind') == 'SecretList' and any(x.get('metadata', {}).get('name') == 'read-me'
            and x['metadata'].get('namespace') == 'project-swan' for x in result.get('items', [])))
    elif k == (1, 10):
        ns = 'project-hamster'
        role = s.get('role', 'processor', ns)
        binding = s.get('rolebinding', 'processor', ns)
        rules = role.get('rules', [])
        permissions = {(g, r, v) for rule in rules for g in rule.get('apiGroups', []) for r in rule.get('resources', []) for v in rule.get('verbs', [])}
        check('Exactly create Secrets and ConfigMaps', permissions == {('', r, 'create') for r in ['secrets', 'configmaps']})
        check('RoleBinding uses processor SA/Role', binding.get('roleRef', {}).get('kind') == 'Role' and binding.get('roleRef', {}).get('name') == 'processor'
            and binding.get('subjects') == [{'kind': 'ServiceAccount', 'name': 'processor', 'namespace': ns}]
            and bool(s.get('serviceaccount', 'processor', ns)))
        for verb, resource, allowed in [('create', 'secrets', True), ('create', 'configmaps', True), ('get', 'secrets', False), ('delete', 'configmaps', False), ('create', 'pods', False)]:
            review = {'apiVersion': 'authorization.k8s.io/v1', 'kind': 'SubjectAccessReview', 'spec': {
                'user': f'system:serviceaccount:{ns}:processor',
                'resourceAttributes': {'namespace': ns, 'verb': verb, 'resource': resource, 'group': ''}}}
            answer = json.loads(kubectl('create', '-f', '-', '-o', 'json', stdin=json.dumps(review)))
            check(f'Authorization {verb} {resource}', answer.get('status', {}).get('allowed', False) == allowed)
    elif k == (1, 11):
        validate_daemonset(s)
    elif k == (1, 12):
        validate_placement(s)
    elif k == (1, 13):
        validate_gateway(s)
    elif k == (1, 14):
        expected = run('openssl', 'x509', '-in', '/etc/kubernetes/pki/apiserver.crt', '-noout', '-enddate').strip().split('=', 1)[1]
        check('Certificate expiry', s.text('expiration') == expected)
        command = '\n'.join(line for line in s.text('kubeadm-renew-certs.sh').splitlines() if not line.lstrip().startswith('#'))
        check('Renewal command (not executed)', ' '.join(shlex.split(command)) == 'kubeadm certs renew apiserver')
    elif k == (1, 15):
        validate_policy(s)
    elif k == (1, 16):
        backup = s.text('coredns_backup.yaml')
        check('Original CoreDNS backup', bool(backup) and s.data['coredns']['Corefile'].strip() in backup)
        dns_check(s, 'kubernetes.default.svc.cluster.local')
        dns_check(s, 'kubernetes.default.svc.custom-domain')
    elif k == (1, 17):
        p = s.pod('tigers-reunite', 'project-tiger')
        check('Pod labels/image/Ready', ready(p) and p.get('metadata', {}).get('labels', {}).get('pod') == 'container'
            and p['metadata']['labels'].get('container') == 'pod' and any(c['image'] == HTTPD for c in containers(p)))
        if ready(p):
            cid = p['status']['containerStatuses'][0]['containerID'].split('://')[-1]
            node = p['spec']['nodeName']
            inspection = json.loads(remote(s, node, 'crictl', 'inspect', cid))
            runtime = inspection.get('info', {}).get('runtimeType', '')
            check('Container ID and runtimeType', cid.startswith(s.text('pod-container.txt').split()[0]) if s.text('pod-container.txt') else False)
            check('runtimeType present', bool(runtime) and runtime in s.text('pod-container.txt'))
            logs = remote(s, node, 'crictl', 'logs', cid).strip()
            check('Runtime logs', bool(logs) and s.text('pod-container.log') == logs)
    elif k == (1, 18):
        text = Path('/etc/kubernetes/manifests/etcd.yaml').read_text()
        cert = flag(text, 'cert-file')
        answer = s.text('etcd-info.txt')
        check('etcd key path', flag(text, 'key-file') in answer)
        expiry = run('openssl', 'x509', '-in', cert, '-noout', '-enddate').strip().split('=', 1)[1]
        check('etcd expiration', expiry in answer)
        check('client certificate auth', flag(text, 'client-cert-auth') == 'true' and re.search(r'yes|true|enabled', answer, re.I))
    elif k == (1, 19):
        evidence = s.data['checkpoints'].get('service', {})
        check('Service rules checkpoint recorded', bool(evidence))
        check('Saved rules', bool(s.text('iptables.txt')) and 'project-hamster/p2-service' in s.text('iptables.txt'))
        check('Service removed', not s.get('service', 'p2-service', 'project-hamster'))
        check('Rules removed', 'project-hamster/p2-service' not in run('iptables-save'))
    elif k == (1, 20):
        first = s.get('service', 'check-ip-service', 'default')
        second = s.get('service', 'check-ip-service2', 'default')
        before = s.data['checkpoints'].get('old-ip', {})
        check('Original Service IP checkpoint', bool(before) and first.get('spec', {}).get('clusterIP') == before.get('ip'))
        address = second.get('spec', {}).get('clusterIP')
        check('New Service IP in 11.96.0.0/12', bool(address) and ipaddress.ip_address(address) in ipaddress.ip_network('11.96.0.0/12'))
        for svc in [first, second]:
            ip = svc.get('spec', {}).get('clusterIP')
            if ip:
                check('HTTP ' + ip, bool(run('curl', '-fsS', '--max-time', '5', f'http://{ip}')))
        check('apiserver range', flag(Path('/etc/kubernetes/manifests/kube-apiserver.yaml').read_text(), 'service-cluster-ip-range') == '11.96.0.0/12')
    elif k == (2, 1):
        validate_dns(s)
    elif k == (2, 2):
        ps = [p for p in s.items('pods', 'default') if p['metadata']['name'].startswith('my-static-pod-')]
        p = ps[0] if len(ps) == 1 else {}
        check('Static Pod on control-plane Ready', ready(p) and p.get('spec', {}).get('nodeName') == s.data['cp']
            and 'kubernetes.io/config.mirror' in p.get('metadata', {}).get('annotations', {}))
        cs = containers(p)
        check('Static Pod image/requests', len(cs) == 1 and cs[0]['image'] == NGINX and quantities(cs[0], '10m', '20Mi'))
        svc = s.get('service', 'static-pod-service', 'default')
        check('NodePort Service', svc.get('spec', {}).get('type') == 'NodePort' and svc['spec']['ports'][0]['port'] == 80)
        if svc:
            ip = node_ip(s, s.data['cp'])
            port = svc['spec']['ports'][0].get('nodePort', 0)
            check('NodePort HTTP responds', 'nginx' in run('curl', '-fsS', '--max-time', '5', f'http://{ip}:{port}').lower())
    elif k == (2, 3):
        node = s.data['workers'][0]
        answer = s.text('certificate-info.txt')
        for path in ['/var/lib/kubelet/pki/kubelet-client-current.pem', '/var/lib/kubelet/pki/kubelet.crt']:
            text = remote(s, node, 'openssl', 'x509', '-in', path, '-noout', '-issuer', '-ext', 'extendedKeyUsage')
            check(path, all(line.strip().removeprefix('issuer=').strip() in answer for line in text.splitlines() if line.strip() and 'X509v3' not in line))
    elif k == (2, 4):
        p = s.pod('ready-if-service-ready')
        other = s.pod('am-i-ready')
        cs = containers(p)
        check('Both Pods Ready', ready(p) and ready(other))
        check('Initial NotReady checkpoint', 'not-ready' in s.data['checkpoints'])
        check('Liveness exec true', bool(cs) and cs[0].get('livenessProbe', {}).get('exec', {}).get('command') == ['true'])
        command = ' '.join(cs[0].get('readinessProbe', {}).get('exec', {}).get('command', [])) if cs else ''
        check('Readiness checks remote Service', 'service-am-i-ready' in command)
        check('Backend label', other.get('metadata', {}).get('labels', {}).get('id') == 'cross-server-ready')
    elif k == (2, 6):
        check('kubelet active', run('systemctl', 'is-active', 'kubelet').strip() == 'active')
        check('Controlplane Ready', node_ready(s, s.data['cp']))
        p = s.pod('success')
        check('success Pod Ready', ready(p) and any(c['image'] == NGINX for c in containers(p)))
    elif k == (2, 7):
        etcd = next((p for p in s.items('pods', 'kube-system') if p['metadata'].get('labels', {}).get('component') == 'etcd'), None)
        if not etcd:
            raise Blocked('Stacked etcd not found.')
        actual = s.exec(etcd['metadata']['name'], 'kube-system', 'etcd', '--version').strip()
        check('etcd server version', s.text('etcd-version') == actual)
        path = Path(s.data['course']) / 'etcd-snapshot.db'
        if not path.is_file():
            check('Snapshot exists', False)
        else:
            status = json.loads(run('etcdutl', 'snapshot', 'status', str(path), '-w', 'json'))
            check('Valid snapshot revision/keys', status.get('revision', 0) > 0 and status.get('totalKey', 0) > 0)
    elif k == (2, 8):
        answer = s.text('controlplane-components.txt')
        for component in ['kubelet', 'kube-apiserver', 'kube-scheduler', 'kube-controller-manager', 'etcd']:
            expected = 'process' if component == 'kubelet' else 'static-pod'
            check(component, re.search(rf'{component}:\s*{expected}', answer))
        check('DNS type/name', re.search(r'dns:\s*pod\s+coredns', answer, re.I))
    elif k == (2, 9):
        check('Intermediate stages', all(x in s.data['checkpoints'] for x in ['pending', 'manual']))
        for name, nodes in [('manual-schedule', [s.data['cp']]), ('manual-schedule2', s.data['workers'])]:
            p = s.pod(name)
            check(name, ready(p) and p['spec'].get('nodeName') in nodes and any(c['image'] == HTTPD for c in containers(p)))
        check('Scheduler Ready', any(ready(p) for p in s.items('pods', 'kube-system') if p['metadata'].get('labels', {}).get('component') == 'kube-scheduler'))
        p2 = s.pod('manual-schedule2')
        created = p2.get('metadata', {}).get('creationTimestamp')
        previous = s.data['checkpoints'].get('manual', {}).get('time')
        check('Second Pod created after manual checkpoint', bool(created and previous) and
            datetime.fromisoformat(created.replace('Z', '+00:00')).timestamp() >= previous)
    elif k == (2, 10):
        validate_storage(s)
    elif k == (2, 11):
        validate_secrets(s)
    elif k == (2, 12):
        p = s.pod('pod1')
        spec = p.get('spec', {})
        check('Ready on control-plane', ready(p) and spec.get('nodeName') == s.data['cp'])
        check('Container name/image', any(c['name'] == 'pod1-container' and c['image'] == HTTPD for c in containers(p)))
        selector = spec.get('nodeSelector', {})
        affinity = spec.get('affinity', {}).get('nodeAffinity', {}).get('requiredDuringSchedulingIgnoredDuringExecution', {})
        terms = affinity.get('nodeSelectorTerms', [])
        check('Required control-plane selection', selector.get('node-role.kubernetes.io/control-plane') == '' or
            bool(terms) and all(any(e['key'] == 'node-role.kubernetes.io/control-plane' and e['operator'] == 'Exists'
                for e in t.get('matchExpressions', [])) for t in terms))
        baseline_nodes(s)
        s.check('Scheduler assignment evidence', any(e.get('reason') == 'Scheduled' and
            e.get('involvedObject', {}).get('uid') == p.get('metadata', {}).get('uid') for e in s.items('events', 'default')))
    elif k == (2, 13):
        validate_multi(s)
    elif k == (2, 14):
        answer = s.text('cluster-info')
        expected = {'1': '1', '2': str(len(s.data['workers'])),
            '3': flag(Path('/etc/kubernetes/manifests/kube-apiserver.yaml').read_text(), 'service-cluster-ip-range'),
            '5': '-' + s.data['cp']}
        for n, value in expected.items():
            check('Answer ' + n, re.search(rf'(?m)^{n}:\s*{re.escape(value)}\s*$', answer))
        cni = [p for p in Path('/etc/cni/net.d').glob('*') if p.suffix in ('.conf', '.conflist')]
        check('CNI configuration path', any(str(p) in answer for p in cni))
    elif k == (2, 15):
        script_check(s, 'cluster_events.sh', ['get', 'events', '-A', '--sort-by=.metadata.creationTimestamp'])
        check('Pod deletion checkpoint', 'pod-deleted' in s.data['checkpoints'])
        check('Container restart checkpoint', 'container-restarted' in s.data['checkpoints'])
        for name in ['pod_kill.log', 'container_kill.log']:
            check(name, bool(s.text(name)) and 'kube-proxy' in s.text(name))
    elif k == (2, 16):
        actual = set(kubectl('api-resources', '--namespaced=true', '-o', 'name').splitlines())
        check('All namespaced resources', set(s.text('resources.txt').splitlines()) == actual)
        counts = {ns['metadata']['name']: len(s.items('roles', ns['metadata']['name'])) for ns in s.items('namespaces') if ns['metadata']['name'].startswith('project-')}
        name = max(counts, key=counts.get)
        answer = s.text('crowded-namespace.txt')
        check('Namespace with most Roles', name in answer and re.search(rf'\b{counts[name]}\b', answer))
    elif k == (2, 17):
        validate_operator(s)
    else:
        raise Blocked('This scenario has no released validator.')


def quantities(c, cpu, memory):
    r = c.get('resources', {}).get('requests', {})
    return qty(r.get('cpu', 0)) == qty(cpu) and qty(r.get('memory', 0)) == qty(memory)


def node_ready(s, name):
    return any(c['type'] == 'Ready' and c['status'] == 'True' for c in s.get('node', name).get('status', {}).get('conditions', []))


def node_ip(s, name):
    return next(x['address'] for x in s.get('node', name)['status']['addresses'] if x['type'] == 'InternalIP')


def remote(s, node, *command):
    if node == s.data['cp']:
        return run(*command)
    return run('ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=5', node, shlex.join(command), timeout=60)


def flag(text, name):
    match = re.search(r'--' + re.escape(name) + r'=([^\s\"\x27]+)', text)
    if not match:
        raise Blocked('Manifest flag missing: ' + name)
    return match[1]


def baseline_nodes(s):
    actual = {n['metadata']['name']: {'labels': n['metadata'].get('labels', {}), 'taints': n['spec'].get('taints', [])} for n in s.items('nodes')}
    s.check('Node labels and taints unchanged', actual == s.data['nodes'])


def script_check(s, name, tokens):
    # Never execute a student's shell file with administrator credentials.
    lines = [line for line in s.text(name).splitlines() if line.strip() and not line.lstrip().startswith('#')]
    try:
        argv = shlex.split(lines[0]) if len(lines) == 1 else []
    except ValueError:
        argv = []
    normalized = ['pod' if x == 'pods' else 'node' if x == 'nodes' else x for x in argv]
    simple = len(lines) == 1 and not any(c in lines[0] for c in ';|&`$<>')
    s.check(name, simple and bool(normalized) and normalized[0] in ('kubectl', 'k') and all(
        t in normalized or (t == '--containers' and '--containers=true' in normalized) or
        (t == '-A' and '--all-namespaces' in normalized) for t in tokens))


def checkpoint(s, stage):
    k = key(s)
    evidence = {}
    if k == (1, 20) and stage == 'old-ip':
        svc = s.get('service', 'check-ip-service', 'default')
        ip = svc.get('spec', {}).get('clusterIP')
        if not ip or ipaddress.ip_address(ip) in ipaddress.ip_network('11.96.0.0/12'):
            raise Blocked('Create the first Service in the original range before changing CIDR.')
        evidence = {'uid': svc['metadata']['uid'], 'ip': ip}
    elif k == (2, 4) and stage == 'not-ready':
        p = s.pod('ready-if-service-ready')
        if not p or ready(p) or s.pod('am-i-ready'):
            raise Blocked('First Pod must be NotReady and backend Pod absent.')
        evidence = {'uid': p['metadata']['uid']}
    elif k == (2, 9) and stage in ('pending', 'manual'):
        runtime = json.loads(run('crictl', 'ps', '-o', 'json'))['containers']
        if any(c['metadata']['name'] == 'kube-scheduler' for c in runtime):
            raise Blocked('Scheduler container still running.')
        p = s.pod('manual-schedule')
        if stage == 'pending':
            ok = bool(p) and not p['spec'].get('nodeName') and p['status']['phase'] == 'Pending'
        else:
            ok = 'pending' in s.data['checkpoints'] and ready(p) and p['spec']['nodeName'] == s.data['cp']
        if not ok:
            raise Blocked('Checkpoint conditions not satisfied.')
        evidence = {'uid': p['metadata']['uid']}
    elif k == (1, 19) and stage == 'service':
        svc = s.get('service', 'p2-service', 'project-hamster')
        rules = run('iptables-save')
        if not svc or 'project-hamster/p2-service' not in rules:
            raise Blocked('Service and iptables rules must exist.')
        evidence = {'uid': svc['metadata']['uid'], 'rules': rules}
    elif k == (2, 15):
        pods = [p for p in s.items('pods', 'kube-system') if p['metadata'].get('labels', {}).get('k8s-app') == 'kube-proxy'
            and p['spec']['nodeName'] == s.data['cp'] and ready(p)]
        if len(pods) != 1:
            raise Blocked('Expected one Ready kube-proxy Pod on control-plane.')
        p = pods[0]
        cid = p['status']['containerStatuses'][0]['containerID']
        if stage == 'pod-deleted' and p['metadata']['uid'] != s.data['proxy_initial']:
            evidence = {'uid': p['metadata']['uid'], 'container': cid}
        elif stage == 'container-restarted' and 'pod-deleted' in s.data['checkpoints']:
            before = s.data['checkpoints']['pod-deleted']
            if p['metadata']['uid'] == before['uid'] and cid != before['container']:
                evidence = {'uid': p['metadata']['uid'], 'container': cid}
    if not evidence:
        raise Blocked('Unsupported stage or checkpoint conditions not met.')
    if stage in s.data['checkpoints']:
        raise Blocked('Checkpoint already recorded.')
    evidence['time'] = time.time()
    s.data['checkpoints'][stage] = evidence
    print('Checkpoint recorded:', stage)


def restore(s, offline=False):
    if Path('/etc/machine-id').read_text() != s.data['machine_id']:
        raise Blocked('Recovery host identity changed.')
    if key(s) == (1, 20):
        if offline:
            raise Blocked('ServiceCIDR migration has no automatic rollback. Recreate this disposable playground if API is broken.')
        return
    for name, original in s.data.get('backups', {}).items():
        path = Path(name)
        if path.is_symlink():
            raise Blocked('Recovery target is a symlink.')
        if original is None:
            path.unlink(missing_ok=True)
        else:
            path.write_text(original)
    if key(s) == (2, 6):
        run('systemctl', 'daemon-reload')
        run('systemctl', 'restart', 'kubelet')
    if key(s) == (1, 8) and s.data.get('worker_detached'):
        if offline:
            raise Blocked('Worker rejoin requires a healthy control-plane API; use ./lab clean when API is available.')
        node = s.data['join_worker']
        target = s.data['join_target']
        remote(s, node, 'apt-get', 'install', '-y', '--allow-downgrades', '--allow-change-held-packages',
            'kubelet=' + target, 'kubectl=' + target, 'kubeadm=' + target)
        if not s.get('node', node):
            join = run('kubeadm', 'token', 'create', '--ttl=10m', '--print-join-command').strip()
            remote(s, node, *shlex.split(join))
        remote(s, node, 'systemctl', 'restart', 'kubelet')
        kubectl('wait', '--for=condition=Ready', 'node/' + node, '--timeout=90s')
        kubectl('uncordon', node)
    if s.data.get('coredns') and not offline:
        cm = s.get('configmap', 'coredns', 'kube-system')
        cm['data'] = s.data['coredns']
        kubectl('apply', '-f', '-', stdin=json.dumps(cm))
        kubectl('rollout', 'restart', 'deployment/coredns', '-n', 'kube-system')
    if key(s) == (1, 2) and not offline:
        releases = json.loads(run('helm', 'list', '-n', 'cert-manager', '-o', 'json'))
        if any(x['name'] == 'cert-manager' for x in releases):
            kubectl('delete', 'clusterissuer', 'course-issuer', '--ignore-not-found')
            run('helm', 'uninstall', 'cert-manager', '-n', 'cert-manager', timeout=120)
        # preflight required all cert-manager.io CRDs absent, so these belong to this exercise.
        for crd in s.items('crd'):
            if crd['metadata']['name'].endswith('cert-manager.io'):
                kubectl('delete', 'crd', crd['metadata']['name'], '--timeout=60s')
    print('System backups restored.' if s.data.get('backups') else 'No host files to restore.')


def prepare_hpa(s):
    base = Path(s.data['course']) / 'api-gateway'
    d = deployment('api-gateway', 'api-gateway-staging', HTTPD)
    d['metadata'].pop('namespace')
    d['spec']['template']['spec']['containers'][0]['resources'] = {'requests': {'cpu': '20m'}}
    cm = obj('ConfigMap', 'horizontal-scaling-config', data={'horizontal-scaling': '70'})
    s.file('api-gateway/base/deployment.yaml', json.dumps(d))
    s.file('api-gateway/base/configmap.yaml', json.dumps(cm))
    s.file('api-gateway/base/kustomization.yaml', 'resources:\n- deployment.yaml\n- configmap.yaml\n')
    for env in ['staging', 'prod']:
        ns = 'api-gateway-' + env
        s.file(f'api-gateway/{env}/kustomization.yaml', f'resources:\n- ../base\nnamespace: {ns}\n')
        kubectl('apply', '-k', str(base / env))


def validate_hpa(s):
    for env, maximum in [('staging', 4), ('prod', 6)]:
        ns = 'api-gateway-' + env
        output = kubectl('kustomize', str(Path(s.data['course']) / 'api-gateway' / env))
        s.check(env + ' rendered ConfigMap removed', 'horizontal-scaling-config' not in output)
        s.check(env + ' live ConfigMap removed', not s.get('configmap', 'horizontal-scaling-config', ns))
        h = s.get('hpa', 'api-gateway', ns).get('spec', {})
        s.check(env + ' HPA target and limits', h.get('minReplicas') == 2 and h.get('maxReplicas') == maximum
            and h.get('scaleTargetRef', {}).get('name') == 'api-gateway' and h.get('scaleTargetRef', {}).get('kind') == 'Deployment')
        s.check(env + ' CPU target 50%', any(m.get('resource', {}).get('name') == 'cpu' and
            m['resource'].get('target', {}).get('averageUtilization') == 50 for m in h.get('metrics', [])))


def validate_daemonset(s):
    ds = s.get('daemonset', 'ds-important', 'project-tiger')
    template = ds.get('spec', {}).get('template', {})
    labels = {'id': 'ds-important', 'uuid': '18426a0b-5f59-4e10-923f-c0e078e82462'}
    s.check('DaemonSet and template labels', all(ds.get('metadata', {}).get('labels', {}).get(k) == v
        and template.get('metadata', {}).get('labels', {}).get(k) == v for k, v in labels.items()))
    cs = containers(template)
    s.check('Image and requests', len(cs) == 1 and cs[0]['image'] == HTTPD and quantities(cs[0], '10m', '10Mi'))
    ps = [p for p in s.items('pods', 'project-tiger') if owned(p, ds.get('metadata', {}).get('uid'))]
    s.check('One Ready owned Pod on each node', len(ps) == len(s.data['nodes']) and all(ready(p) for p in ps)
        and {p['spec'].get('nodeName') for p in ps} == set(s.data['nodes']))
    baseline_nodes(s)


def validate_placement(s):
    ns = 'project-tiger'
    d = s.get('deployment', 'deploy-important', ns)
    spec = d.get('spec', {})
    template = spec.get('template', {})
    s.check('Replicas = workers + 1', spec.get('replicas') == len(s.data['workers']) + 1)
    s.check('Labels', d.get('metadata', {}).get('labels', {}).get('id') == 'very-important'
        and template.get('metadata', {}).get('labels', {}).get('id') == 'very-important')
    s.check('Containers', {c['name']: c['image'] for c in containers(template)} ==
        {'container1': NGINX, 'container2': 'registry.k8s.io/pause:3.10'})
    rs = {r['metadata']['uid'] for r in s.items('replicasets', ns) if owned(r, d.get('metadata', {}).get('uid'))}
    ps = [p for p in s.items('pods', ns) if any(owned(p, uid) for uid in rs) and not p['metadata'].get('deletionTimestamp')]
    running = [p for p in ps if ready(p)]
    pending = [p for p in ps if not p['spec'].get('nodeName')]
    s.check('One Ready per worker and one unassigned', len(ps) == len(s.data['workers']) + 1
        and len(running) == len(s.data['workers']) and len(pending) == 1
        and {p['spec']['nodeName'] for p in running} == set(s.data['workers']))
    ids = {p['metadata']['uid'] for p in pending}
    s.check('Pending caused by placement', any(e.get('reason') == 'FailedScheduling'
        and e.get('involvedObject', {}).get('uid') in ids and any(x in e.get('message', '').lower()
            for x in ['anti-affinity', 'topology spread']) for e in s.items('events', ns)))
    baseline_nodes(s)


def prepare_dns(s):
    ns = 'lima-workload'
    s.put(service('department', ns, {'app': 'department'}, headless=True))
    s.put(pod('department1', ns, labels={'app': 'department'}))
    s.put(service('section', ns, {'app': 'section'}, headless=True))
    p = pod('section100', ns, labels={'app': 'section'}, hostname='section100', subdomain='section')
    s.put(p)
    s.put(obj('ConfigMap', 'control-config', 'lima-control', data={f'DNS_{i}': 'invalid.local' for i in range(1, 5)}))
    d = deployment('controller', 'lima-control', BUSYBOX)
    c = d['spec']['template']['spec']['containers'][0]
    c['command'] = ['sh', '-c', 'while true; do for x in "$DNS_1" "$DNS_2" "$DNS_3" "$DNS_4"; do nslookup "$x"; done; sleep 10; done']
    c['envFrom'] = [{'configMapRef': {'name': 'control-config'}}]
    s.put(d)


def validate_dns(s):
    expected = {
        'DNS_1': 'kubernetes.default.svc.cluster.local', 'DNS_2': 'department.lima-workload.svc.cluster.local',
        'DNS_3': 'section100.section.lima-workload.svc.cluster.local', 'DNS_4': '1-2-3-4.kube-system.pod.cluster.local'}
    cm = s.get('configmap', 'control-config', 'lima-control')
    s.check('Four FQDN values', cm.get('data') == expected)
    ps = [p for p in s.items('pods', 'lima-control') if p['metadata'].get('labels', {}).get('app') == 'controller' and ready(p)]
    s.check('Controller Ready', bool(ps))
    if ps:
        for variable, domain in expected.items():
            actual = s.exec(ps[0]['metadata']['name'], 'lima-control', 'printenv', variable).strip()
            s.check(variable + ' loaded into Pod', actual == domain)
            output = s.exec(ps[0]['metadata']['name'], 'lima-control', 'nslookup', domain)
            s.check(variable + ' resolves', 'Address' in output)


def dns_check(s, domain):
    ns = 'ks-dns-probe'
    if not any(r['key'] == ['namespace', ns, None] for r in s.data['resources']):
        s.namespace(ns)
        p = pod('probe', ns, BUSYBOX)
        p['spec']['containers'][0]['command'] = ['sleep', '3600']
        s.put(p)
    kubectl('wait', '-n', ns, '--for=condition=Ready', 'pod/probe', '--timeout=60s')
    s.check(domain, 'Address' in s.exec('probe', ns, 'nslookup', domain))


def validate_secrets(s):
    p = s.pod('secret-pod', 'secret')
    s.check('Pod Ready busybox', ready(p) and any(c['image'] == BUSYBOX for c in containers(p)))
    secret = s.get('secret', 'secret2', 'secret')
    data = secret.get('data', {})
    s.check('Secret2 contents', data.get('user') == base64.b64encode(b'user1').decode()
        and data.get('pass') == base64.b64encode(b'1234').decode())
    volumes = {v['name'] for v in p.get('spec', {}).get('volumes', []) if v.get('secret', {}).get('secretName') == 'secret1'}
    cs = containers(p)
    s.check('Read-only Secret1 mount', any(v['name'] in volumes and v['mountPath'] == '/tmp/secret1' and v.get('readOnly')
        for c in cs for v in c.get('volumeMounts', [])))
    env = {e['name']: e.get('valueFrom', {}).get('secretKeyRef', {}) for c in cs for e in c.get('env', [])}
    s.check('Secret references in environment', env.get('APP_USER') == {'name': 'secret2', 'key': 'user'}
        and env.get('APP_PASS') == {'name': 'secret2', 'key': 'pass'})
    if ready(p):
        s.check('Actual env values', s.exec('secret-pod', 'secret', 'printenv', 'APP_USER').strip() == 'user1'
            and s.exec('secret-pod', 'secret', 'printenv', 'APP_PASS').strip() == '1234')
        s.check('Secret1 file', s.exec('secret-pod', 'secret', 'cat', '/tmp/secret1/message').strip() == 'training-secret')


def validate_multi(s):
    p = s.pod('multi-container-playground')
    cs = {c['name']: c for c in containers(p)}
    s.check('Three Ready containers', ready(p) and set(cs) == {'c1', 'c2', 'c3'})
    if set(cs) != {'c1', 'c2', 'c3'}:
        return
    s.check('Images', cs['c1']['image'] == NGINX and cs['c2']['image'] == BUSYBOX and cs['c3']['image'] == BUSYBOX)
    s.check('Downward API', any(e.get('name') == 'MY_NODE_NAME' and e.get('valueFrom', {}).get('fieldRef', {}).get('fieldPath') == 'spec.nodeName'
        for e in cs['c1'].get('env', [])))
    empty = {v['name'] for v in p['spec'].get('volumes', []) if 'emptyDir' in v}
    shared = empty.copy()
    for c in cs.values():
        shared &= {v['name'] for v in c.get('volumeMounts', [])}
    s.check('Shared emptyDir', bool(shared))
    if ready(p):
        env = s.exec('multi-container-playground', 'default', 'printenv', 'MY_NODE_NAME', container='c1').strip()
        s.check('Actual node env', env == p['spec']['nodeName'])
        before = kubectl('logs', 'multi-container-playground', '-c', 'c3')
        time.sleep(2)
        after = kubectl('logs', 'multi-container-playground', '-c', 'c3')
        s.check('Reader logs keep growing', len(after) > len(before) > 0)


def validate_storage(s):
    ns = 'project-bern'
    sc = s.get('storageclass', 'local-backup')
    s.check('StorageClass settings', sc.get('provisioner') == 'rancher.io/local-path' and sc.get('reclaimPolicy') == 'Retain'
        and sc.get('volumeBindingMode') == 'WaitForFirstConsumer')
    job = s.get('job', 'backup', ns)
    s.check('Job completed once', job.get('status', {}).get('succeeded', 0) == 1)
    claims = [v['persistentVolumeClaim']['claimName'] for v in job.get('spec', {}).get('template', {}).get('spec', {}).get('volumes', []) if 'persistentVolumeClaim' in v]
    s.check('Job uses PVC', bool(claims))
    for name in claims:
        pvc = s.get('pvc', name, ns)
        s.check('PVC class/size/bound', pvc.get('spec', {}).get('storageClassName') == 'local-backup'
            and qty(pvc.get('spec', {}).get('resources', {}).get('requests', {}).get('storage', 0)) == qty('50Mi')
            and pvc.get('status', {}).get('phase') == 'Bound')
        if pvc.get('spec', {}).get('volumeName'):
            pv = s.get('pv', pvc['spec']['volumeName'])
            s.check('PV Retain policy', pv.get('spec', {}).get('persistentVolumeReclaimPolicy') == 'Retain')


def prepare_gateway(s):
    ns = 'project-r500'
    classes = s.items('gatewayclasses.gateway.networking.k8s.io')
    accepted = next(c['metadata']['name'] for c in classes if any(x.get('type') == 'Accepted' and x.get('status') == 'True'
        for x in c.get('status', {}).get('conditions', [])))
    gateway = obj('Gateway', 'main', ns, spec={'gatewayClassName': accepted,
        'listeners': [{'name': 'http', 'protocol': 'HTTP', 'port': 80}]})
    gateway['apiVersion'] = 'gateway.networking.k8s.io/v1'
    s.put(gateway)
    for suffix in ['desktop', 'mobile']:
        name = 'web-' + suffix
        cm = obj('ConfigMap', name, ns, data={'default.conf': f'server {{ listen 80; location / {{ return 200 "Web {suffix} App\\n"; }} }}'})
        s.put(cm)
        d = deployment(name, ns)
        spec = d['spec']['template']['spec']
        spec['volumes'] = [{'name': 'config', 'configMap': {'name': name}}]
        spec['containers'][0]['volumeMounts'] = [{'name': 'config', 'mountPath': '/etc/nginx/conf.d/default.conf', 'subPath': 'default.conf'}]
        s.put(d)
        s.put(service(name, ns, {'app': name}))
    s.file('ingress.yaml', 'apiVersion: networking.k8s.io/v1\nkind: Ingress\nmetadata:\n  name: traffic-director\nspec:\n  rules:\n  - host: r500.gateway\n    http:\n      paths:\n' + ''.join(
        f'      - path: /{name}\n        pathType: Prefix\n        backend:\n          service:\n            name: web-{name}\n            port:\n              number: 80\n' for name in ['desktop', 'mobile']))


def validate_gateway(s):
    route = s.get('httproute', 'traffic-director', 'project-r500')
    s.check('HTTPRoute references main', any(r['name'] == 'main' for r in route.get('spec', {}).get('parentRefs', [])))
    conditions = [c for p in route.get('status', {}).get('parents', []) for c in p.get('conditions', [])]
    s.check('Accepted and ResolvedRefs', all(any(c['type'] == t and c['status'] == 'True' for c in conditions) for t in ['Accepted', 'ResolvedRefs']))
    gateway = s.get('gateway', 'main', 'project-r500')
    addresses = gateway.get('status', {}).get('addresses', [])
    if not addresses:
        raise Blocked('Gateway has no usable address; check controller provisioning.')
    address = addresses[0]['value']
    for path, ua, expected in [('/desktop', None, 'desktop'), ('/mobile', None, 'mobile'),
                              ('/auto', 'mobile', 'mobile'), ('/auto', 'other', 'desktop')]:
        args = ['curl', '-fsS', '--max-time', '5', '-H', 'Host: r500.gateway']
        if ua:
            args += ['-H', 'User-Agent: ' + ua]
        output = run(*args, f'http://{address}{path}')
        s.check(path + ' ' + str(ua), expected in output.lower())


def validate_policy(s):
    ns = 'project-snake'
    policy = s.get('networkpolicy', 'np-backend', ns)
    s.check('Backend egress policy', policy.get('spec', {}).get('podSelector', {}).get('matchLabels', {}).get('app') == 'backend'
        and 'Egress' in policy.get('spec', {}).get('policyTypes', []))
    pods = {p['metadata']['name']: p for p in s.items('pods', ns)}
    if not all(ready(p) for p in pods.values()) or len(pods) < 4:
        raise Blocked('Wait for all fixture Pods to become Ready.')
    for name, port, allowed in [('db1-0', 1111, True), ('db2-0', 2222, True), ('db1-0', 2222, False), ('db2-0', 1111, False), ('vault-0', 3333, False)]:
        ip = pods[name]['status']['podIP']
        # Check listener from the destination first; an unavailable server must not pass a deny test.
        s.exec(name, ns, 'curl', '-fsS', '--max-time', '3', f'http://127.0.0.1:{port}')
        try:
            output = s.exec('backend-0', ns, 'curl', '-fsS', '--connect-timeout', '2', '--max-time', '3', f'http://{ip}:{port}')
            reached = bool(output)
        except Blocked as exc:
            if 'exited 28' not in str(exc) and 'exit code 28' not in str(exc):
                raise
            reached = False
        s.check(f'{name}:{port} ' + ('allow' if allowed else 'deny'), reached == allowed)


def prepare_operator(s):
    for plural, singular in [('students', 'student'), ('classes', 'class')]:
        crd = obj('CustomResourceDefinition', plural + '.education.killer.sh', spec={
            'group': 'education.killer.sh', 'scope': 'Namespaced',
            'names': {'plural': plural, 'singular': singular, 'kind': singular.title()},
            'versions': [{'name': 'v1', 'served': True, 'storage': True, 'schema': {'openAPIV3Schema': {
                'type': 'object', 'properties': {'spec': {'type': 'object', 'properties': {
                    'name': {'type': 'string'}, 'description': {'type': 'string'}}}}}}}]})
        s.put(crd)
        kubectl('wait', '--for=condition=Established', 'crd/' + plural + '.education.killer.sh', '--timeout=60s')
    ns = 'operator-prod'
    sa = obj('ServiceAccount', 'operator', ns)
    role = obj('Role', 'operator-role', ns, rules=[])
    binding = obj('RoleBinding', 'operator-rolebinding', ns,
        roleRef={'apiGroup': 'rbac.authorization.k8s.io', 'kind': 'Role', 'name': 'operator-role'},
        subjects=[{'kind': 'ServiceAccount', 'name': 'operator', 'namespace': ns}])
    d = deployment('operator', ns, 'python:3.12-alpine')
    d['spec']['template']['spec']['serviceAccountName'] = 'operator'
    client = '''import json, ssl, time, urllib.request, urllib.error
from pathlib import Path
root = Path('/var/run/secrets/kubernetes.io/serviceaccount')
context = ssl.create_default_context(cafile=str(root / 'ca.crt'))
while True:
    for resource in ('students', 'classes'):
        url = 'https://kubernetes.default/apis/education.killer.sh/v1/namespaces/operator-prod/' + resource
        request = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + (root / 'token').read_text().strip()})
        try:
            with urllib.request.urlopen(request, context=context, timeout=5) as response:
                data = json.load(response)
                print(resource + ': ' + ', '.join(x['metadata']['name'] for x in data['items']), flush=True)
        except urllib.error.HTTPError as error:
            print(error.read().decode(), flush=True)
        except Exception as error:
            print(str(error), flush=True)
    time.sleep(10)
'''
    d['spec']['template']['spec']['containers'][0]['command'] = ['python', '-u', '-c', client]
    resources = [sa, role, binding, d]
    for i in range(1, 4):
        student = obj('Student', f'student{i}', ns, spec={'name': f'Student {i}', 'description': 'Training'})
        student['apiVersion'] = 'education.killer.sh/v1'
        resources.append(student)
    for i, resource in enumerate(resources):
        s.file(f'operator/base/resource-{i}.json', json.dumps(resource, indent=2))
        s.put(resource)
    s.file('operator/base/kustomization.yaml', 'resources:\n' + ''.join(f'- resource-{i}.json\n' for i in range(len(resources))))
    s.file('operator/prod/kustomization.yaml', 'resources:\n- ../base\nnamespace: operator-prod\n')


def validate_operator(s):
    ns = 'operator-prod'
    for resource in ['students', 'classes']:
        role = s.get('role', 'operator-role', ns)
        s.check('Role list ' + resource, any('education.killer.sh' in r.get('apiGroups', []) and resource in r.get('resources', [])
            and 'list' in r.get('verbs', []) for r in role.get('rules', [])))
    student = s.get('student', 'student4', ns)
    s.check('student4 fields', bool(student.get('spec', {}).get('name')) and bool(student.get('spec', {}).get('description')))
    render = kubectl('kustomize', str(Path(s.data['course']) / 'operator/prod'))
    s.check('student4 in Kustomize source', 'student4' in render)
    ps = [p for p in s.items('pods', ns) if p['metadata'].get('labels', {}).get('app') == 'operator' and ready(p)]
    s.check('Operator Ready', bool(ps))
    if ps:
        logs = kubectl('logs', '-n', ns, ps[0]['metadata']['name'], '--since=15s')
        s.check('Recent operator output lists students', 'student4' in logs and 'Forbidden' not in logs)
