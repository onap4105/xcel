This Message Is From an External Sender 
This message came from outside AT&T. Click for additional detail. 




To resolve a **kube-apiserver startup probe failure with a 403 Forbidden error**, follow these steps:

---

### 1. **Check API Server Logs**
   - Look for explicit authorization failures in the logs:
     ```bash
     journalctl -u kube-apiserver -n 100 --no-pager | grep -i "403"
     ```
   - Focus on entries mentioning `Forbidden`, `RBAC`, or `permission denied`.

---

### 2. **Validate the Startup Probe Configuration**
   - Ensure the probe uses the correct **path** and **port** in the API server manifest:
     ```yaml
     startupProbe:
       httpGet:
         path: /livez      # Use `/livez` or `/readyz` (not `/healthz`)
         port: 6443
         scheme: HTTPS
     ```
   - Incorrect paths (e.g., `/healthz`) may trigger 403s if RBAC blocks access.

---

### 3. **Verify RBAC Permissions**
   - The kubelet uses the `system:node` or `system:kubelet` identity to contact the API server. Ensure it has access to the probe endpoints:
     ```bash
     kubectl get clusterrole system:kubelet-api-admin -o yaml
     ```
   - Confirm the role has rules allowing access to `get` on the `/livez` and `/readyz` endpoints:
     ```yaml
     apiVersion: rbac.authorization.k8s.io/v1
     kind: ClusterRole
     metadata:
       name: system:kubelet-api-admin
     rules:
     - apiGroups: [""]
       resources: ["nodes/proxy", "nodes/log", "nodes/stats", "nodes/metrics"]
       verbs: ["*"]
     - nonResourceURLs: ["/livez", "/readyz", "/healthz"]  # Ensure these are listed
       verbs: ["get"]
     ```

   - If permissions are missing, update the role:
     ```bash
     kubectl edit clusterrole system:kubelet-api-admin
     ```

---

### 4. **Check Kubelet Credentials**
   - The kubelet uses a client certificate to authenticate. Verify its **Subject** (CN and O fields):
     ```bash
     openssl x509 -in /var/lib/kubelet/pki/kubelet-client-current.pem -noout -subject
     ```
   - The certificate should include:
     - **CN (Common Name):** `system:node:<node-name>`
     - **O (Organization):** `system:nodes`
   - If missing, regenerate the kubelet certificate or fix certificate rotation.

---

### 5. **Confirm API Server Authorization Modes**
   - Ensure the API server is configured with `--authorization-mode=Node,RBAC`:
     ```bash
     ps aux | grep kube-apiserver | grep authorization-mode
     ```
   - If `Node` authorization is missing, add it to the API server manifest (`/etc/kubernetes/manifests/kube-apiserver.yaml`).

---

### 6. **Check Admission Controllers**
   - Misconfigured admission controllers (e.g., `NodeRestriction`) might block probes. Review the API server flags:
     ```bash
     ps aux | grep kube-apiserver | grep admission-plugins
     ```
   - Temporarily test by disabling problematic admission controllers (e.g., `--disable-admission-plugins=PodSecurityPolicy`).

---

### 7. **Audit API Server Flags**
   - Ensure the API server trusts the kubelet’s certificate authority:
     ```bash
     grep -i client-ca-file /etc/kubernetes/manifests/kube-apiserver.yaml
     ```
   - The flag `--client-ca-file` should point to your cluster’s CA (e.g., `/etc/kubernetes/pki/ca.crt`).

---

### 8. **Check Anonymous Auth Settings**
   - If `--anonymous-auth=false` is set, even health checks may require credentials. Ensure it’s enabled:
     ```bash
     ps aux | grep kube-apiserver | grep anonymous-auth
     ```
   - Default is `--anonymous-auth=true`. If disabled, re-enable it in the API server manifest.

---

### 9. **Test Access Manually**
   - Use `curl` to test the probe endpoint from the node:
     ```bash
     curl -k -v --cert /var/lib/kubelet/pki/kubelet-client-current.pem \
          --key /var/lib/kubelet/pki/kubelet-client-current.pem \
          https://localhost:6443/livez
     ```
   - If this returns 403, the issue is likely RBAC or certificate-related.

---

### 10. **Renew Certificates**
   - For kubeadm clusters, renew certificates if they are misconfigured:
     ```bash
     kubeadm certs renew all
     systemctl restart kubelet
     ```

---

### 11. **Check Audit Logs**
   - Inspect API server audit logs for details on the 403 error:
     ```bash
     grep -i "forbidden" /var/log/kubernetes/audit/audit.log
     ```

---

