Since you **don’t have access to all namespaces**, you cannot retrieve NodePort services directly via `kubectl`. However, if your goal is to **detect which NodePort ports are in use cluster-wide**, there’s a workaround:

---

### ✅ **Alternative Approach: Scan NodePorts from Node Network**

You can **scan all Kubernetes nodes** for listening NodePort ports from a privileged pod. This detects **used NodePorts** regardless of namespace or access rights.

---

### 🛠️ Step-by-Step Solution

#### 1. **Run a privileged pod** on a node (with `hostNetwork: true` and tools like `netstat`, `ss`, or `nmap`):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: port-scanner
  namespace: default
spec:
  containers:
  - name: scanner
    image: nicolaka/netshoot  # has netstat, ss, nmap, etc.
    command: ["sleep", "3600"]
    securityContext:
      privileged: true
  hostNetwork: true
  restartPolicy: Never
```

Save as `port-scanner.yaml`, then run:

```bash
kubectl apply -f port-scanner.yaml
```

---

#### 2. **Exec into the pod and scan for NodePort range (default 30000–32767)**:

```bash
kubectl exec -it port-scanner -- bash
```

Then run:

```bash
# Option 1: using netstat
netstat -tuln | awk '$4 ~ /30000|32767/ {print $4}'

# Option 2: using ss
ss -tuln | grep ':3'

# Option 3: using nmap (most comprehensive)
nmap -p 30000-32767 127.0.0.1
```

---

### 📌 Why This Works

* **NodePorts are exposed on every node**, so a privileged pod with `hostNetwork: true` can see open ports even if you can't access their Kubernetes service definitions.
* Works **without namespace permissions**.

---

Would you like a script to automate this check or parse the results into a cleaner list?
