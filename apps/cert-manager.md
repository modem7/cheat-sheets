# Cert-Manager
Cert-manager adds certificates and certificate issuers as resource types in **Kubernetes ([[kubernetes]])** clusters, and simplifies the process of obtaining, renewing and using those certificates.

Documentation & Project Homepage: [Cert-Manager Docs](https://cert-manager.io/docs/)

---
## Install
```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set crds.enabled=true
```
See [[helm]]. Older chart versions use `--set installCRDs=true` instead of `crds.enabled`. Without Helm, apply the release manifest `cert-manager.yaml` from the GitHub releases page with [[kubectl]].

```bash
kubectl -n cert-manager get pods
```

---
## Let's Encrypt (ACME)
Start with the **staging** server (`https://acme-staging-v02.api.letsencrypt.org/directory`) to avoid rate limits, then switch to production.

### HTTP-01 (Ingress)
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: you@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    solvers:
      - http01:
          ingress:
            ingressClassName: traefik
```
Use `ingressClassName: nginx` for ingress-nginx. Port 80 must be reachable from the internet. See [[traefik]] and [[nginx]].

### DNS-01 (Cloudflare Example)
Needed for wildcard certificates and for hosts that are not reachable from the internet.
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cloudflare-api-token
  namespace: cert-manager
type: Opaque
stringData:
  api-token: <CLOUDFLARE_API_TOKEN>
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-dns
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: you@example.com
    privateKeySecretRef:
      name: letsencrypt-dns-account-key
    solvers:
      - dns01:
          cloudflare:
            apiTokenSecretRef:
              name: cloudflare-api-token
              key: api-token
        selector:
          dnsZones:
            - example.com
```
The Cloudflare token needs `Zone:DNS:Edit` and `Zone:Zone:Read`. Other providers (Route 53, DigitalOcean, Google, Azure and more) are listed in the cert-manager docs.

### Request a Certificate
Either annotate an Ingress:
```yaml
metadata:
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - app.example.com
      secretName: app-example-com-tls
```
Or create a `Certificate` directly:
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: app-example-com
  namespace: default
spec:
  secretName: app-example-com-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - app.example.com
```

## Self-Signed Certificates

1. Create a self-signed CA ([[ssl-certs]]) creating a ca.key (private key) and ca.crt (certificate)

(ca.key)
```bash
openssl genrsa -out ca.key 4096
```

(ca.crt)
```bash
openssl req -new -x509 -sha256 -days 365 -key ca.key -out ca.crt
```

2. Create the TLS secret directly from the files (no manual base64 needed)

```bash
kubectl create secret tls ssl-issuer-secret --cert=ca.crt --key=ca.key -n cert-manager
```
The secret must live in the namespace cert-manager uses for cluster resources (`cert-manager` by default) when used by a `ClusterIssuer`. A namespaced `Issuer` reads it from its own namespace.

3. Create a new ClusterIssuer or Issuer object by using the secret

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-issuer
spec:
  ca:
    secretName: ssl-issuer-secret
```

For a quick throwaway issuer with no CA, use `spec: { selfSigned: {} }` instead.

## Useful Commands
COMMAND | DESCRIPTION
---|---
`kubectl get clusterissuer,issuer -A` | List issuers and their Ready state
`kubectl get certificate -A` | List certificates and Ready state
`kubectl describe certificate <NAME>` | Show events and renewal time
`kubectl get certificaterequest,order,challenge -A` | Follow an issuance through its stages
`kubectl describe challenge <NAME>` | See why an ACME challenge is stuck
`kubectl -n cert-manager logs deploy/cert-manager` | Controller logs
`cmctl status certificate <NAME>` | Detailed status (needs the `cmctl` CLI)
`cmctl renew <NAME>` | Force a renewal
`kubectl get secret <SECRET> -o jsonpath='{.data.tls\.crt}' \| base64 -d \| openssl x509 -noout -dates -subject` | Check the issued certificate

## Troubleshooting

### Common Errors

**DNS Record not yet propagated**
The error, `Waiting for DNS-01 challenge propagation: DNS record for "your-dns-record" not yet propagated.`, might occur in the `challenge` object. Cert-Manager creates a TXT record on the DNS provider and checks that the record exists before issuing the certificate. In a split-DNS environment this can fail when internal DNS servers can't resolve the TXT record on the cloud DNS. Use the controller `extraArgs` `--dns01-recursive-nameservers-only` and `--dns01-recursive-nameservers=8.8.8.8:53,1.1.1.1:53` to set the resolvers used for the challenge.

**No solver found**
The error, `Failed to determine a valid solver configuration for the set of domains on the Order: no configured challenge solvers can be used for this challenge` might occur in the `order` object when no solver matches the DNS hostname. Make sure your solvers have a correct `dnsZones` configured that matches the hostname's zone.

**HTTP-01 challenge stays pending**
Check that port 80 is reachable from outside, that the DNS name points at the ingress, and that no redirect or auth rule blocks `/.well-known/acme-challenge/`.

**Rate limited by Let's Encrypt**
Switch the issuer to the staging server while testing.
