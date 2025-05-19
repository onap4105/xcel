Here's the updated `values-k8saudit.yaml` with JFrog proxy integration and firewall adjustments:

```yaml
# -- Disable the drivers since we want to deploy only the k8saudit plugin.
driver:
  enabled: false

# -- Disable the collectors, no syscall events to enrich with metadata.
collectors:
  enabled: false

# -- Deploy Falco as a deployment. One instance of Falco is enough.
controller:
  kind: deployment
  deployment:
    replicas: 1

# -- JFrog proxy configuration for artifact management
falcoctl:
  artifact:
    install:
      enabled: true
    follow:
      enabled: true
  config:
    artifact:
      allowedRepos: ["jfrog.example.com/artifactory/falco-proxy"]  # Whitelist JFrog repo
      install:
        refs: 
          - "jfrog.example.com/artifactory/falco-proxy/k8saudit-rules:0.11"
          - "jfrog.example.com/artifactory/falco-proxy/k8saudit:0.11"
      follow:
        refs: 
          - "jfrog.example.com/artifactory/falco-proxy/k8saudit-rules:0.11"

# -- Add JFrog pull secret for artifact download
imagePullSecrets:
  - name: jfrog-pull-secret  # Your JFrog registry secret

services:
  - name: k8saudit-webhook
    type: NodePort
    ports:
      - port: 9765
        nodePort: 30007
        protocol: TCP

# -- TLS/SSL configuration for JFrog proxy (if using self-signed certs)
falco:
  extraVolumes:
    - name: jfrog-ca-cert
      secret:
        secretName: jfrog-ca-cert-secret  # Your CA cert secret
  extraVolumeMounts:
    - name: jfrog-ca-cert
      mountPath: /etc/ssl/certs/jfrog-ca.crt
      subPath: jfrog-ca.crt
  env:
    - name: SSL_CERT_FILE
      value: /etc/ssl/certs/jfrog-ca.crt

  rules_files:
    - /etc/falco/k8s_audit_rules.yaml
    - /etc/falco/rules.d
  plugins:
    - name: k8saudit
      library_path: libk8saudit.so
      init_config:
        ""
      open_params: "http://:9765/k8s-audit"
    - name: json
      library_path: libjson.so
      init_config: ""
  load_plugins: [k8saudit, json]
```

Key changes made:
1. Added `imagePullSecrets` for JFrog authentication
2. Modified artifact `refs` to point to JFrog repository
3. Added `allowedRepos` whitelist for security
4. Added TLS/SSL configuration section (optional if using self-signed certs)

**Before deploying:**
1. Replace placeholder values:
   - `jfrog.example.com/artifactory/falco-proxy` → Your JFrog repository URL
   - `jfrog-pull-secret` → Your image pull secret name
   - `jfrog-ca-cert-secret` → Your CA certificate secret (if using self-signed certs)

2. If not using self-signed certificates, remove:
   - `extraVolumes`
   - `extraVolumeMounts`
   - `env` section for SSL_CERT_FILE

3. Ensure your JFrog repository contains these artifacts:
   - `k8saudit-rules:0.11`
   - `k8saudit:0.11`



Here's the complete updated `values-k8saudit.yaml` with explicit JFrog registry configuration and firewall compliance:

```yaml
# -- Disable the drivers since we want to deploy only the k8saudit plugin.
driver:
  enabled: false

# -- Disable the collectors, no syscall events to enrich with metadata.
collectors:
  enabled: false

# -- Deploy Falco as a deployment
controller:
  kind: deployment
  deployment:
    replicas: 1

# -- JFrog Artifactory integration for falcoctl
falcoctl:
  artifact:
    install:
      enabled: true
    follow:
      enabled: true
  config:
    artifact:
      # -- Whitelist your JFrog repository
      allowedRepos: ["jfrog.example.com/artifactory/falco-proxy"]
      # -- Define custom repository mapping
      repos:
        - name: "jfrog-falco"
          url: "jfrog.example.com/artifactory/falco-proxy"
      # -- Artifact references using JFrog repo
      install:
        refs:
          - "jfrog-falco/k8saudit-rules:0.11"
          - "jfrog-falco/k8saudit:0.11"
      follow:
        refs:
          - "jfrog-falco/k8saudit-rules:0.11"

# -- Image pull secret for JFrog authentication
imagePullSecrets:
  - name: jfrog-pull-secret

# -- Kubernetes audit webhook configuration
services:
  - name: k8saudit-webhook
    type: NodePort
    ports:
      - port: 9765
        nodePort: 30007
        protocol: TCP

# -- Falco core configuration
falco:
  # -- TLS configuration (only if using self-signed certificates)
  extraVolumes:
    - name: jfrog-ca-cert
      secret:
        secretName: jfrog-ca-cert-secret
  extraVolumeMounts:
    - name: jfrog-ca-cert
      mountPath: /etc/ssl/certs/jfrog-ca.crt
      subPath: jfrog-ca.crt
  env:
    - name: SSL_CERT_FILE
      value: /etc/ssl/certs/jfrog-ca.crt

  # -- Plugin and rules configuration
  rules_files:
    - /etc/falco/k8s_audit_rules.yaml
    - /etc/falco/rules.d
  plugins:
    - name: k8saudit
      library_path: libk8saudit.so
      init_config:
        ""
      open_params: "http://:9765/k8s-audit"
    - name: json
      library_path: libjson.so
      init_config: ""
  load_plugins: [k8saudit, json]
```

### Replacement Guide
1. **JFrog Configuration**:
   - Replace `jfrog.example.com/artifactory/falco-proxy` with your actual JFrog Artifactory URL
   - Replace `jfrog-falco` with your preferred repository alias (must match in `refs`)

2. **Secrets**:
   - Replace `jfrog-pull-secret` with your actual image pull secret name
   - Replace `jfrog-ca-cert-secret` with your CA certificate secret name (if using self-signed certs)

3. **Optional TLS**:
   - Remove the entire `extraVolumes`, `extraVolumeMounts`, and `env` sections if not using self-signed certificates

### Verification Steps
1. Ensure JFrog contains these artifacts:
   ```bash
   jfrog-falco/k8saudit-rules:0.11
   jfrog-falco/k8saudit:0.11
   ```

2. Validate artifact paths match your JFrog repository structure:
   ```bash
   curl -v https://jfrog.example.com/artifactory/falco-proxy/k8saudit-rules:0.11
   ```

3. Deploy with Helm:
   ```bash
   helm upgrade falco falcosecurity/falco \
     --install \
     --namespace falco \
     -f values-k8saudit.yaml
   ```

This configuration ensures all artifact operations go through your JFrog proxy while maintaining the Kubernetes audit-specific setup. The `falcoctl` component will now resolve artifacts using your private registry instead of public sources.
