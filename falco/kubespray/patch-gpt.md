You're correct — in **Kubespray v2.27.0**, there is **no built-in support** for `kube_apiserver_extra_args` or `kube_apiserver_extra_volumes`. This means we **must modify the Kubespray Ansible roles directly or extend them** to inject the necessary config into `kube-apiserver.yaml`.

Here’s how to do it **reliably** and cleanly, without breaking future upgrades:

---

## ✅ Strategy

1. **Use `patches` to modify the `kube-apiserver.yaml` manifest post-deployment**.
2. **Pre-create `/etc/kubernetes/webhook-config.yaml` using a custom playbook.**
3. **Trigger the patch after control plane setup but before cluster health checks.**

---

## 🧩 Step-by-Step: Modify `kube-apiserver.yaml` After It's Generated

### ✅ 1. **Create a Custom Post-Task Hook for Patching**

Create a custom playbook file:
`inventory/mycluster/custom/falco_apiserver_patch.yml`

```yaml
---
- name: Patch kube-apiserver manifest with Falco audit webhook
  hosts: kube_control_plane
  become: yes
  tasks:

    - name: Ensure webhook config exists
      copy:
        dest: /etc/kubernetes/webhook-config.yaml
        content: |
          apiVersion: v1
          kind: Config
          clusters:
            - name: falco-webhook
              cluster:
                server: http://<idns>:31007/k8s-audit
                insecure-skip-tls-verify: true
          users:
            - name: falco-webhook
          contexts:
            - context:
                cluster: falco-webhook
                user: falco-webhook
              name: falco-webhook
          current-context: falco-webhook

    - name: Patch kube-apiserver manifest for Falco audit webhook
      replace:
        path: /etc/kubernetes/manifests/kube-apiserver.yaml
        regexp: '((?:\s*)- --advertise-address=.*)'
        replace: |
          \1
          \1\n\1- --audit-webhook-config-file=/etc/kubernetes/webhook-config.yaml
          \1- --audit-webhook-batch-max-wait=10ms
          \1- --audit-webhook-initial-backoff=10ms

    - name: Add volumeMount for webhook-config
      blockinfile:
        path: /etc/kubernetes/manifests/kube-apiserver.yaml
        marker: "# {mark} FALCO_WEBHOOK_VOLUME_MOUNT"
        insertafter: 'volumeMounts:'
        block: |
          - mountPath: /etc/kubernetes/webhook-config.yaml
            name: webhook-config
            readOnly: true

    - name: Add volume for webhook-config
      blockinfile:
        path: /etc/kubernetes/manifests/kube-apiserver.yaml
        marker: "# {mark} FALCO_WEBHOOK_VOLUME"
        insertafter: 'volumes:'
        block: |
          - hostPath:
              path: /etc/kubernetes/webhook-config.yaml
              type: File
            name: webhook-config
```

Replace `<idns>` with the actual internal DNS name or IP where Falco will be reachable.

---

### ✅ 2. **Include the Patch in Your Kubespray Execution**

In your `inventory/mycluster/hosts.yml` or playbook:

```yaml
extra_playbooks:
  - inventory/mycluster/custom/falco_apiserver_patch.yml
```

Alternatively, add it to your Kubespray command:

```bash
ansible-playbook -i inventory/mycluster/hosts.yaml \
  cluster.yml \
  -e "@inventory/mycluster/group_vars/k8s_cluster/k8s-cluster.yml" \
  -e extra_playbooks='["inventory/mycluster/custom/falco_apiserver_patch.yml"]'
```

---

## 🔁 Optional: Use `lineinfile` or `yq` (for cleaner YAML)

If you want cleaner logic (especially for YAML parsing), you could also:

* Use `yq` to manipulate the manifest as a proper YAML file.
* Or build a custom Ansible module to generate the full file.

---

## ✅ Summary

* Kubespray v2.27.0 doesn’t have `kube_apiserver_extra_args/volumes`.
* You should **patch the kube-apiserver manifest after it’s generated**, using a custom Ansible playbook.
* This patch injects both the Falco webhook flags and volume mount.

---

Would you like me to generate the full ready-to-use custom Ansible patch playbook file for your project?
