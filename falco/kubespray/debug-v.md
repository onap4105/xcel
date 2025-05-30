Thanks — since manual indentation inside `blockinfile` isn't being preserved as expected, you’re likely hitting an Ansible quirk where YAML interprets indentation based on the Ansible file’s indentation (not just the string block). Let's make sure it works **consistently**, using a workaround that ensures correct indentation.

---

### ✅ **Recommended Fix Using `blockinfile` with Exact Indentation**

Use the YAML `|` block with \*\*each line manually indented with **exact spaces**, including spaces before the `- name`, not within the block itself:

```yaml
- hosts: kube_control_plane
  tasks:
    - name: Add Falco audit webhook volume
      blockinfile:
        path: /etc/kubernetes/manifests/kube-apiserver.yaml
        marker: "# {mark} FALCO AUDIT VOLUME"
        insertafter: '^  volumes:'
        block: |
          - name: falco-webhook-config
            hostPath:
              path: /etc/kubernetes/falco/webhook-config.yaml
              type: File
```

**BUT!** Because Ansible itself adds indentation based on where the `block:` is declared in the playbook YAML, **you must left-align `block:` in the playbook to prevent extra indentation**.

To force indentation control, **use `ansible.builtin.template` instead.** Here's how:

---

### ✅ **Alternative: Use `template` module for predictable formatting**

1. **Create a Jinja2 template file**, `falco_volume_block.yml.j2`:

```yaml
# BEGIN FALCO AUDIT VOLUME
    - name: falco-webhook-config
      hostPath:
        path: /etc/kubernetes/falco/webhook-config.yaml
        type: File
# END FALCO AUDIT VOLUME
```

2. **Use `blockinfile` with `lookup('file', ...)` to insert it**:

```yaml
- hosts: kube_control_plane
  tasks:
    - name: Add Falco audit webhook volume
      blockinfile:
        path: /etc/kubernetes/manifests/kube-apiserver.yaml
        marker: "# {mark} FALCO AUDIT VOLUME"
        insertafter: '^  volumes:'
        block: "{{ lookup('file', 'falco_volume_block.yml.j2') }}"
```

This way, you maintain **full control of indentation** in the `.j2` file, unaffected by Ansible’s YAML parser.

---

### ✅ Final Tip: Double-Check Regex Match

Make sure `insertafter: '^  volumes:'` matches **exactly** — it's two spaces before `volumes:`. Adjust as needed (`^volumes:` or `^ {2}volumes:`) based on your YAML.

---

Would you like me to help you generate both volume and mount changes with matching templates in a fully idempotent task block?
