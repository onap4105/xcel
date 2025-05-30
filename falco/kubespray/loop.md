Here’s how you can loop over a list of Falco-related flags using `with_items` (or `loop`) in your Ansible task:

---

### ✅ **Ansible Task with Loop**

```yaml
- name: Insert Falco webhook config lines
  lineinfile:
    path: /etc/kubernetes/manifests/kube-apiserver.yaml
    line: "{{ item }}"
    insertafter: '^ {4}- kube-apiserver$'
  loop:
    - "    - --audit-webhook-config-file=/etc/kubernetes/webhook-config.yaml"
    - "    - --audit-webhook-batch-max-wait=10ms"
    - "    - --audit-webhook-initial-backoff=10ms"
```

---

### ✅ Key Notes:

* Each `item` already includes the **4 spaces** to match the surrounding YAML indentation.
* `insertafter` targets the line: `    - kube-apiserver`
* Each line will be inserted immediately **after** that line, preserving order.

---

### 🔁 Bonus: Using `with_items` (equivalent in older syntax)

```yaml
with_items:
  - "    - --audit-webhook-config-file=/etc/kubernetes/webhook-config.yaml"
  - "    - --audit-webhook-batch-max-wait=10ms"
  - "    - --audit-webhook-initial-backoff=10ms"
```

But `loop` is preferred in newer Ansible versions.

Let me know if you also want a loop for volume mounts or volume definitions.
