**OpenSearch OSS vs Elasticsearch OSS: Key Differences**

1. **Origin and Governance:**
   - **Elasticsearch OSS:** Developed by Elastic, originally under Apache 2.0. Post-2021, new features are under the SSPL (not OSI-approved), but the core remains Apache 2.0.
   - **OpenSearch OSS:** Forked from Elasticsearch 7.10.2 by AWS, maintained by a community under Apache 2.0. Aims to stay fully open-source.

2. **Licensing:**
   - Both core engines are Apache 2.0, but **Elasticsearch**'s newer features (post-7.x) are SSPL-licensed, limiting their use in OSS distributions.
   - **OpenSearch** guarantees all features remain under Apache 2.0, avoiding SSPL restrictions.

3. **Features:**
   - **OpenSearch OSS:** Includes features Elastic formerly restricted to commercial licenses (e.g., security plugins, alerting, anomaly detection) as open source.
   - **Elasticsearch OSS:** Lacks advanced features now under SSPL (e.g., advanced security, machine learning). Focuses on core search/analytics.

4. **Versioning and Compatibility:**
   - **Elasticsearch OSS:** Now at 8.x, with breaking API changes. Older clients/tools may require updates.
   - **OpenSearch OSS:** Starts at 1.x (based on Elasticsearch 7.10.2) and evolves independently. Maintains backward compatibility with Elasticsearch 7.x APIs.

5. **Ecosystem:**
   - **Elasticsearch:** Integrates with Elastic's commercial stack (e.g., Kibana under SSPL, Observability, SIEM).
   - **OpenSearch:** Includes open-source OpenSearch Dashboards (Kibana fork) and prioritizes AWS integration (e.g., AWS Cognito, CloudWatch).

6. **Community and Support:**
   - **Elasticsearch:** Backed by Elastic with commercial support. Development driven by Elastic’s roadmap.
   - **OpenSearch:** Community-driven with AWS backing. Prioritizes transparency and community contributions.

7. **Use Cases:**
   - **Choose Elasticsearch OSS** if you need the latest core improvements and can navigate SSPL limitations.
   - **Choose OpenSearch OSS** for open-source advanced features (security, alerting), AWS integration, or to avoid SSPL.

**Summary Table:**

| Aspect                | Elasticsearch OSS                          | OpenSearch OSS                              |
|-----------------------|--------------------------------------------|---------------------------------------------|
| **License**           | Apache 2.0 (core), SSPL for new features   | Apache 2.0 (entire project)                 |
| **Advanced Features** | Limited (SSPL features excluded)           | Included (security, ML, alerting)           |
| **Version Base**      | Current (8.x+)                             | Forked from Elasticsearch 7.10.2, now 2.x   |
| **Ecosystem**         | Elastic’s commercial tools (SSPL)          | AWS integration, open-source Dashboards     |
| **Governance**        | Elastic-led                                | Community-driven with AWS support           |
| **Best For**          | Latest core features, Elastic ecosystem    | Open-source compliance, AWS users, security | 

**Decision Guide:**
- **Prioritize open-source ethos?** → OpenSearch.
- **Need advanced features without pay?** → OpenSearch.
- **Rely on Elastic’s latest innovations?** → Elasticsearch OSS (with SSPL awareness).
- **AWS environment?** → OpenSearch for seamless integration.
Both **Fluent Bit** and **Fluentd** support logging to Elasticsearch OSS and OpenSearch OSS, but there are key differences in compatibility, configuration, and feature support due to the divergence between the two projects. Here’s a breakdown:

---

