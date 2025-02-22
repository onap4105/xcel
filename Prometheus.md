Here's a summarized table for the resource configurations:

| **Component**               | **CPU Requests** | **CPU Limits** | **Memory Requests** | **Memory Limits** | **Storage**               |
|------------------------------|------------------|----------------|---------------------|-------------------|---------------------------|
| **Prometheus**               |   2 cores        |   4 cores      |   8 GiB             |   16 GiB          | 100–200 GiB (Persistent)  |
| **Grafana**                  |   1 cores        |   2 cores      |   2 GIB             |    4 GiB          | 10–20 GiB (or external DB)|
| **Grafana-sc-datasource**    |   0.1 cores      |   0.2 cores    |   128 MiB           |   256 MiB         | N/A                       |
| **Grafana-sc-dashboard**     |   0.1 cores      |   0.2 cores    |   128 MiB           |   256 MiB         | N/A                       |

---
When determining resource requirements for a Prometheus container (exposing port `9090` for its web interface), consider the following guidelines, which depend on the scale of your monitoring setup:

---

### **1. Key Factors Influencing Resource Usage**
- **Scrape Targets**: Number of services/endpoints being monitored.
- **Scrape Interval**: How frequently metrics are collected (e.g., 15s vs. 1m).
- **Metrics Volume**: Number of time series/metrics per target.
- **Retention Period**: How long data is stored (default: 15 days).
- **Query Load**: Frequency and complexity of queries/dashboards/alerting rules.

---

### **2. Resource Estimates**

#### **A. CPU**
- **Small Setup** (10–50 targets, 15s scrape interval):  
  - **1–2 Cores** (sustained usage, spikes during rule evaluations or queries).
- **Medium Setup** (50–500 targets):  
  - **2–4 Cores**.
- **Large Setup** (500+ targets, high churn/metrics):  
  - **4+ Cores** (scale horizontally with sharding or use Thanos/Cortex for very large deployments).

#### **B. Memory (RAM)**
- **Baseline**: ~1–3 GB (idle with minimal metrics).
- **Small Setup**: 2–4 GB.
- **Medium Setup**: 4–8 GB.
- **Large Setup**: 16+ GB (or higher for millions of time series).  
  **Formula**: Roughly `number_of_series * 2KB` (e.g., 500k series ≈ 1GB RAM).

