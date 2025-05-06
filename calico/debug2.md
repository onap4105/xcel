To resolve the version skew and properly upgrade your Kubernetes cluster, follow these steps:

### 1. **Immediate Action: Fix `kubectl` Version Skew**
Downgrade your `kubectl` client to a version within the supported skew (±1 minor version from the server):
```bash
# Example: Install kubectl v1.29.x to match Server v1.28.6
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable-1.29.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
```

---

### 2. **Verify Cluster State**
Check component versions and node status:
```bash
kubectl get nodes -o wide  # Check kubelet versions on nodes
kubectl get pods -n kube-system  # Inspect control plane pods (apiserver, controller-manager, etcd)
```

---

### 3. **Proper Upgrade Path with Kubespray**
Upgrade one minor version at a time using `upgrade.yml`:

#### Step 1: Upgrade from 1.28.6 → 1.29.x
- Edit `inventory/mycluster/group_vars/k8s_cluster/k8s-cluster.yml`:
  ```yaml
  kube_version: v1.29.10
  ```
- Run the upgrade playbook:
  ```bash
  ansible-playbook -i inventory/mycluster/hosts.yml upgrade.yml \
    -b -v --tags=upgrade
  ```

#### Step 2: Upgrade from 1.29.x → 1.30.x
- Update `k8s-cluster.yml` to `v1.30.4`
- Run `upgrade.yml` again.

#### Step 3: Upgrade from 1.30.x → 1.31.4
- Update `k8s-cluster.yml` to `v1.31.4`
- Run `upgrade.yml` again.

---

### 4. **Post-Upgrade Checks**
- Verify all control plane components and nodes are upgraded:
  ```bash
  kubectl get nodes  # All should show v1.31.4
  kubectl get pods -n kube-system -l tier=control-plane
  ```
- Validate cluster health:
  ```bash
  kubectl get componentstatuses
  kubectl describe pod -n kube-system <apiserver-pod>
  ```

---

### 5. **If Upgrade Fails**
- **Rollback**: Restore from an etcd backup (if taken before upgrade).
- **Debug**: Check Ansible logs for failed tasks:
  ```bash
  grep -i 'failed=' ansible.log
  ```

---

### 6. **Re-Install Correct `kubectl`**
After successful server upgrade to v1.31.4:
```bash
curl -LO "https://dl.k8s.io/release/v1.31.4/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

---

### Key Notes:
- **Why `upgrade.yml`?** It ensures rolling updates, handles etcd upgrades, and preserves configurations.
- **Avoid `cluster.yml` for Upgrades**: It may reset cluster state or skip critical upgrade steps.
- **Version Skew Policy**: Always maintain client/server versions within ±1 minor version.

By following this process, you’ll align your cluster with Kubernetes’ supported upgrade path and eliminate version skew issues.
