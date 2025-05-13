To enable Kubernetes audit logging and configure threat detection, follow these organized steps, considering both self-managed and managed clusters:

### **1. Enable Kubernetes Audit Logging**

#### **Self-Managed Clusters**:
- **Create an Audit Policy** (e.g., `audit-policy.yaml`):
  ```yaml
  apiVersion: audit.k8s.io/v1
  kind: Policy
  rules:
    - level: Metadata  # Log metadata for all requests
      omitStages: ["RequestReceived"]  # Exclude the initial request stage
    - level: RequestResponse  # Log full details for sensitive operations
      resources:
        - group: ""  # Core API group
          resources: ["secrets", "configmaps"]
      users: ["system:serviceaccount:kube-system:anonymous"]
  ```
  - **Levels**: `None`, `Metadata`, `Request`, `RequestResponse`.
  - Customize rules to log critical actions (e.g., secrets access, admin operations).

- **Configure kube-apiserver**:
  Add these flags to the API server manifest (`/etc/kubernetes/manifests/kube-apiserver.yaml`):
  ```yaml
  - --audit-policy-file=/etc/kubernetes/audit-policy.yaml
  - --audit-log-path=/var/log/kubernetes/audit.log
  - --audit-log-maxage=30   # Retain logs for 30 days
  - --audit-log-maxbackup=5  # Keep 5 backup logs
  - --audit-log-maxsize=100  # Rotate after 100 MB
  ```
  - Mount the audit policy and log directory into the API server container.

- **Restart kube-apiserver**:
  The API server will reload automatically if running in a static Pod.

#### **Managed Clusters** (EKS, GKE, AKS):
- **AWS EKS**:
  - Enable audit logs via the EKS control plane logging settings (AWS Console/CLI). Ensure `audit` logs are sent to CloudWatch Logs in a **US region** (e.g., `us-east-1`).
  ```bash
  aws eks update-cluster-config \
    --region us-east-1 \
    --name <cluster-name> \
    --logging '{"clusterLogging":[{"types":["audit"],"enabled":true}]}'
  ```

- **GKE**:
  - Audit logs are enabled by default under _Cloud Audit Logs_ (Admin Activity and Data Access logs). Confirm they are routed to a **US region bucket** in BigQuery or Log Analytics.

- **Azure AKS**:
  - Enable diagnostic settings to stream `kube-audit` logs to Azure Monitor/Log Analytics in a **US region**.

---

### **2. Configure Log Storage & Retention**
- **Centralized Storage**:
  - Use cloud-native solutions (e.g., AWS CloudWatch, GCP Cloud Logging, Azure Monitor) with retention policies (e.g., 1 year for compliance).
  - For on-prem/hybrid, use Elasticsearch, Splunk, or Grafana Loki.

- **Data Residency (US)**:
  - Ensure logs are stored in US regions (e.g., AWS `us-east-1`, GCP `us-central1`, Azure `eastus`).

---

### **3. Set Up Threat Detection**
- **Runtime Threat Detection**:
  - **Falco**: Deploy to detect anomalous container behavior (e.g., shell in a container, sensitive mounts).
    ```yaml
    helm repo add falcosecurity https://falcosecurity.github.io/charts
    helm install falco falcosecurity/falco
    ```

- **SIEM Integration**:
  - Forward logs to Splunk, Sumo Logic, or Datadog. Use AWS GuardDuty (for EKS) or GCP Security Command Center for managed services.

- **Alerting Rules**:
  - Example alerts:
    - Unauthorized access (e.g., `user: anonymous`).
    - Privilege escalation (e.g., `verb: escalate` on `roles`).
    - Sensitive resource access (e.g., `secrets` in `kube-system`).
  - Use Prometheus Alertmanager or cloud-native alerting (e.g., AWS CloudWatch Alarms).

---

### **4. Compliance & Monitoring**
- **Regular Audits**:
  - Use tools like `kube-bench` (CIS Benchmark checks) or `kube-hunter` (penetration testing).

- **Dashboards**:
  - Build Grafana dashboards to track API request rates, error codes, and user activity.

---

### **5. Example Workflow for EKS**
1. **Enable Audit Logging**:
   ```bash
   aws eks update-cluster-config --name my-cluster --logging '{"clusterLogging":[{"types":["audit"],"enabled":true}]}'
   ```
2. **Analyze in CloudWatch**:
   - Create Metric Filters for patterns like `"userAgent":"kubectl" AND "responseStatus.code":403`.
3. **GuardDuty for EKS**:
   - Enable GuardDuty in AWS to detect compromised credentials or unusual API calls.

---

### **Troubleshooting Tips**
- **Log Volume**: Start with `Metadata` level to avoid performance issues.
- **Access Control**: Restrict log access using IAM roles or RBAC.
- **Validation**: Test policies with `kube-apiserver` dry-run flags.

