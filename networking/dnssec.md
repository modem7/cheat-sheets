# DNSSEC
DNSSEC signs DNS data so a validating resolver can prove an answer is genuine and unmodified. This sheet covers signing a zone with BIND (`dnssec-policy` with inline signing, or manual `dnssec-keygen` and `dnssec-signzone`), publishing the DS record, and checking and troubleshooting with `dig` and `delv`.

Documentation: [BIND 9 DNSSEC Guide](https://bind9.readthedocs.io/en/latest/dnssec-guide.html) · [BIND 9 manual pages](https://bind9.readthedocs.io/en/latest/manpages.html)
Project: [BIND 9 at ISC](https://www.isc.org/bind/)

Verification: BIND tools and `rndc` output checked against BIND 9.18.39 (Ubuntu 24.04 package) in a throwaway container, including a signed `example.com` test zone. Other versions may differ. Not exercised (taken from `--help` output only, unverified): `rndc dnssec -checkds` with `-key`/`-when`, `rndc dnssec -rollover`, `rndc nta`, `rndc loadkeys`, `rndc sign`, `dnssec-cds`, and `delv -a` with a custom anchor file.

## Concepts
TERM | MEANING
---|---
DNSKEY | Public key published in the zone
RRSIG | Signature over a record set, made with a DNSKEY
KSK | Key signing key: signs the DNSKEY set; its hash is the DS record
ZSK | Zone signing key: signs the rest of the zone; rolled more often
DS | Delegation signer: hash of the child KSK, published in the parent zone (via your registrar)
NSEC / NSEC3 | Signed proof that a name or type does not exist; NSEC3 hides the zone's names
CDS / CDNSKEY | Child-published copies of DS and DNSKEY so the parent can update the DS automatically
Trust anchor | Key a validator trusts without a DS, normally the root KSK
Chain of trust | Root DS, then TLD DS, then your DS, then your DNSKEY, then your records
`ad` flag | Authenticated Data: the resolver validated the answer
`cd` flag | Checking Disabled: the client asks the resolver not to validate
SERVFAIL | What a validating resolver returns for bogus (failed) data

## Sign a Zone with dnssec-policy
The recommended method on BIND 9.16 and later (checked on 9.18): BIND generates and rolls keys and re-signs the zone itself. Use `inline-signing yes` to keep the unsigned zone file as it is.

```text
options {
    directory "/var/cache/bind";
    key-directory "/var/cache/bind/keys";
    recursion no;
};

dnssec-policy "homelab" {
    keys {
        ksk lifetime unlimited algorithm ecdsap256sha256;
        zsk lifetime 60d algorithm ecdsap256sha256;
    };
    dnskey-ttl 300;
    signatures-validity 14d;
    nsec3param iterations 0 optout no salt-length 0;
};

zone "example.com" {
    type primary;
    file "zones/example.com.db";
    dnssec-policy "homelab";
    inline-signing yes;
};
```

STEP | COMMAND
---|---
Check syntax and zones | `named-checkconf -z`
Reload | `rndc reconfig` (new or changed zone and policy config) or `rndc reload`
Show key and rollover state | `rndc dnssec -status example.com`
Get the DS record to give the registrar | `dig @<SERVER_IP> example.com DNSKEY \| dnssec-dsfromkey -f - example.com`
Tell BIND the parent has the DS | `rndc dnssec -checkds published example.com`

OPTION | DESCRIPTION
---|---
`dnssec-policy default;` | Use the built-in policy instead of defining your own
`dnssec-policy insecure;` | Built-in policy that unsigns a zone (use while removing DNSSEC)
`dnssec-policy none;` | Built-in policy that disables DNSSEC maintenance for the zone
`key-directory` | Where BIND stores `K*.key`, `K*.private` and `K*.state` files
`inline-signing yes;` | Sign a separate copy; the file you edit stays unsigned
`lifetime unlimited` | Never roll that key automatically (typical for the KSK)

The signed copy of an inline-signed zone is stored as `<ZONEFILE>.signed` in a raw binary format, not text. Zone-file tools such as `dnssec-dsfromkey -f` cannot read it, so get the DS from a `dig` query as above.

## Sign a Zone Manually
Offline signing with the key tools. You re-sign before the signatures expire (default validity is 30 days) and bump the SOA serial each time.

```bash
cd /etc/bind/zones
dnssec-keygen -a ECDSAP256SHA256 -n ZONE -f KSK example.com
dnssec-keygen -a ECDSAP256SHA256 -n ZONE example.com
dnssec-signzone -S -o example.com -N unixtime -x example.com.db
named-checkzone -i full example.com example.com.db.signed
```

The two `dnssec-keygen` runs print the key names (`Kexample.com.+013+<KEYTAG>`). With `-S` (smart signing) `dnssec-signzone` finds the key files itself and also writes `dsset-example.com.` containing the DS records. Point the zone statement at `example.com.db.signed`. Keep `K*.private` files secret and backed up.

COMMAND | DESCRIPTION
---|---
`dnssec-keygen -a ECDSAP256SHA256 -n ZONE <ZONE>` | Generate a ZSK (use `ED25519` or `RSASHA256 -b 2048` where needed)
`dnssec-keygen -a ECDSAP256SHA256 -n ZONE -f KSK <ZONE>` | Generate a KSK
`dnssec-keygen -K <DIR> ...` | Write key files to a directory
`dnssec-keygen -P <DATE> -A <DATE> -I <DATE> -D <DATE> ...` | Set publish, activate, inactivate and delete times
`dnssec-settime -p all <KEYFILE>` | Print every timing value for a key
`dnssec-settime -I +30d -D +60d <KEYFILE>` | Change inactivation and deletion times
`dnssec-signzone -S -o <ZONE> <ZONEFILE>` | Smart-sign using key files in the current directory
`dnssec-signzone -S -K <DIR> -o <ZONE> <ZONEFILE>` | Look for key files in another directory
`dnssec-signzone -N unixtime ...` | Set the serial of the signed zone to the Unix time (`increment` and `keep` also exist)
`dnssec-signzone -e +30d ...` | Signature expiry (default 30 days from now)
`dnssec-signzone -x ...` | Sign the DNSKEY set with KSKs only
`dnssec-signzone -3 <SALT> -H 0 ...` | Use NSEC3 (`-H` sets iterations; `-` as the salt means none)
`dnssec-signzone -g -d <DIR> ...` | Pull in DS records of child zones from their `dsset-*` files
`dnssec-verify -o <ZONE> <SIGNED_FILE>` | Check a signed zone file
`named-checkzone -i full <ZONE> <SIGNED_FILE>` | Check the zone, including DNSSEC consistency

## DS Records
The DS record goes in the parent zone, so you add it at your registrar (or in the parent zone if you run it). Use SHA-256 (digest type 2).

COMMAND | DESCRIPTION
---|---
`dnssec-dsfromkey -a SHA-256 K<ZONE>.+013+<KEYTAG>.key` | DS from a KSK key file
`dnssec-dsfromkey -a SHA-256 -f <ZONEFILE> <ZONE>` | DS from a text zone file containing the DNSKEYs
`dig @<SERVER_IP> <ZONE> DNSKEY \| dnssec-dsfromkey -f - <ZONE>` | DS from a live server's DNSKEY answer
`dnssec-dsfromkey -C -a SHA-256 <KEYFILE>` | Print CDS records instead
`dig <ZONE> DS +short` | The DS the parent currently serves
`dig @<SERVER_IP> <ZONE> CDS +short` | CDS records published by the child
`dnssec-cds -f <CHILD_FILE> -d <DIR> <ZONE>` | Check child CDS/CDNSKEY against the parent `dsset-` file (see `dnssec-cds -h`)

A DS has four fields: key tag, algorithm number (13 is ECDSAP256SHA256), digest type (2 is SHA-256) and the digest. Registrars may ask for the DNSKEY itself instead; use `dig <ZONE> DNSKEY +short` and pick the `257` (KSK) line.

## rndc for DNSSEC
COMMAND | DESCRIPTION
---|---
`rndc dnssec -status <ZONE>` | Key states and next rollover (needs `dnssec-policy`)
`rndc dnssec -checkds published <ZONE>` | Tell BIND the new DS is now in the parent
`rndc dnssec -checkds withdrawn <ZONE>` | Tell BIND the old DS has been removed from the parent
`rndc dnssec -checkds -key <KEYTAG> -when <TIME> published <ZONE>` | Same for one KSK, with a time
`rndc dnssec -rollover -key <KEYTAG> <ZONE>` | Start a key rollover now
`rndc loadkeys <ZONE>` | Reload keys from the key directory without signing immediately
`rndc sign <ZONE>` | Load keys and sign as needed
`rndc signing -list <ZONE>` | Signing state of a zone with manually managed keys (zones using a policy tell you to use `rndc dnssec`)
`rndc signing -nsec3param 1 0 0 - <ZONE>` | Add an NSEC3 chain (hash, flags, iterations, salt) to a manually managed zone
`rndc signing -nsec3param none <ZONE>` | Remove the NSEC3 chain
`rndc zonestatus <ZONE>` | Shows `secure: yes`, `inline signing` and next key and re-sign times
`rndc secroots` | Write the trust anchors and negative trust anchors to `named.secroots`
`rndc managed-keys status` | RFC 5011 managed trust anchor state
`rndc validation status` / `rndc validation off` / `rndc validation on` | Show, disable or enable validation on a resolver (disabling is temporary, for testing)
`rndc nta -lifetime 1h <DOMAIN>` | Negative trust anchor: skip validation for a broken domain (maximum one week)
`rndc nta -dump` / `rndc nta -remove <DOMAIN>` | List or remove negative trust anchors
`rndc flushtree <DOMAIN>` | Clear cached data under a name after fixing it

## Validating Resolver
A BIND resolver validates by default with the built-in root trust anchor.

```text
options {
    recursion yes;
    dnssec-validation auto;
};
```

OPTION | DESCRIPTION
---|---
`dnssec-validation auto;` | Validate using the built-in root trust anchor (default)
`dnssec-validation yes;` | Validate, but you must configure the trust anchors
`dnssec-validation no;` | Do not validate (not recommended)

## dig
`dig` does not validate by itself: it relays what the resolver says. See [dig](dig.md) for general use.

COMMAND | DESCRIPTION
---|---
`dig +dnssec <NAME>` | Ask for RRSIGs (sets the DO bit)
`dig +dnssec +multiline <NAME>` | Show RRSIGs in a readable layout
`dig <NAME> @<RESOLVER>` | `ad` in the flags means the resolver validated the answer
`dig +cd <NAME> @<RESOLVER>` | Checking disabled: get the data even if validation fails
`dig <ZONE> DNSKEY +dnssec` | Public keys and their signature
`dig <ZONE> DS @<PARENT_NS>` | DS at a parent server
`dig +trace +dnssec <NAME>` | Follow the chain from the root with signatures
`dig <NAME> NSEC` / `dig <NAME> NSEC3PARAM` | Denial of existence records
`dig +noall +comments <NAME>` | Show only the header, flags and status

Compare the two:

```bash
dig app.example.com @RESOLVER_IP
dig +cd app.example.com @RESOLVER_IP
```

`SERVFAIL` on the first and `NOERROR` on the second means validation is failing and the data itself is reachable.

## delv
`delv` (from `bind9-dnsutils`) does its own validation and reports why it succeeded or failed, independent of your resolver.

COMMAND | DESCRIPTION
---|---
`delv <NAME>` | Prints `; fully validated` with the answer, or the validation failure
`delv @<RESOLVER> <NAME> <TYPE>` | Use a chosen server and type
`delv +vtrace <NAME>` | Trace the validation steps (DNSKEY and DS lookups)
`delv +rtrace <NAME>` | Trace the resolver fetches
`delv +mtrace <NAME>` | Trace the messages received
`delv -i <NAME>` | Disable validation (output reads `; answer not validated`)
`delv -a <ANCHOR_FILE> <NAME>` | Use a custom trust anchor file
`delv +short <NAME>` | Short form
`delv +multiline <NAME> DNSKEY` | Expanded record layout

## Troubleshooting
SYMPTOM | FIX
---|---
`SERVFAIL` from a validating resolver, `+cd` works | Validation failure; run `delv +vtrace <NAME>` to find the broken link
Signatures expired | Re-sign (`dnssec-signzone`) or check `rndc dnssec -status`, `rndc zonestatus` and the server clock; compare `dig +dnssec` RRSIG expiry times
DS at the registrar does not match the KSK | Compare `dig <ZONE> DS +short` with the DS from `dnssec-dsfromkey`; replace the DS at the registrar
Zone went bogus after changing provider or key | Publish the new DS before removing the old one; to leave DNSSEC remove the DS first, wait for its TTL, then unsign
Secondary serves unsigned or old data | With manual signing, transfer the `.signed` zone; check `rndc zonestatus` serial on each server
No `ad` flag but answer is fine | The resolver is not validating, or the zone is unsigned; `dig <ZONE> DS` at the parent shows whether a DS exists
Key files missing or not readable | `named` needs read access to `key-directory`; with `dnssec-policy` it must also be writable
Large DNSKEY responses fail | Try TCP (`dig +tcp`) and check the EDNS buffer size (`dig +bufsize=1232`); see [dig](dig.md)
Need to test a failing third-party domain | `rndc nta -lifetime 1h <DOMAIN>` on your resolver (temporary, and it removes protection for that name)
Clock skew | Validators reject signatures outside their validity window; check NTP on both signer and resolver

## See Also
- [BIND 9](../homelab/bind9.md)
- [dig](dig.md)
- [DNS Record Types](dns-record-types.md)
- [DNS Troubleshooting](../recipes/dns-troubleshooting.md)
- [Unbound](../homelab/unbound.md)
- [DNS Encryption](dns-encryption.md)