### **1. Elasticsearch OSS Support**
#### **Fluentd**:
- **Plugin**: Uses the [`out_elasticsearch`](https://github.com/uken/fluent-plugin-elasticsearch) plugin to ship logs to Elasticsearch.
- **Compatibility**:
  - Works with Elasticsearch OSS **7.x and older** (Apache 2.0 licensed versions).
  - For **Elasticsearch 8.x**, compatibility depends on the plugin version. Newer Elasticsearch OSS versions (under SSPL) may require updates to the plugin or configuration tweaks (e.g., SSL/TLS settings, API compatibility headers).
- **Authentication**:
  - Supports basic auth, API keys, and TLS/SSL.
  - Advanced security features (e.g., role-based access control) require Elasticsearch’s commercial license or OpenSearch’s open-source security.

#### **Fluent Bit**:
- **Output Plugin**: Uses the **Elasticsearch output plugin** (`es`).
- **Compatibility**:
  - Works with Elasticsearch OSS 7.x and 8.x, but newer Elasticsearch versions may require:
    - Explicit `api_key` or `http_user`/`http_passwd` configuration.
    - `tls` settings for HTTPS.
    - `suppress_type_name on` (for Elasticsearch 8.x, which removes document types).
- **Limitations**:
  - Features like machine learning or advanced security require Elastic’s commercial stack (X-Pack).

---

### **2. OpenSearch OSS Support**
#### **Fluentd**:
- **Plugin**: Use the [`out_opensearch`](https://github.com/fluent/fluent-plugin-opensearch) plugin (a fork of `out_elasticsearch` tailored for OpenSearch).
- **Compatibility**:
  - Designed for OpenSearch 1.x/2.x (forked from Elasticsearch 7.10.2).
  - Handles OpenSearch-specific API changes (e.g., security endpoints, index management).
- **Authentication**:
  - Supports Sigv4 signing for AWS OpenSearch Serverless/IAM roles.
  - TLS/SSL and basic auth work out-of-the-box (OpenSearch’s security plugin is open-source).

#### **Fluent Bit**:
- **Native Support**: Added OpenSearch output in **v1.8.0** ([official docs](https://docs.fluentbit.io/manual/pipeline/outputs/opensearch)).
- **Configuration**:
  - Use the `opensearch` output plugin (not `es`).
  - Example:
    ```ini
    [OUTPUT]
        Name          opensearch
        Match         *
        Host          opensearch-host
        Port          9200
        Index         my_index
        AWS_Region    us-west-2
        AWS_Auth      On
        tls           On
    ```
- **Features**:
  - Supports Sigv4 authentication for AWS-managed OpenSearch clusters.
  - TLS/SSL and OpenSearch’s native security (e.g., fine-grained access control).

---

### **Key Differences & Considerations**
| Aspect                  | Elasticsearch OSS                         | OpenSearch OSS                             |
|-------------------------|-------------------------------------------|--------------------------------------------|
| **Fluentd Plugin**      | `out_elasticsearch`                       | `out_opensearch` (forked, optimized)       |
| **Fluent Bit Plugin**   | `es` output plugin                        | `opensearch` output plugin (native)        |
| **Security**            | Limited in OSS (needs commercial license) | Built-in open-source security (e.g., RBAC) |
| **AWS Integration**     | Manual Sigv4 setup                        | Native Sigv4 support in plugins            |
| **Version Compatibility** | Issues with Elasticsearch 8.x+          | Aligns with OpenSearch 1.x/2.x APIs        |

---

### **4. Common Issues & Fixes**
- **Elasticsearch 8.x Compatibility**:
  - Add `suppress_type_name on` in Fluent Bit/Fluentd to avoid type-related errors.
  - Use `api_key` instead of basic auth if Elasticsearch 8.x is configured with API keys.
- **OpenSearch TLS Errors**:
  - Ensure the `tls` option is enabled and the CA certificate is correctly configured.
- **AWS Sigv4 Authentication**:
  - For AWS OpenSearch Serverless, use `AWS_Region`, `AWS_Auth`, and `AWS_Service os` (for Serverless) in Fluent Bit.

---

### **5. Which Should You Use?**
- **Elasticsearch OSS**:
  - If you’re tied to Elastic’s ecosystem or need the latest non-SSPL core features.
  - Requires workarounds for newer versions (8.x).
- **OpenSearch OSS**:
  - Better for open-source compliance, AWS users, or needing built-in security/alerting.
  - Smoother integration with Fluent Bit/Fluentd (dedicated plugins).

---

### **Summary**

### **1. Suggested Prometheus Configurations**

| **Setup**      | **Targets** | **CPU** | **Memory** | **Disk(PVC)**    |
|----------------|-------------|---------|------------|------------------|
| **Dev**        | 10–20       | 1 core  | 2 GB       | 20 GB            |
| **Test/Prod**  | 100–200     | 2 cores | 4–8 GB     | 100–200 GB       |

### **2. Suggested Configurations for grafana-sc-dashboard and grafana-sc-datasources**

| **Container**      | **CPU** | **Memory** | **Disk(PVC)**    |
|--------------------|---------|---------|------------|------------------|
| **grafana**        | 1 core  | 2 GB       | 20 GB            |

- **Fluent Bit**: Prefer the `opensearch` output plugin for OpenSearch and the `es` plugin for Elasticsearch OSS (with version tweaks).
- **Fluentd**: Use `out_opensearch` for OpenSearch and `out_elasticsearch` for Elasticsearch OSS.
- **OpenSearch** is more straightforward for AWS users and open-source purists, while **Elasticsearch OSS** requires caution with newer SSPL-licensed versions.

Here's a summarized table for the resource configurations:

Component	CPU Requests	CPU Limits	Memory Requests	Memory Limits	Storage
Prometheus	1–2 cores	2–4 cores	4–8 GiB	8–16 GiB	50–200 GiB (Persistent)
Grafana	0.5 cores	1–2 cores	512 MiB	2–4 GiB	10–20 GiB (or external DB)
Grafana-sc-datasource	0.05–0.1 cores	0.1–0.2 cores	64–128 MiB	128–256 MiB	N/A
Grafana-sc-dashboard	0.05–0.1 cores	0.1–0.2 cores	64–128 MiB	128–256 MiB	N/A