By following these steps, you’ll enable comprehensive audit logging and threat detection tailored to US compliance needs.

### ** --------------- kubespray configuration ------------------ **

Yes, **Kubespray** (the popular open-source tool for deploying production-ready Kubernetes clusters) supports configuring Kubernetes audit logging out of the box, and you can extend it to integrate threat detection tools like Falco. Below is a breakdown of how to achieve this with the latest Kubespray version (as of 2023):

---

### **1. Enabling Kubernetes Audit Logging with Kubespray**
Kubespray allows you to configure audit logging by customizing the `kube-apiserver` settings through Ansible variables.

#### **Step 1: Define the Audit Policy**
Create an audit policy file (e.g., `audit-policy.yaml`) and configure Kubespray to use it. Example policy:
```yaml
# File: audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: Metadata
    omitStages: ["RequestReceived"]
  - level: RequestResponse
    resources:
      - group: ""
        resources: ["secrets", "configmaps"]
    users: ["system:serviceaccount:kube-system:anonymous"]
```

#### **Step 2: Configure Kubespray Variables**
In your Kubespray inventory directory (e.g., `inventory/mycluster/group_vars/k8s_cluster`), set the following variables:
```yaml
# Enable audit logging
kube_audit_enabled: true

# Path to your audit policy file (host machine path)
kube_audit_policy_file: "/path/to/audit-policy.yaml"

# Configure audit log backend (file or webhook)
kube_audit_log_enabled: true
kube_audit_log_path: "/var/log/kubernetes/audit.log"
kube_audit_log_maxage: 30
kube_audit_log_maxbackup: 5
kube_audit_log_maxsize: 100

# Mount audit policy/log directory to the API server
kube_apiserver_extra_volumes:
  - name: audit-log
    hostPath: /var/log/kubernetes
    mountPath: /var/log/kubernetes
    readOnly: false
  - name: audit-policy
    hostPath: "{{ kube_audit_policy_file }}"
    mountPath: /etc/kubernetes/audit-policy.yaml
    readOnly: true
```

#### **Step 3: Deploy the Cluster**
Run the Kubespray playbook to apply the configuration:
```bash
ansible-playbook -i inventory/mycluster/hosts.yaml cluster.yml
```

#### **Result**:
- The `kube-apiserver` will log audit events to `/var/log/kubernetes/audit.log`.
- Logs are rotated based on `maxage`, `maxbackup`, and `maxsize`.

---

### **2. Threat Detection with Kubespray**
Kubespray does **not** include threat detection tools like Falco by default, but you can integrate them using Ansible roles or Helm.

#### **Option 1: Deploy Falco with Helm**
Add Falco to your cluster post-deployment using Helm:
```yaml
# Add Falco Helm chart
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco
```

#### **Option 2: Custom Ansible Role**
Create a custom Ansible role in Kubespray to deploy Falco:
```yaml
# Example task in roles/falco/tasks/main.yml
- name: Install Falco
  helm:
    chart_ref: falcosecurity/falco
    release_name: falco
    namespace: falco
    create_namespace: true
```

---

### **3. Log Storage & Threat Detection Integration**
Kubespray does **not** handle log aggregation or SIEM integration directly, but you can extend it:
1. **Forward Logs to a SIEM**:
   - Use `filebeat` or `fluentd` DaemonSets to ship logs to Elasticsearch, Splunk, or AWS CloudWatch.
   - Example role: [Elasticsearch Filebeat role](https://github.com/elastic/ansible-filebeat).

2. **Enable Alerts**:
   - Integrate Prometheus/Grafana with Falco alerts ([docs](https://falco.org/docs/alerts/)).

---

### **4. Verify Configuration**
After deployment:
1. Check audit logs:
   ```bash
   tail -f /var/log/kubernetes/audit.log
   ```
2. Validate Falco detection:
   ```bash
   kubectl logs -l app=falco -n falco
   ```

---

### **Key Notes**
- **Kubespray Version**: Ensure you’re using Kubespray **v2.23+** (audit logging support is stable since v2.18).
- **Performance**: Audit logging can generate large volumes of data. Start with `Metadata` level and adjust rules as needed.
- **Compliance**: For US data residency, ensure logs are stored in US-based storage (e.g., S3 buckets in `us-east-1`).

---

### **Troubleshooting**
- If the `kube-apiserver` fails to start, check:
  - Permissions for the audit log directory (`/var/log/kubernetes`).
  - Syntax errors in the audit policy file.
- Use `kubectl describe pod kube-apiserver-<node>` for error details.

By following these steps, Kubespray can fully support Kubernetes audit logging and be extended for threat detection. For managed clusters (EKS/GKE/AKS), use cloud-native audit logging instead.