### **Summary**
A **403 Forbidden** error indicates the kubelet’s credentials are authenticated but lack RBAC permissions to access the probe endpoint. Focus on:
1. Correct RBAC rules for `system:kubelet-api-admin`.
2. Valid kubelet certificates with proper `system:nodes` group membership.
3. Proper API server flags (`--authorization-mode=Node,RBAC` and `--client-ca-file`).
4. Valid startup probe paths (`/livez` or `/readyz`).

Sent from Yahoo Mail for iPhone

A `401 Unauthorized` error during the **`kube-apiserver` self `livez` check** typically indicates an authentication failure when the API server attempts to verify its own health. This is unusual because the `livez`/`readyz` endpoints are designed to bypass authentication/authorization by default. Below are the most likely causes and solutions:

---

### **1. Misconfigured `--anonymous-auth` Flag**
- **Problem:** If the `kube-apiserver` is started with `--anonymous-auth=false`, it disables anonymous access to the API server. This blocks unauthenticated requests to the `/livez` endpoint, causing a `401` error.
- **Fix:**  
  Ensure the `--anonymous-auth` flag is set to `true` (the default). Check the API server manifest (e.g., `/etc/kubernetes/manifests/kube-apiserver.yaml`):
  ```yaml
  - command:
    - kube-apiserver
    - --anonymous-auth=true  # Ensure this is present and set to "true"
  ```

---

### **2. Admission Controller Interference**
- **Problem:** Aggressive admission controllers (e.g., `NodeRestriction`, custom webhooks) might block anonymous requests to the health endpoints.
- **Fix:**  
  - Verify if an admission controller is denying access to the `/livez` endpoint. Check API server logs for clues:
    ```bash
    kubectl logs -n kube-system kube-apiserver-<node-name> | grep -i "unauthorized"
    ```
  - Whitelist the `/livez`, `/readyz`, and `/healthz` endpoints in admission control configurations if necessary.

---

### **3. RBAC Misconfiguration**
- **Problem:** The `system:anonymous` user or `system:unauthenticated` group might lack permissions to access the health endpoints due to overly restrictive RBAC policies.
- **Fix:**  
  Ensure the following RBAC rules exist to allow unauthenticated access to health checks:
  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: ClusterRole
  metadata:
    name: healthz-access
  rules:
  - nonResourceURLs: ["/livez", "/readyz", "/healthz"]
    verbs: ["get"]
  ---
  apiVersion: rbac.authorization.k8s.io/v1
  kind: ClusterRoleBinding
  metadata:
    name: healthz-access
  roleRef:
    apiGroup: rbac.authorization.k8s.io
    kind: ClusterRole
    name: healthz-access
  subjects:
  - kind: Group
    name: system:unauthenticated
    apiGroup: rbac.authorization.k8s.io
  ```

---

### **4. Network Policy or Firewall Blocking Loopback Requests**
- **Problem:** Network policies or host firewalls might block the API server’s internal loopback requests to itself (e.g., when running self-health checks).
- **Fix:**  
  - Allow traffic to `localhost`/`127.0.0.1` on the API server port (default: `6443`).
  - Check network policies affecting the control plane nodes.

---

### **5. Corrupted or Missing Service Account Tokens**
- **Problem:** If the API server relies on a service account token for internal communication (rare), a missing or invalid token could cause `401` errors.
- **Fix:**  
  - Verify the service account token mount in the API server pod:
    ```yaml
    spec:
      containers:
      - name: kube-apiserver
        volumeMounts:
        - name: kube-api-access-xxxxx
          mountPath: /var/run/secrets/kubernetes.io/serviceaccount
    ```
  - Ensure the token exists and is valid.

---

### **6. Reverse Proxy or Load Balancer Interference**
- **Problem:** A proxy/load balancer (e.g., NGINX, HAProxy) in front of the API server might require authentication, even for health checks.
- **Fix:**  
  Configure the proxy to exclude `/livez`, `/readyz`, and `/healthz` from authentication.

---

### **Troubleshooting Steps**
1. **Test the endpoint manually** (from the API server node):
   ```bash
   curl -k https://localhost:6443/livez
   ```
   If it returns `401`, the issue is local to the API server configuration.  
   If it succeeds, the problem lies in external probes (e.g., kubelet, monitoring tools).

2. **Check API server logs** for authentication failures:
   ```bash
   journalctl -u kube-apiserver | grep -i "unauthorized"
   ```

3. **Verify API server flags**:
   ```bash
   ps aux | grep kube-apiserver | grep -E 'anonymous-auth|enable-admission-plugins'
   ```

---

### **Summary**
The `401` error on the `livez` check is almost always caused by **disabled anonymous authentication** or **overly restrictive RBAC policies**. Start by ensuring `--anonymous-auth=true` and that RBAC allows access to the health endpoints. If the issue persists, audit admission controllers and network policies.
