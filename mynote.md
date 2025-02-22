Here's a summarized table for the resource configurations:

| **Component**               | **CPU Requests** | **CPU Limits** | **Memory Requests** | **Memory Limits** | **Storage**               |
|------------------------------|------------------|----------------|---------------------|-------------------|---------------------------|
| **Prometheus**               | 1–2 cores        | 2–4 cores      | 4–8 GiB             | 8–16 GiB          | 50–200 GiB (Persistent)   |
| **Grafana**                  | 0.5 cores        | 1–2 cores      | 512 MiB             | 2–4 GiB           | 10–20 GiB (or external DB)|
| **Grafana-sc-datasource**    | 0.05–0.1 cores   | 0.1–0.2 cores  | 64–128 MiB          | 128–256 MiB       | N/A                       |
| **Grafana-sc-dashboard**     | 0.05–0.1 cores   | 0.1–0.2 cores  | 64–128 MiB          | 128–256 MiB       | N/A                       |

---
