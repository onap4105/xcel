Here's a concise command to list all NodePort services and their exposed ports in a Kubernetes cluster:

```bash
kubectl get services --all-namespaces -o jsonpath='{range .items[?(@.spec.type=="NodePort")]}{.metadata.name}{" - "}{.spec.ports[*].nodePort}{"\n"}{end}'
```

**Sample Output:**
```
my-web-service - 32080
api-gateway - 31000 31001
```

For a more detailed view with namespace information:
```bash
kubectl get services --all-namespaces -o jsonpath='{range .items[?(@.spec.type=="NodePort")]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{.spec.ports[*].nodePort}{"\n"}{end}' | column -t
```

**Sample Output:**
```
default    my-web-service  32080
production api-gateway     31000 31001
```

### Explanation:
1. `--all-namespaces`: Searches across all namespaces
2. `?(@.spec.type=="NodePort")`: Filters services with type NodePort
3. `{.spec.ports[*].nodePort}`: Extracts all nodePort values
4. `column -t`: Formats output in aligned columns

### Alternative using JSON processing (jq):
```bash
kubectl get services -A -o json | jq -r '.items[] | select(.spec.type=="NodePort") | "\(.metadata.namespace)\t\(.metadata.name)\t\(.spec.ports[] | .nodePort)"'
```

### To see all ports including service details:
```bash
kubectl get svc -A -o custom-columns='NAMESPACE:.metadata.namespace,NAME:.metadata.name,TYPE:.spec.type,PORTS:.spec.ports[*].nodePort'
```

**Notes:**
- NodePorts are always in the range 30000-32767 by default
- Services can expose multiple ports (shown as space-separated values)
- ClusterIP services won't appear in this list
- LoadBalancer services will also show their NodePorts

This gives you a complete list of all NodePorts currently in use across your cluster.
