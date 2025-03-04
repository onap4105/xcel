Here’s a summary of **API changes, deprecations, and other notable updates** between Kubernetes **v1.28.6** and **v1.31.4**, covering versions **1.29**, **1.30**, and **1.31**:

---

### **Removed APIs (No Longer Available in 1.29–1.31)**  
These APIs were deprecated in earlier versions and **fully removed** in subsequent releases. Ensure your manifests/tools no longer rely on them:

| API Group/Version                     | Resource/Endpoint | Removed In | Replacement (Stable API) |
|---------------------------------------|-------------------|------------|--------------------------|
| `admissionregistration.k8s.io/v1beta1` | `ValidatingAdmissionPolicy` | 1.29 | `admissionregistration.k8s.io/v1` |
| `autoscaling/v2beta2`                 | `HorizontalPodAutoscaler` | 1.29 | `autoscaling/v2` |
| `discovery.k8s.io/v1beta1`            | `EndpointSlice` | 1.29 | `discovery.k8s.io/v1` |
| `flowcontrol.apiserver.k8s.io/v1beta1`| `FlowSchema`, `PriorityLevelConfiguration` | 1.29 | `flowcontrol.apiserver.k8s.io/v1` |
| `networking.k8s.io/v1beta1`           | `Ingress`, `IngressClass` | 1.29 | `networking.k8s.io/v1` |
| `storage.k8s.io/v1beta1`              | `CSIDriver`, `CSINode`, `VolumeAttachment` | 1.29 | `storage.k8s.io/v1` |
| `metrics.k8s.io/v1beta1`              | `PodMetrics`, `NodeMetrics` | 1.31 | `metrics.k8s.io/v1` |

---

### **Newly Deprecated APIs (Still Available in 1.31 but Planned for Removal)**  
These APIs are marked deprecated in 1.29–1.31 and will be removed in future releases (e.g., 1.32+):

| API Group/Version                     | Resource/Endpoint | Replacement |
|---------------------------------------|-------------------|-------------|
| `policy/v1beta1`                      | `PodDisruptionBudget` | `policy/v1` |
| `authentication.k8s.io/v1beta1`       | `TokenReview` | `authentication.k8s.io/v1` |
| `authorization.k8s.io/v1beta1`        | `SubjectAccessReview` | `authorization.k8s.io/v1` |
| `rbac.authorization.k8s.io/v1beta1`   | `ClusterRole`, `Role` | `rbac.authorization.k8s.io/v1` |
| `certificates.k8s.io/v1beta1`         | `CertificateSigningRequest` | `certificates.k8s.io/v1` |

---

### **Other Major Changes**  
#### **1. Features Removed**  
- **Dynamic Kubelet Configuration**: Removed in 1.29 (use `kubeadm` or static configs).  
- **Legacy In-Tree Cloud Providers**:  
  - OpenStack and vSphere in-tree providers removed in 1.29 (use out-of-tree CSI drivers).  
  - CephFS and GlusterFS in-tree volume plugins deprecated in 1.31 (planned removal in 1.34).  

#### **2. Feature Promotions to Stable**  
- **Sidecar Containers (1.30)**: Sidecars can now restart independently of the main pod.  
- **Node Swap Support (1.30)**: Swap memory support for nodes is stable (requires `NodeSwap` feature gate).  
- **Pod Lifecycle Updates (1.30)**: New `PodReadyToStartContainers` condition to track initialization.  
- **CronJob Time Zones (1.31)**: Time zone support for `CronJob` is stable.  

#### **3. Security & Default Changes**  
- **Seccomp by Default (1.30)**: Seccomp profiles are now enabled by default for all workloads.  
- **ServiceAccount Token Improvements (1.31)**: Bound tokens and improved rotation logic.  

#### **4. Tooling & Dependencies**  
- **Go Version**: Kubernetes 1.31 requires Go 1.21+ for building components.  
- **Kubernetes Go Client**: Versions older than `v0.28.0` may not work with 1.31 APIs.  
- **Helm Chart Compatibility**: Ensure Helm v3.10+ for compatibility with newer APIs.  

---

### **Action Items for Upgrading to 1.31**  
1. **Update Manifests**:  
   - Replace `metrics.k8s.io/v1beta1` → `v1` for metrics collection.  
   - Migrate `policy/v1beta1` → `policy/v1` for `PodDisruptionBudget`.  
   - Use stable RBAC (`rbac.authorization.k8s.io/v1`) for roles/cluster roles.  
2. **Cluster Components**:  
   - Upgrade CSI drivers, CNI plugins, and Ingress controllers to versions compatible with 1.31.  
3. **Deprecation Scans**:  
   - Use tools like `kubent` (kube-no-trouble) or `kube-apiserver` audit logs to detect deprecated APIs.  
4. **Test Workloads**:  
   - Validate critical workloads with new API versions and security defaults (e.g., Seccomp).  

---

### **Key Resources**  
- [Kubernetes Deprecation Guide](https://kubernetes.io/docs/reference/using-api/deprecation-guide/)  
- [1.31 Release Notes](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.31.md)  
- [Kubent Tool](https://github.com/doitintl/kube-no-trouble) (to detect deprecated APIs).  

Always test upgrades in a non-production environment first!
