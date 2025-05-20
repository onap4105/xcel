The “No such file or directory” indicates that, inside your Falco pod, nothing was ever mounted or baked into `/usr/share/falco/plugins/libk8saudit.so`. You need to make sure that path really exists in the container at runtime—either by building it into your image or by mounting it via a volume. Here are two ways to fix it:

---

## 1) Build a custom Falco image with the `.so` baked in

**Dockerfile**

```dockerfile
FROM falcosecurity/falco:0.40.0

# copy your locally built plugins
COPY libk8saudit.so /usr/share/falco/plugins/libk8saudit.so
COPY libjson.so      /usr/share/falco/plugins/libjson.so

# copy your rules
COPY k8s_audit_rules.yaml /etc/falco/k8s_audit_rules.yaml
```

```bash
docker build -t myregistry/falco-custom:0.40.0 .
docker push myregistry/falco-custom:0.40.0
```

Then in your `values-k8saudit.yaml` override the image:

```yaml
controller:
  deployment:
    image:
      repository: myregistry/falco-custom
      tag: "0.40.0"
```

Falco will then see `/usr/share/falco/plugins/libk8saudit.so` because you baked it in.

---

## 2) Mount the plugins via a ConfigMap or Secret

### a) Create a ConfigMap (or Secret) with your `.so` files

```bash
kubectl -n falco create configmap falco-plugins \
  --from-file=libk8saudit.so=./libk8saudit.so \
  --from-file=libjson.so=./libjson.so
```

### b) In your Helm values, tell the chart to mount that ConfigMap

```yaml
# values-k8saudit.yaml
controller:
  deployment:
    extraVolumes:
      - name: falco-plugins
        configMap:
          name: falco-plugins

    extraVolumeMounts:
      - name: falco-plugins
        mountPath: /usr/share/falco/plugins
        readOnly: true

falco:
  rules_files:
    - /etc/falco/k8s_audit_rules.yaml

  plugins:
    - name: k8saudit
      library_path: /usr/share/falco/plugins/libk8saudit.so
      init_config: ""
      open_params: "http://:9765/k8s-audit"
    - name: json
      library_path: /usr/share/falco/plugins/libjson.so
      init_config: ""

  load_plugins: [k8saudit, json]
```

This will mount **both** `.so` files into `/usr/share/falco/plugins` where Falco expects them.

---

### Quick sanity-check

After you redeploy, run:

```bash
kubectl exec -n falco -it pod/falco-547f88cc9-9fm6p -- ls -l /usr/share/falco/plugins
```

You should see your `libk8saudit.so` and `libjson.so` there. If yes, then:

```bash
kubectl logs -n falco pod/falco-547f88cc9-9fm6p
```

should show the plugin loading successfully rather than “no such file.”

---

Pick whichever approach fits your workflow—baking into an image for immutable deployments, or mounting via ConfigMap if you need to change plugins without rebuilding. Let me know which one you’ll use or if you need any tweaks!
