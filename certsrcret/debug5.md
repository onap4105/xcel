To find and verify the `serviceaccounts/token` permissions tied to the `ClusterRole` you provided, follow these steps:

---

### **1. Identify the Service Account**
The `ClusterRole` you shared (`ndcu-vault-csi-provider-clusterrole`) grants permission to **create tokens for service accounts** (`serviceaccounts/token`). This is typically used by the Vault CSI provider to generate tokens for pods to authenticate with Vault using the Kubernetes auth method.

First, identify the **ServiceAccount** associated with this role. Based on the metadata, this ClusterRole is part of a Helm release named `ndcu-vault` in the `ndcu-vault` namespace. The likely ServiceAccount is:

```yaml
# Example ServiceAccount (adjust based on your actual setup)
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ndcu-vault-csi-provider
  namespace: ndcu-vault
```

---

### **2. Verify ServiceAccount Token Permissions**
#### **Step 1: Check the ClusterRoleBinding**
Ensure a `ClusterRoleBinding` links the `ClusterRole` (`ndcu-vault-csi-provider-clusterrole`) to the ServiceAccount (`ndcu-vault-csi-provider`):

```bash
kubectl get clusterrolebinding -l app.kubernetes.io/name=vault-csi-provider
```

Example output:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ndcu-vault-csi-provider-clusterrolebinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: ndcu-vault-csi-provider-clusterrole
subjects:
- kind: ServiceAccount
  name: ndcu-vault-csi-provider
  namespace: ndcu-vault
```

#### **Step 2: Verify Token Creation Permissions**
The `ClusterRole` allows creating tokens for ServiceAccounts via the `serviceaccounts/token` resource. To test if the ServiceAccount can create tokens:

```bash
# Replace <POD_SERVICE_ACCOUNT> with the actual ServiceAccount name (e.g., `ndcu-vault-csi-provider`)
kubectl auth can-i create token --namespace=ndcu-vault --as=system:serviceaccount:ndcu-vault:ndcu-vault-csi-provider
```

If successful, this returns `yes`.

---

### **3. Find the ServiceAccount Token**
#### **Option 1: List Tokens for the ServiceAccount**
Tokens for a ServiceAccount are stored as Kubernetes Secrets. List them with:

```bash
kubectl get serviceaccount ndcu-vault-csi-provider -n ndcu-vault -o jsonpath='{.secrets[*].name}'
```

Example output:
```plaintext
ndcu-vault-csi-provider-token-abc12
```

#### **Option 2: Manually Create a Token**
If no token exists (common in Kubernetes 1.24+ where tokens are not auto-generated), create one:

```bash
kubectl create token ndcu-vault-csi-provider -n ndcu-vault --duration=8760h
```

This generates a token with a 1-year expiry. Use it for authentication (e.g., with Vault).

---

### **4. Verify the Token’s Permissions**
Decode the token to verify its audience and claims (replace `<TOKEN>` with the actual token):

```bash
kubectl get secret ndcu-vault-csi-provider-token-abc12 -n ndcu-vault -o jsonpath='{.data.token}' | base64 -d
```

Use a JWT decoder (e.g., [jwt.io](https://jwt.io)) to inspect the token’s payload. Ensure:
- The `aud` (audience) matches your Vault Kubernetes auth configuration (e.g., `vault`).
- The `sub` (subject) includes the ServiceAccount’s identity:
  ```
  system:serviceaccount:ndcu-vault:ndcu-vault-csi-provider
  ```

---

### **5. Test Token Authentication to Vault**
Use the token to authenticate with Vault’s Kubernetes auth method:

```bash
# Replace <TOKEN> with the ServiceAccount token
curl -k -X POST \
  https://ndcu-vault.ndcu-vault:8200/v1/auth/kubernetes/login \
  -d '{"role": "prometheus-read-role", "jwt": "<TOKEN>"}'
```

If successful, Vault returns a client token with policies linked to the role.

---

### **Troubleshooting**
- **Permission Denied**: Ensure the `ClusterRoleBinding` exists and links to the correct ServiceAccount.
- **Invalid Token**: Regenerate the token if it’s expired or misconfigured.
- **Vault Authentication Failure**: Verify the Vault role (`prometheus-read-role`) exists and is bound to the ServiceAccount.

Let me know if you need further help! 🔍
