You're attempting to deploy Falco with the `values-k8saudit.yaml` configuration **behind a firewall** using a **JFrog proxy** (with a pull secret) to retrieve open source artifacts. This file triggers the `falcoctl` init and sidecar containers to **pull artifacts dynamically** at runtime, which can **fail in air-gapped or proxied environments** like yours.

---

### 🚨 Problem Summary

The critical issue here is:

> `falcoctl.artifact.install.refs` and `falcoctl.artifact.follow.refs` attempt to download plugins and rules from `https://download.falco.org`.

This fails behind a firewall unless JFrog is explicitly caching those artifacts and Falco is configured to fetch them from there.

---

### ✅ Recommendations

Here’s what you need to do to make this work behind a firewall using JFrog:

---

#### **1. Manually Download Required Artifacts**

Download the following manually **via a network that has access**, and **upload them into your JFrog proxy**:

* `https://download.falco.org/plugins/k8saudit/0.11/k8saudit.linux-x86_64.so`
* `https://download.falco.org/plugins/k8saudit-rules/0.11/k8s_audit_rules.yaml`
* `https://download.falco.org/plugins/json/latest/json.linux-x86_64.so`

You can find official artifacts here:
🔗 [https://falco.org/docs/plugins/plugins-list/](https://falco.org/docs/plugins/plugins-list/)

---

#### **2. Host Artifacts in JFrog**

Upload them into a specific path on your JFrog proxy, for example:

```
https://myjfrog.example.com/falco-plugins/k8saudit/0.11/k8saudit.linux-x86_64.so
https://myjfrog.example.com/falco-plugins/k8saudit-rules/0.11/k8s_audit_rules.yaml
https://myjfrog.example.com/falco-plugins/json/latest/json.linux-x86_64.so
```

---

#### **3. Disable falcoctl Artifact Downloading**

Update your `values-k8saudit.yaml`:

```yaml
falcoctl:
  artifact:
    install:
      enabled: false
    follow:
      enabled: false
```

---

#### **4. Bundle Artifacts into the Image or Mount Them**

**Option A:** Custom Falco image
Create a custom Falco image with these plugins and rules pre-baked into the image:

```Dockerfile
FROM falcosecurity/falco:latest
COPY k8saudit.linux-x86_64.so /usr/share/falco/plugins/libk8saudit.so
COPY k8s_audit_rules.yaml /etc/falco/k8s_audit_rules.yaml
COPY json.linux-x86_64.so /usr/share/falco/plugins/libjson.so
```

**Option B:** Use a ConfigMap/Volume mount
Mount these via Kubernetes volumes (ConfigMap or Secret).

---

#### **5. Make Sure to Mount Plugin and Rule Paths Correctly**

Ensure your paths in `falco.rules_files` and `falco.plugins` match where you've mounted/copied the files.

```yaml
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

---

### 🧪 Optional: Test Plugin Functionality Locally

Use `falcoctl` locally on a machine that has internet access to inspect and download the artifacts to verify their structure:

```bash
falcoctl artifact get k8saudit:0.11 --extract
falcoctl artifact get k8saudit-rules:0.11 --extract
```

---

### ✅ Final YAML Cleanup (Minimal working version)

```yaml
falcoctl:
  artifact:
    install:
      enabled: false
    follow:
      enabled: false

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

---

Let me know if you’d like help generating the custom Falco Dockerfile or Kubernetes manifests for mounting the plugins.
