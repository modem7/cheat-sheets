# MongoDB
MongoDB is a document database that stores JSON-like (BSON) documents in collections. This sheet covers `mongosh`, users and roles, indexes, everyday queries, and backup with `mongodump` and `mongorestore` from the MongoDB Database Tools.

Documentation: [MongoDB Manual](https://www.mongodb.com/docs/manual/) · [mongosh](https://www.mongodb.com/docs/mongodb-shell/) · [Database Tools](https://www.mongodb.com/docs/database-tools/)
Project: [MongoDB](https://www.mongodb.com/)

> **Verification:** the `mongodump`, `mongorestore`, `mongoexport` and `mongoimport` options were checked against `--help` from Database Tools 100.20.1. The `mongosh` options, `db.createUser`, `createIndex` and `find` syntax and the `mongo` Docker image variables were checked against the MongoDB docs and Docker Hub. `mongosh` itself was not run. **Not verified against the docs:** the update, delete, aggregation, `getIndexes`, `dropIndex`, `explain`, `db.getUsers` and `db.changeUserPassword` examples (standard shell API, written from knowledge), and the Compose healthcheck. `drop`, `deleteMany` and `dropDatabase` destroy data.

See also: [Docker](../docker/docker.md) · [Docker-Compose](../docker/docker-compose.md) · [Database Dumps](../backup/database-dumps.md) · [borgmatic](../backup/borgmatic.md) · [Redis](redis.md) · [PostgreSQL Cheat-Sheet](postgres.md)

---
## Run in Docker
The official `mongo` image creates a root user in the `admin` database only when both `MONGO_INITDB_ROOT_*` variables are set, and then starts with authentication enabled. The variables are ignored if the data directory already holds a database.

```yaml
services:
  mongo:
    image: mongo:8
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD_FILE: /run/secrets/mongo_root_password
    secrets: [mongo_root_password]
    volumes:
      - mongo-data:/data/db
      - mongo-config:/data/configdb
    ports:
      - 127.0.0.1:27017:27017

secrets:
  mongo_root_password:
    file: ./mongo-root-password

volumes:
  mongo-data:
  mongo-config:
```

VARIABLE / PATH | MEANING
---|---
`MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` | Create the root user (set both); only these two accept a `_FILE` suffix
`MONGO_INITDB_DATABASE` | Database the init scripts run against (default `test`)
`/docker-entrypoint-initdb.d/` | `.sh` and `.js` files run once, alphabetically, on first start
`/data/db` | Data directory
`/data/configdb` | Second volume defined by the image

```bash
docker compose exec mongo mongosh -u root --authenticationDatabase admin
```

## Connect with mongosh
COMMAND | DESCRIPTION
---|---
`mongosh` | Connect to `localhost:27017`
`mongosh "mongodb://HOST:27017/DBNAME"` | Connect with a connection string
`mongosh --host HOST --port 27017` | Host and port as options
`mongosh "mongodb://HOST:27017" --username USER --authenticationDatabase admin` | Prompts for the password
`mongosh "mongodb://USER@HOST:27017/DBNAME?authSource=admin"` | User and auth database in the URI (percent-encode special characters)
`mongosh "mongodb+srv://HOST/"` | SRV record URI, TLS on by default
`mongosh "mongodb://HOST:27017" --tls` | Force TLS
`mongosh --quiet --eval 'db.runCommand({ ping: 1 })' "mongodb://HOST:27017/DBNAME"` | Run a one-off expression for scripts
`mongosh --file SCRIPT.js "mongodb://HOST:27017/DBNAME"` | Run a script file (`-f` is the short form)
`mongosh --nodb` | Start without connecting
`mongosh --norc` | Skip `~/.mongoshrc.js`

Avoid `--password PASS` on the command line (it shows in the process list). Omit the value and `mongosh` prompts for it.

## Shell Helpers
COMMAND | DESCRIPTION
---|---
`show dbs` | List databases
`use DBNAME` | Switch database (created on first write)
`db` | Print the current database
`show collections` | List collections in the current database
`db.help()` | Database methods
`db.COLLECTION.help()` | Collection methods
`db.stats()` | Database statistics
`db.COLLECTION.countDocuments({})` | Count documents
`db.runCommand({ ping: 1 })` | Check the server answers
`db.version()` | Server version
`exit` | Leave the shell

## Queries
```javascript
// Insert
db.users.insertOne({ name: "Ada", role: "admin", logins: 3 })
db.users.insertMany([{ name: "Bob" }, { name: "Cy" }])

// Find, filter, project, sort, page
db.users.find()
db.users.find({ role: "admin" })
db.users.find({ logins: { $gt: 1 } }, { name: 1, _id: 0 })
db.users.find().sort({ name: 1 }).skip(10).limit(5)
db.users.findOne({ name: "Ada" })

// Update
db.users.updateOne({ name: "Ada" }, { $set: { role: "owner" }, $inc: { logins: 1 } })
db.users.updateMany({ role: "guest" }, { $set: { active: false } })

// Delete (destroys data)
db.users.deleteOne({ name: "Bob" })
db.users.deleteMany({ active: false })

// Aggregate
db.users.aggregate([
  { $match: { active: true } },
  { $group: { _id: "$role", total: { $sum: 1 } } },
  { $sort: { total: -1 } }
])
```

OPERATOR | MEANING
---|---
`$eq` `$ne` `$gt` `$gte` `$lt` `$lte` | Comparison
`$in` / `$nin` | Value in or not in a list
`$and` / `$or` / `$not` | Logical
`$exists` | Field present
`$set` / `$unset` / `$inc` | Update fields
`$push` / `$pull` | Add to or remove from an array

A projection cannot mix include and exclude, except for `_id`.

## Users and Roles
Create users in the database they authenticate against, usually `admin` for administrators. `passwordPrompt()` asks for the password instead of putting it in history.

```javascript
use admin
db.createUser({
  user: "appadmin",
  pwd: passwordPrompt(),
  roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
})

use appdb
db.createUser({
  user: "appuser",
  pwd: passwordPrompt(),
  roles: [{ role: "readWrite", db: "appdb" }]
})
```

COMMAND | DESCRIPTION
---|---
`db.getUsers()` | List users in the current database
`db.changeUserPassword("USER", passwordPrompt())` | Change a password
`db.grantRolesToUser("USER", [{ role: "read", db: "DBNAME" }])` | Add a role
`db.dropUser("USER")` | Delete a user

ROLE | GRANTS
---|---
`read` | Read non-system collections in one database
`readWrite` | Read and write, create and drop collections and indexes
`dbAdmin` | Indexes, statistics and schema tasks, no user management
`userAdmin` | Create and change users and roles in one database
`dbOwner` | `readWrite` plus `dbAdmin` plus `userAdmin`
`readAnyDatabase` / `readWriteAnyDatabase` | Same, across all databases (`admin` only)
`userAdminAnyDatabase` / `dbAdminAnyDatabase` | Same, across all databases (`admin` only)
`clusterMonitor` | Read-only monitoring
`backup` / `restore` | Privileges for `mongodump` and `mongorestore`
`root` | Superuser

Give applications `readWrite` on their own database only, and use the `backup` role for dump jobs. `db.createUser` is not supported on Atlas clusters.

## Indexes
Syntax is `createIndex(<keys>, <options>)`. Put every option in one document.

```javascript
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ role: 1, logins: -1 })
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })
db.users.createIndex({ email: 1 }, { partialFilterExpression: { active: true }, name: "active_email" })
```

COMMAND | DESCRIPTION
---|---
`db.COLLECTION.getIndexes()` | List indexes
`db.COLLECTION.dropIndex("NAME")` | Drop an index (change an option by dropping and recreating, except `hidden`)
`db.COLLECTION.hideIndex({ title: 1 })` / `unhideIndex(...)` | Hide from the query planner to test a drop
`db.COLLECTION.find({ ... }).explain("executionStats")` | Check an index is used (look for `IXSCAN`, not `COLLSCAN`)

OPTION | MEANING
---|---
`unique` | Reject duplicate key values (default false)
`expireAfterSeconds` | TTL index, 0 to 2147483647
`partialFilterExpression` | Index only matching documents (preferred to `sparse`)
`sparse` | Index only documents that contain the field
`name` | Index name
`hidden` | Hide from the planner

## Backup: mongodump and mongorestore
`mongodump` writes BSON and metadata (indexes included). It needs the `backup` role, and `mongorestore` needs `restore`.

COMMAND | DESCRIPTION
---|---
`mongodump --uri="mongodb://USER@HOST:27017/?authSource=admin" --out=DIR` | Dump everything to a directory (prompts for the password)
`mongodump --uri=URI --db=DBNAME --gzip --archive=FILE.gz` | One database, compressed, as a single archive file
`mongodump --uri=URI --db=DBNAME --collection=NAME --out=DIR` | One collection (`--collection` goes with `--db`)
`mongodump --uri=URI --db=DBNAME --excludeCollection=NAME --out=DIR` | Skip a collection (with `--db`)
`mongodump --uri=URI --dumpDbUsersAndRoles --db=DBNAME --out=DIR` | Include users and roles of a database
`mongodump --uri=URI --oplog --out=DIR` | Point-in-time dump of a replica set (see the Database Tools docs for the limits; unverified)
`mongorestore --uri=URI --dryRun DIR` | Summarise a restore without writing
`mongorestore --uri=URI DIR` | Restore a dump directory
`mongorestore --uri=URI --gzip --archive=FILE.gz` | Restore a gzipped archive
`mongorestore --uri=URI --drop DIR` | Drop each collection before restoring it (destroys current data)
`mongorestore --uri=URI --nsInclude='DBNAME.*' DIR` | Restore only matching namespaces
`mongorestore --uri=URI --nsFrom='old.*' --nsTo='new.*' DIR` | Restore into a renamed database
`mongorestore --uri=URI --restoreDbUsersAndRoles --db=DBNAME DIR` | Restore users and roles

In Docker, dump from the host with the tools in a throwaway container, or run them inside the server container:

```bash
docker compose exec -T mongo mongodump --username root --authenticationDatabase admin \
  --password "$(cat mongo-root-password)" --archive --gzip > mongo-$(date +%F).archive.gz
docker compose exec -T mongo mongorestore --username root --authenticationDatabase admin \
  --password "$(cat mongo-root-password)" --archive --gzip < mongo-2026-01-01.archive.gz
```

`--archive` with no file name writes to stdout (and reads from stdin for `mongorestore`), which is what makes the redirection work (unverified; the `--help` text lists `--archive=<file-path>` only). Test restores into a scratch instance ([Restore-Test a Backup](../recipes/restore-test-a-backup.md)).

## Export and Import
`mongoexport` and `mongoimport` move JSON or CSV. They lose some BSON types, so use `mongodump` for backups.

COMMAND | DESCRIPTION
---|---
`mongoexport --uri=URI --collection=NAME --out=FILE.json` | Export a collection as JSON lines
`mongoexport --uri=URI --collection=NAME --type=csv --fields=a,b --out=FILE.csv` | Export CSV
`mongoexport --uri=URI --collection=NAME --jsonArray --pretty --out=FILE.json` | Single pretty JSON array
`mongoexport --uri=URI --collection=NAME --sort='{a: 1}' --limit=100` | Sort and limit
`mongoimport --uri=URI --collection=NAME --file=FILE.json` | Import JSON lines
`mongoimport --uri=URI --collection=NAME --type=csv --headerline --file=FILE.csv` | Import CSV using the first line as field names
`mongoimport --uri=URI --collection=NAME --file=FILE.json --mode=upsert --upsertFields=_id` | Upsert instead of insert
`mongoimport --uri=URI --collection=NAME --file=FILE.json --drop` | Drop the collection first (destroys data)

## Install the Tools
The database tools are separate from the server and `mongosh`. On Ubuntu, download the `.deb` or `.tgz` for your release from the [Database Tools download page](https://www.mongodb.com/try/download/database-tools) and check the published SHA-256 before installing.

COMMAND | DESCRIPTION
---|---
`mongodump --version` | Confirm the tools are installed
`mongosh --version` | Confirm the shell is installed

## Troubleshooting
SYMPTOM | FIX
---|---
`Authentication failed` | Set `--authenticationDatabase` (or `authSource=`) to where the user was created, usually `admin`
`MONGO_INITDB_*` has no effect | The data volume already holds a database; the variables only run on first start
Init scripts did not run | They only run when `/data/db` is empty; use `MONGO_INITDB_DATABASE` to choose the database
Connection refused from another host | The port is bound to `127.0.0.1` in Compose, or the server `bindIp` excludes that interface
Slow query | Run `.explain("executionStats")`; add an index if it shows `COLLSCAN`
`mongorestore` leaves duplicates or errors | It does not drop existing data unless `--drop`; restore into an empty database
Password with `@` or `:` fails in a URI | Percent-encode it (`@` is `%40`) or use the prompt

## See Also
- [Docker](../docker/docker.md)
- [Docker-Compose](../docker/docker-compose.md)
- [Database Dumps](../backup/database-dumps.md)
- [borgmatic](../backup/borgmatic.md)
- [Redis](redis.md)
- [PostgreSQL Cheat-Sheet](postgres.md)
