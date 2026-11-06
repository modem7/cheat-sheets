# KASM Workspaces
Streaming containerized apps and desktops to end-users. The Workspaces platform provides enterprise-class orchestration, data loss prevention, and web streaming technology to enable the delivery of containerized workloads to your browser.

Documentation: [Kasm Docs](https://www.kasmweb.com/docs/latest/)

---
## Service Control
COMMAND | DESCRIPTION
---|---
`sudo /opt/kasm/bin/start` | Start Kasm services
`sudo /opt/kasm/bin/stop` | Stop Kasm services
`sudo docker ps --format '{{.Names}}\t{{.Status}}' \| grep kasm` | Container health
`sudo docker logs kasm_api` | API logs (also `kasm_manager`, `kasm_agent`, `kasm_proxy`)

## Add self-signed SSL Certificates

1. Stop the kasm services
```
sudo /opt/kasm/bin/stop
```

2. Replace `kasm_nginx.crt` and `kasm_nginx.key` files
```
sudo cp <your_cert> /opt/kasm/current/certs/kasm_nginx.crt
sudo cp <your_key> /opt/kasm/current/certs/kasm_nginx.key
```
Use the full chain in the `.crt` file. See [[openssl]] for creating certificates.

3. Start the Kasm Services
```
sudo /opt/kasm/bin/start
```

---
## Custom Images
Add a workspace under **Workspaces > Add Workspace** using a Docker image ([[docker]]).

Registry
```
https://index.docker.io/v1/
```

### Add Images in KASM
> [!attention]
> You need to pass in a "tag" in the Docker Image. Otherwise kasm won't pull and start the image correctly.

### Docker Run Config
**Example**
```
{
	"cap_add":["NET_ADMIN"],
	"devices":["dev/net/tun","/dev/net/tun"],
	"sysctls":{"net.ipv6.conf.all.disable_ipv6":"0"}
}
```
Other useful keys: `"environment"`, `"hostname"`, `"shm_size"`, `"dns"`.

---
## Troubleshooting

### KASM Agent
Check `sudo docker logs kasm_agent` and confirm the agent's address and port (default 4443) is reachable from the manager. Workspace containers that fail to start are visible with `sudo docker ps -a` and `sudo docker logs <CONTAINER>`.

### Database
Open a SQL shell:
```
sudo docker exec -it kasm_db psql -U kasmapp -d kasm
```
Back up before changing anything: `sudo docker exec kasm_db pg_dump -U kasmapp kasm > kasm-backup.sql` (see [[postgres]]).

### Delete invalid users from user_groups table

1. Check table for invalid entries
```
kasm=# select * from user_groups;
            user_group_id             |               user_id                |               group_id
--------------------------------------+--------------------------------------+--------------------------------------
 07c54672-739f-42d8-befc-bb2ba29fa22d | 71899524-5b31-41ac-a359-1aa8a008b831 | 68d557ac-4cac-42cc-a9f3-1c7c853de0f3
 e291f1f7-86be-490f-9f9b-3a520d4d1dfa | 71899524-5b31-41ac-a359-1aa8a008b831 | b578d8e9-5585-430b-a70b-9935e8acaaa3
 07b6f450-2bf5-48c0-9c5e-3443ad962fcb |                                      | 68d557ac-4cac-42cc-a9f3-1c7c853de0f3
 8c4c7242-b2b5-4a7a-89d3-e46d24456e5c |                                      | b578d8e9-5585-430b-a70b-9935e8acaaa3
```

2. Delete invalid entries from the table:
```postgresql
delete from user_groups where user_id is null;
```

3. Verify table
```
kasm=# select * from user_groups;
            user_group_id             |               user_id                |               group_id
--------------------------------------+--------------------------------------+--------------------------------------
 07c54672-739f-42d8-befc-bb2ba29fa22d | 71899524-5b31-41ac-a359-1aa8a008b831 | 68d557ac-4cac-42cc-a9f3-1c7c853de0f3
 e291f1f7-86be-490f-9f9b-3a520d4d1dfa | 71899524-5b31-41ac-a359-1aa8a008b831 | b578d8e9-5585-430b-a70b-9935e8acaaa3
(2 rows)
```
