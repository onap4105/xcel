The metric `node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate` is typically a recording rule that needs to be set up in your Prometheus configuration. If it's not showing any values, here's a step-by-step guide to troubleshoot:

---

### 1. **Verify the Metric Exists**
   Check if the metric exists in Prometheus:
   ```promql
   node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate
   ```
   - Go to **Prometheus UI → Graph** and run this query.
   - If it returns "no data", the metric is either not being collected or the recording rules are missing.

---

### 2. **Check Recording Rules**
   This metric is usually defined via a recording rule in the `kube-prometheus-stack` Helm chart. Ensure the rule is properly configured in your Prometheus rules:

   ```yaml
   groups:
     - name: node-namespace-pod-container.rules
       rules:
         - record: node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate
           expr: |
             sum by (cluster, namespace, pod, container) (
               irate(container_cpu_usage_seconds_total{job="kubelet", metrics_path="/metrics/cadvisor"}[5m])
             )
   ```
   - Ensure the rule is enabled in your Helm values:
     ```yaml
     prometheus:
       prometheusSpec:
         ruleSelectorNilUsesHelmValues: false
     ```

---

### 3. **Verify Underlying Metrics**
   The recording rule depends on `container_cpu_usage_seconds_total`. Check if this base metric exists:
   ```promql
   container_cpu_usage_seconds_total
   ```
   - If this returns no data, your Prometheus isn't scraping kubelet/cAdvisor metrics correctly.

---

### 4. **Check Service Discovery**
   Ensure Prometheus is scraping the **kubelet** and **kube-state-metrics** endpoints:
   - In Prometheus UI, go to **Status → Targets**.
   - Look for targets with jobs `kubelet` and `kube-state-metrics`.

---

### 5. **Adjust Label Selectors**
   If your environment doesn't have a `cluster` label (common in single-cluster setups), modify the query to exclude it:
   ```promql
   sum(node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{namespace="$namespace", pod="$pod"}) by (container)
   ```

---

### 6. **Check Time Range**
   Ensure you’re not querying a time range where no data exists. Try widening the time range in Grafana.

---

### 7. **Verify Permissions**
   Ensure Prometheus has permissions to scrape kubelet metrics:
   ```yaml
   # In your Helm values
   prometheus:
     kubelet:
       enabled: true
     serviceAccount:
       create: true
       name: prometheus
   ```

---

### 8. **Check Network Policies**
   If you’re using network policies, ensure Prometheus can access the kubelet and kube-state-metrics endpoints.

---

### Example Debug Queries
1. Check raw CPU usage:
   ```promql
   container_cpu_usage_seconds_total{namespace="$namespace", pod="$pod"}
   ```
2. Check kube-state-metrics resource requests:
   ```promql
   kube_pod_container_resource_requests{namespace="$namespace", pod="$pod", resource="cpu"}
   ```

---

If you still see no data, share:
- Output of `kubectl get pods -n monitoring` (to verify components),
- Screenshot of Prometheus targets,
- Relevant excerpts from Prometheus logs (`kubectl logs <prometheus-pod>`).


    ## If true, a nil or {} value for prometheus.prometheusSpec.ruleSelector will cause the
    ## prometheus resource to be created with selectors based on values in the helm deployment,
    ## which will also match the PrometheusRule resources created
    ##
    ruleSelectorNilUsesHelmValues: true



