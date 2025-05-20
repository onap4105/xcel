Below are two ways to have your Kubernetes API-server send every audit event into Falco’s k8saudit webhook at `http://<service>:9765/k8s-audit`. Pick the one that matches your cluster setup:

---

## 1) Dynamic Auditing (AuditSink) — no API-server restart

> **Kubernetes v1.13+**

Create a **Policy** and an **AuditSink** CRD. The sink points at your Falco webhook service (e.g. `k8saudit-webhook.falco.svc.cluster.local:9765`).

```yaml
# audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
# capture metadata for all requests (tweak level/rules as needed)
# see https://kubernetes.io/docs/tasks/debug-application-cluster/audit/#policy
rules:
  - level: Metadata
    # you can add `resources:`/`verbs:` filters here
```

```yaml
# audit-sink.yaml
apiVersion: auditregistration.k8s.io/v1alpha1
kind: AuditSink
metadata:
  name: falco-webhook
spec:
  policy:
    # reference the policy above
    auditPolicy:
      name: audit-policy
  webhook:
    throttle:
      qps: 10
      burst: 15
    clientConfig:
      service:
        namespace: falco
        name: k8saudit-webhook
        path: /k8s-audit
        port: 9765
      # if your webhook uses a serving cert signed by a private CA:
      # caBundle: <base64-encoded-CA-cert>
```

1. `kubectl apply -f audit-policy.yaml`
2. `kubectl apply -f audit-sink.yaml`

After a few seconds, every API request/response metadata (per your policy) will flow into Falco.

---

## 2) Static Auditing (API-server flags) — requires restart

If you manage your own control plane manifests, you can instead point your kube-apiserver at a webhook config file.

1. **Create** `/etc/kubernetes/audit-policy.yaml` (same content as above).

2. **Create** `/etc/kubernetes/webhook-config.yaml`:

   ```yaml
   apiVersion: v1
   kind: Config
   clusters:
     - name: falco-webhook
       cluster:
         # use the in-cluster service DNS
         server: https://k8saudit-webhook.falco.svc.cluster.local:9765
         insecure-skip-tls-verify: true   # or provide caBundle
   users:
     - name: falco-webhook
   contexts:
     - context:
         cluster: falco-webhook
         user: falco-webhook
       name: falco-webhook
   current-context: falco-webhook
   ```

3. **Edit** your kube-apiserver manifest (e.g. kube-adm static pod) to include:

   ```
   --audit-policy-file=/etc/kubernetes/audit-policy.yaml
   --audit-log-path=/var/log/kubernetes/audit.log      # (optional)
   --audit-webhook-config-file=/etc/kubernetes/webhook-config.yaml
   --audit-webhook-batch-max-wait=10ms
   --audit-webhook-initial-backoff=10ms
   ```

4. **Restart** the API-server. Now every audit event is both logged locally (if you set `--audit-log-path`) and POSTed to Falco’s webhook.

---

### Verifying it’s working

After either approach:

```bash
kubectl get pods -n falco -l app=falco
kubectl logs -n falco <falco-pod>
```

You should see lines like:

```
Starting k8saudit plugin (listening on :9765/k8s-audit)…
Received audit event POST /k8s-audit
```

And in Falco’s logs you’ll see rules firing against those audit events.

— Let me know if you need tweaks to the policy (e.g. include RequestResponse data) or help handling TLS/certs.
