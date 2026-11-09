# Elastic Stack
The Elastic Stack (often called ELK) is Elasticsearch for storage and search, Logstash for processing, Kibana for dashboards and Beats or Elastic Agent for shipping data. Use it for central logs and search in a lab that can spare the RAM. It is heavy compared with [Loki and Alloy](loki-alloy.md), and [Graylog](graylog.md) is the all-in-one alternative. These notes follow the 9.5 documentation.

Documentation: [Elasticsearch Docker install](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic) · [Filebeat](https://www.elastic.co/docs/reference/beats/filebeat/filebeat-installation-configuration)

## Host Setting
Elasticsearch needs a larger memory map limit:

```bash
sudo sysctl -w vm.max_map_count=1048576
sysctl vm.max_map_count
```

Make it permanent in `/etc/sysctl.d/`. Elastic's current page says to raise it to 1048576 when the default is lower. Older guides used 262144.

## Single Node (Docker)
From the Elastic docs:

```bash
docker network create elastic
docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:<VERSION>
```

The initial `elastic` password and a Kibana enrolment token print **once** on first start. Save them, or regenerate:

COMMAND | DESCRIPTION
---|---
`docker exec -it es01 /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic` | New password for the `elastic` user
`docker exec -it es01 /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana` | Token to connect Kibana (use `-s node` for another node, valid 30 minutes)
`docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .` | Copy the CA certificate for clients

Test with the CA certificate and the `elastic` credentials from a variable or `.netrc`, not typed on the command line:

```bash
curl --cacert http_ca.crt --netrc https://localhost:9200
```

Security is on by default, with HTTPS, and the `-m 1GB` limit is only for a quick trial. Pin the image tag. A production-like compose file with Kibana and `ELASTIC_PASSWORD` was **not verified** here.

## Ports
PORT | USE
---|---
9200 | Elasticsearch HTTP API
5601 | Kibana
5044 | Logstash Beats input (an example value, the plugin has no default)

## Common API Calls
These are standard Elasticsearch calls, not checked against the 9.5 reference in this pass:

COMMAND | DESCRIPTION
---|---
`GET _cluster/health` | Cluster state (green, yellow, red)
`GET _cat/indices?v` | Indices, sizes and document counts
`GET _cat/shards?v` | Shard placement
`GET _cat/allocation?v` | Disk use per node
`GET <INDEX>/_search?q=<TEXT>` | Quick search
`DELETE <INDEX>` | Delete an index (**destructive**)

Run them with `curl` against `https://localhost:9200/<PATH>` using the CA certificate and credentials as above, or in Kibana's Dev Tools.

## Filebeat
Install the `.deb` from `artifacts.elastic.co` and match the version to your Elasticsearch:

```bash
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-<VERSION>-amd64.deb
sudo dpkg -i filebeat-<VERSION>-amd64.deb
```

Minimal `/etc/filebeat/filebeat.yml`:

```yaml
filebeat.inputs:
  - type: filestream
    id: system-logs
    paths:
      - /var/log/*.log

output.elasticsearch:
  hosts: ["https://<ES_HOST>:9200"]
  username: "filebeat_writer"
  password: "${FILEBEAT_PASSWORD}"
  ssl.enabled: true
  ssl.ca_trusted_fingerprint: "<CA_FINGERPRINT>"
```

COMMAND | DESCRIPTION
---|---
`filebeat modules enable system` | Enable a module (the docs example uses `nginx`, so `system` is inferred)
`filebeat setup -e` | Load index templates and dashboards
`filebeat test config -e` | Validate the config
`filebeat test output` | Check the output connection (not verified)

Every `filestream` input needs a unique `id`. Use a dedicated writer user with limited rights, not `elastic`.

## Logstash
A minimal pipeline that receives Beats and writes to Elasticsearch:

```text
input {
  beats {
    port => 5044
  }
}

output {
  elasticsearch {
    hosts => ["https://<ES_HOST>:9200"]
    index => "%{[@metadata][beat]}-%{[@metadata][version]}"
  }
}
```

Filters (`grok`, `date`) and TLS options for the output were not verified. Many homelabs skip Logstash and ship straight from Beats to Elasticsearch.

## Licence and Forks
Elastic added AGPL as an option again in 2024, alongside ELv2 and SSPL. Check the licence for the version you run before relying on this. OpenSearch is the Apache 2.0 fork of Elasticsearch 7.10 (from general knowledge, not fetched here), and Graylog's Data Node is based on it.

## Not Verified
Kibana compose and the `kibana_system` password, `ELASTIC_PASSWORD` and `ES_JAVA_OPTS` environment variables, Index Lifecycle Management, `filebeat test output`, and Logstash filters.

## See Also
- [Graylog](graylog.md)
- [Loki and Alloy](loki-alloy.md)
- [Grafana](grafana.md)
- [Prometheus](prometheus.md)
