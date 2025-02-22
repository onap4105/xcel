For **Grafana**, **grafana-sc-dashboard** (Sidecar for dashboards), and **grafana-sc-datasource** (Sidecar for datasources) in Kubernetes, the resource requirements vary based on their roles. Here's a breakdown:

---

### **1. `grafana` (Main Container)**
Handles dashboards, queries, and user interactions. Use the recommendations from the previous answer, adjusted for your workload:
```yaml
resources:
  requests:
    cpu: "500m"    # Adjust based on query/alert load
    memory: "1Gi"  # Increase for complex dashboards
  limits:
    cpu: "2000m"   # Avoid aggressive throttling
    memory: "2Gi"  # Prevent OOM crashes
```

---

### **2. `grafana-sc-datasource` (Datasource Sidecar)**
- **Purpose**: Syncs datasource configurations (e.g., Prometheus, Loki) from ConfigMaps/Secrets.
- **Resource Needs**: Minimal since it runs once or periodically.
```yaml
resources:
  requests:
    cpu: "50m"     # Very low CPU
    memory: "64Mi"  # Minimal memory
  limits:
    cpu: "100m"
    memory: "128Mi"
```

---

### **3. `grafana-sc-dashboard` (Dashboard Sidecar)**
- **Purpose**: Syncs dashboard JSON files from ConfigMaps/Volumes.
- **Resource Needs**: Slightly higher than the datasource sidecar if dashboards are large or frequently updated.
```yaml
resources:
  requests:
    cpu: "100m"     # Low CPU
    memory: "128Mi"  # Enough for JSON parsing
  limits:
    cpu: "200m"
    memory: "256Mi"
```

---

### **Full Example (Helm Chart `values.yaml`)**
```yaml
grafana:
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 2Gi

  sidecar:
    datasources:
      resources:
        requests:
          cpu: 50m
          memory: 64Mi
        limits:
          cpu: 100m
          memory: 128Mi
    dashboards:
      resources:
        requests:
          cpu: 100m
          memory: 128Mi
        limits:
          cpu: 200m
          memory: 256Mi
```

---

### **Key Notes**
1. **Sidecars Are Lightweight**:
   - Both `grafana-sc-datasource` and `grafana-sc-dashboard` are sidecars that run briefly at startup or on config changes. They don’t handle user traffic, so keep their resources minimal.

2. **Adjust Based on Workload**:
   - Increase `grafana` memory if dashboards use heavy queries (e.g., large Prometheus ranges).
   - If dashboards are updated constantly, raise the sidecar CPU limits slightly.

3. **Scaling**:
   - For HA, run multiple `grafana` replicas with `podAntiAffinity`.
   - Sidecars don’t need replicas (they’re per-pod helpers).

4. **Monitoring**:
   - Alert on Grafana container OOMs or CPU throttling.
   - Use `kubectl top pods` to track real-world usage.

---

### **Why These Values?**
- **Sidecars**: Designed to run short-lived tasks (e.g., config syncing). Overprovisioning wastes cluster resources.
- **Grafana Main Container**: Memory is critical for caching dashboards and query results. CPU spikes during rendering/alerts.

Always validate with staging environments and adjust based on metrics!
