# SOPS and age
SOPS encrypts the *values* of YAML, JSON, ENV and INI files while leaving keys readable, so secrets can live in Git and still produce sensible diffs. `age` is the small, modern file-encryption tool SOPS uses for keys (simpler than [[gpg]]). Typical homelab use: encrypted `.env` files for [[docker-compose]] and encrypted Kubernetes Secrets for Flux or Argo CD ([[kubernetes]], [[argocd]]).

Documentation: [SOPS](https://getsops.io/docs/) · [age](https://github.com/FiloSottile/age)

## Install
```bash
sudo apt install age                      # Ubuntu 22.04+ / Debian 12+
brew install sops age                     # macOS
# sops: download the .deb / binary from https://github.com/getsops/sops/releases
```

## age Keys
COMMAND | DESCRIPTION
---|---
`age-keygen -o key.txt` | Generate a key pair (the public key is printed and stored as a comment in the file)
`age-keygen -y key.txt` | Print the public key (`age1...`) of an existing key file
`age -r <PUBKEY> -o file.age file` | Encrypt a file to a recipient
`age -R recipients.txt -o file.age file` | Encrypt to every key in a file
`age -d -i key.txt file.age > file` | Decrypt
`age -p -o file.age file` | Encrypt with a passphrase

Store the private key where SOPS looks by default and lock it down:
```bash
mkdir -p ~/.config/sops/age
age-keygen -o ~/.config/sops/age/keys.txt
chmod 600 ~/.config/sops/age/keys.txt
```
Back the private key up in a password manager ([[bitwarden]]). If it is lost, every file encrypted only to it is unrecoverable.

## Environment Variables
VARIABLE | DESCRIPTION
---|---
`SOPS_AGE_KEY_FILE` | Path to the age private key file (default `~/.config/sops/age/keys.txt`)
`SOPS_AGE_KEY` | The private key itself (handy in CI)
`SOPS_AGE_RECIPIENTS` | Recipients used when encrypting without a `.sops.yaml`

## Configuration (.sops.yaml)
Put this at the repo root so `sops` picks the right keys by path. The first matching rule wins.
```yaml
creation_rules:
  - path_regex: ^kubernetes/.*\.sops\.ya?ml$
    encrypted_regex: ^(data|stringData)$      # only encrypt these top-level keys
    age: <PUBKEY_LAPTOP>,<PUBKEY_CLUSTER>
  - path_regex: \.env\.sops$
    age: <PUBKEY_LAPTOP>
  - path_regex: secrets/.*
    age: <PUBKEY_LAPTOP>
```
Multiple recipients are comma-separated: any one of the matching private keys can decrypt.

## SOPS Commands
COMMAND | DESCRIPTION
---|---
`sops encrypt secrets.yaml > secrets.sops.yaml` | Encrypt using `.sops.yaml` rules
`sops encrypt -i secrets.yaml` | Encrypt in place
`sops decrypt secrets.sops.yaml` | Print plaintext to stdout
`sops decrypt -i secrets.sops.yaml` | Decrypt in place (don't commit the result)
`sops edit secrets.sops.yaml` | Decrypt into `$EDITOR`, re-encrypt on save
`sops --encrypt --age <PUBKEY> file.yaml` | Encrypt with an explicit recipient
`sops --encrypted-regex '^(data\|stringData)$' -e -i secret.yaml` | Encrypt only matching keys
`sops decrypt --extract '["db"]["password"]' secrets.sops.yaml` | Print a single value
`sops set secrets.sops.yaml '["db"]["password"]' '"<VALUE>"'` | Set a value without opening an editor
`sops updatekeys secrets.sops.yaml` | Apply the current `.sops.yaml` recipients (add/remove keys)
`sops rotate -i secrets.sops.yaml` | Generate a new data key and re-encrypt
`sops --input-type dotenv --output-type dotenv -d file.env` | Force format for odd file names
`sops exec-env secrets.sops.yaml '<CMD>'` | Run a command with the values as environment variables
`sops exec-file secrets.sops.yaml '<CMD> {}'` | Run a command with a temporary decrypted file (`{}`)

Older versions use `sops -e` / `sops -d`; both spellings work.

## Docker Compose .env
```bash
sops encrypt --input-type dotenv --output-type dotenv .env > .env.sops
git add .env.sops && echo .env >> .gitignore

# deploy: decrypt only into the process environment
sops exec-env .env.sops 'docker compose up -d'
# or write the file temporarily
sops decrypt --input-type dotenv --output-type dotenv .env.sops > .env
```

## Kubernetes with Flux
Create the key secret in the cluster, then tell the Kustomization to decrypt.
```bash
kubectl -n flux-system create secret generic sops-age \
  --from-file=age.agekey=$HOME/.config/sops/age/keys.txt
```
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 10m
  path: ./apps
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
  decryption:
    provider: sops
    secretRef:
      name: sops-age
```
Argo CD has no native SOPS support; use a plugin such as KSOPS or helm-secrets.

## Git Integration
```bash
# show a readable diff of encrypted files
git config diff.sops.textconv "sops decrypt"
echo '*.sops.yaml diff=sops' >> .gitattributes
```
Pair with [[secret-scanning]] so an accidentally committed plaintext copy is caught.

## Troubleshooting
SYMPTOM | FIX
---|---
`no identity matched any of the recipients` / `Failed to get the data key` | The private key isn't found. Set `SOPS_AGE_KEY_FILE` or check the file matches a recipient in the file's `sops:` block
`config file not found, or has no creation rules` | Run from the repo (or a subfolder) with `.sops.yaml`, or pass `--config`; check `path_regex` matches the *path you give sops*
Whole file encrypted, including `metadata.name` | Add `encrypted_regex` so Kubernetes metadata stays readable
`MAC mismatch` | The encrypted file was edited by hand. Restore from Git; always use `sops edit`
Removed a colleague's key but they can still decrypt | `sops updatekeys` only affects future data keys of that file; run `sops rotate -i` and rotate the secrets themselves
Wrong format on `.env` files | Add `--input-type dotenv --output-type dotenv`