#### **C. Disk**
- **Storage Calculation**:  
  `disk_space = ingestion_rate (samples/sec) * bytes_per_sample * retention_period_seconds`  
  - **Bytes per sample**: ~1–3 bytes (compressed via Prometheus' TSDB).  
  - **Example**:  
    - 100k samples/sec * 3 bytes * 15 days ≈ **~388 GB**.
- **Recommendations**:  
  - **Small**: 50–100 GB (SSD recommended).  
  - **Medium**: 100–500 GB.  
  - **Large**: 1+ TB (with provisions for growth).  
  - Use persistent volumes and monitor disk usage to avoid full disks.

#### **D. Network**
- Minimal for small setups, but ensure sufficient bandwidth for:  
  - Scraping metrics from targets.  
  - Remote write/read operations (if using remote storage).

---

### **3. Example Configurations**

| **Setup** | **Targets** | **CPU** | **Memory** | **Disk**         | **Network**       |
|-----------|-------------|---------|------------|------------------|-------------------|
| **Dev**   | 10–20       | 1 core  | 2 GB       | 20 GB (SSD)      | Low               |
| **Prod**  | 100–200     | 2 cores | 4–8 GB     | 100–200 GB (SSD) | Moderate          |
| **Large** | 500+        | 4+ cores| 16+ GB     | 1 TB+ (SSD)      | High bandwidth    |

---

### **4. Best Practices**
- **Start Small**: Begin with 2 CPU, 4 GB RAM, and 50 GB disk, then scale based on usage.
- **Monitor Prometheus Itself**: Track `container_memory_usage_bytes`, `process_cpu_seconds_total`, and `prometheus_tsdb_storage_blocks_bytes`.
- **Optimize**:  
  - Increase scrape intervals (e.g., 30s instead of 15s).  
  - Drop unused metrics with `metric_relabel_configs`.  
  - Limit retention period or use remote storage (e.g., Thanos, Cortex).  
- **Persist Data**: Use a persistent volume for `/prometheus` directory.
- **High Availability**: Run two Prometheus instances with the same configuration for redundancy.

---

### **5. Troubleshooting**
- **OOM Kills**: Increase memory limits if Prometheus is killed due to high usage.  
- **High CPU**: Check query load and optimize alerting rules.  
- **Disk Full**: Extend storage or reduce retention time.  

Adjust these estimates based on your actual metrics ingestion rate and query patterns. Always test under load!


To determine the number of scrape targets being monitored by Prometheus, you can use the following methods:

---

### **1. Check the Prometheus Web UI**
Prometheus exposes its web interface on port `9090` by default. Navigate to:
```
http://<prometheus-server>:9090/targets
```
This page lists **all configured scrape targets** and their status (`UP` or `DOWN`).  
You can manually count the targets here or use the UI to filter by job/service.

---

### **2. Use Prometheus Metrics**
Prometheus itself exposes metrics about its targets. Query these metrics in the Prometheus expression browser (`http://<prometheus-server>:9090/graph`):

#### **A. Total Targets**
```promql
count(up)
```
This returns the total number of scrape targets that Prometheus is configured to monitor (including both `UP` and `DOWN` targets).

#### **B. Healthy Targets**
```promql
sum(up)
```
This returns the number of targets currently in the `UP` state.

#### **C. Targets by Job**
```promql
count by (job) (up)
```
This breaks down the number of targets per configured `job` in your `prometheus.yml`.

---

### **3. Check Prometheus Configuration File**
Inspect your `prometheus.yml` configuration file to see how targets are defined:
- **Static Targets**: Defined directly under `static_configs`.
- **Dynamic Targets**: Discovered via service discovery (e.g., Kubernetes, Consul, EC2, etc.).

Example:
```yaml
scrape_configs:
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node1:9100', 'node2:9100']  # 2 static targets
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:  # Dynamic targets from Kubernetes
      - role: pod
```

---

### **4. Use the Prometheus API**
Query the Prometheus API programmatically to list all targets:
```bash
curl http://<prometheus-server>:9090/api/v1/targets
```
The response includes a JSON list of all targets and their metadata (e.g., `labels`, `health`, `scrape_url`).

---

### **5. Check Service Discovery Status**
If you’re using **service discovery** (e.g., Kubernetes, Consul), check the Service Discovery page in the Prometheus UI:
```
http://<prometheus-server>:9090/service-discovery
```
This shows discovered targets grouped by service discovery mechanism.

---

### **6. Use `promtool`**
The `promtool` CLI (bundled with Prometheus) can inspect your configuration file and validate targets:
```bash
promtool check config prometheus.yml
```

---

### **7. Key Metrics to Monitor**
Track these metrics to understand your target landscape over time:
- `prometheus_sd_discovered_targets`: Number of discovered targets per service discovery mechanism.
- `up`: Health status of each target (`1` = healthy, `0` = unhealthy).
- `scrape_samples_scraped`: Number of samples scraped per target.

---

### **Example Workflow**
1. **Web UI**: Quickly check `Targets` page for a visual overview.
2. **Metrics**: Use `count(up)` to get the total number of targets.
3. **API/Configuration**: Cross-reference with your `prometheus.yml` to ensure no misconfigurations.
4. **Service Discovery**: Verify dynamic targets (e.g., Kubernetes pods) are being discovered correctly.

---

### **Automation Tip**
Use a dashboard (e.g., Grafana) to visualize the number of targets and their health over time. Example queries:
- Total targets: `count(up)`
- Unhealthy targets: `count(up == 0)`

---

### **Common Pitfalls**
- **Double-Counting**: Ensure service discovery isn’t overlapping with static targets.
- **Inactive Targets**: Clean up old/unused targets in your configuration or service discovery.
- **Reloads**: After updating `prometheus.yml`, reload Prometheus with `curl -X POST http://localhost:9090/-/reload`.

By combining these methods, you’ll have full visibility into your monitored scrape targets and their status.
