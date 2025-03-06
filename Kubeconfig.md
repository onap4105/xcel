To protect Kubernetes configuration files in `/etc/kubernetes` from unauthorized changes, follow these security best practices:

---

### **1. **File System Permissions and Ownership**
Ensure strict permissions on files and directories:
```bash
# Set ownership to root (or a dedicated system user)
sudo chown -R root:root /etc/kubernetes

# Restrict permissions (read-only for non-root users)
sudo chmod -R 600 /etc/kubernetes  # Files
sudo chmod -R 700 /etc/kubernetes/manifests  # Directories (if applicable)
```

- Use **immutable flags** to prevent accidental or malicious modifications:
  ```bash
  sudo chattr +i /etc/kubernetes/*.conf  # Make files immutable (even root can't modify)
  sudo chattr +i /etc/kubernetes/manifests/*.yaml  # Protect static Pod definitions
  ```
  To modify later, temporarily remove the flag with `chattr -i`.

---

### **2. **Kubelet Configuration**
The `kubelet` manages static Pods in `/etc/kubernetes/manifests`. Secure its config:
- Restrict permissions for `/var/lib/kubelet/config.yaml`:
  ```bash
  sudo chmod 600 /var/lib/kubelet/config.yaml
  ```
- Use the `--read-only-port=0` flag in the kubelet service to disable the read-only API port.

---

### **3. **Kubernetes RBAC**
Limit access to cluster resources:
- Use **Role-Based Access Control (RBAC)** to restrict users/service accounts from modifying critical resources:
  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: ClusterRole
  metadata:
    name: restricted-access
  rules:
  - apiGroups: [""]
    resources: ["nodes", "secrets", "pods"]
    verbs: ["get", "list", "watch"]  # Deny "create", "update", "delete"
  ```

---

### **4. **AppArmor/SELinux**
Enforce mandatory access control (MAC):
- **AppArmor**: Create a profile to restrict write access to `/etc/kubernetes`:
  ```bash
  # Example profile: /etc/apparmor.d/kubernetes-protect
  /etc/kubernetes/** r,
  ```
- **SELinux**: Apply a policy to prevent unauthorized processes from modifying files:
  ```bash
  sudo semanage fcontext -a -t etc_t "/etc/kubernetes(/.*)?"
  sudo restorecon -Rv /etc/kubernetes
  ```

---

### **5. **Encryption at Rest**
Encrypt sensitive files (e.g., certificates, kubeconfigs):
- Use **Linux Unified Key Setup (LUKS)** for disk encryption.
- For Kubernetes Secrets, enable [Encryption at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/).

---

### **6. **Host Hardening**
Secure the underlying host:
- Regularly update the OS and Kubernetes components.
- Use **firewalls** (e.g., `ufw`, `iptables`) to block unauthorized access to control plane ports.
- Restrict SSH access to administrative users only (use SSH keys instead of passwords).
- Disable unnecessary services on control plane nodes.

---

### **7. **Audit Logging**
Monitor changes to `/etc/kubernetes`:
- Use **auditd** to track file modifications:
  ```bash
  sudo auditctl -w /etc/kubernetes -p wa -k kubernetes-config
  ```
- Deploy **Falco** or **Sysdig** to alert on unauthorized changes.

---

### **8. **GitOps and Version Control**
Store configurations in a Git repository:
- Use tools like **Argo CD** or **Flux** to enforce declarative management.
- Require pull requests (PRs) and peer reviews for changes to Kubernetes manifests.

---

### **9. **Immutable Infrastructure**
Treat nodes as immutable:
- Use **Container-Optimized OS** (e.g., Flatcar, Talos Linux) where the filesystem is read-only by default.
- Rebuild nodes instead of modifying them directly.

---

### **10. **Network Security**
Isolate control plane nodes:
- Place them in a private subnet with no direct internet access.
- Use a **bastion host** or VPN for administrative access.

---

### **11. **Service Account Restrictions**
Avoid mounting service account tokens unnecessarily:
- Disable automatic mounting in Pod specs:
  ```yaml
  automountServiceAccountToken: false
  ```
- Restrict service account permissions using RBAC.

---

### **12. **Backup and Recovery**
Regularly back up `/etc/kubernetes`:
```bash
# Example backup script
tar -czvf /backup/kubernetes-config-$(date +%F).tar.gz /etc/kubernetes
```
Use tools like **Velero** for cluster-wide backups.

---

### **Common Pitfalls to Avoid**
- Avoid running workloads on control plane nodes.
- Never share kubeconfig files with broad permissions.
- Rotate certificates and keys periodically (use `kubeadm certs renew`).

--- 

By combining **filesystem protections**, **RBAC**, **host hardening**, and **auditing**, you can significantly reduce the risk of unauthorized changes to Kubernetes configurations. Start with immutable flags and strict permissions, then layer on RBAC and monitoring for defense-in-depth.
