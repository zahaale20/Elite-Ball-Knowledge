# Databases & Data Engineering — Storage, Pipelines & Query at Scale

> **Why this exists.** Every autonomous system is also a data system: it records what it sensed,
> what it decided, and what happened, and that record is the raw material for debugging, for
> training the next model, and for proving the system did the right thing. A flight test
> generates gigabytes per sortie; a fleet generates terabytes per day; the data flywheel that
> makes Tesla and leading defense-tech firms hard to beat is, underneath, a storage-and-pipeline problem. The
> engineer who understands how databases actually store, index, and transact — and how to build
> pipelines that move and shape data reliably at scale — is the one who turns a firehose of
> telemetry into queryable truth and into training sets, instead of into an unsearchable swamp.
>
> **What mastering it makes you.** The engineer who picks relational vs document vs time-series
> vs columnar *for reasons*; who reads a query plan and knows why it's slow; who understands what
> ACID actually guarantees and what an isolation level really allows; who designs idempotent,
> replayable pipelines; and who knows when to reach for Postgres, when for Kafka, and when for a
> data lake.

This module is the durable foundation under the world model and data flywheel of
[20-autonomy-ml-ai.md](../autonomy/20-ml-ai.md), the storage engine that the distributed-systems
guarantees of [80-software-distributed-systems-deep.md](80-distributed-systems-deep.md)
replicate and partition, and the source of training data for
[85-software-mlops-and-ml-infrastructure.md](85-mlops-and-ml-infrastructure.md). It rides
the transports of [83-software-networking-and-protocols.md](83-networking-and-protocols.md),
must be hardened per [86-software-cybersecurity-engineering.md](86-cybersecurity-engineering.md)
and encrypted per [87-software-cryptography-applied.md](87-cryptography-applied.md),
follows the engineering discipline of [12-career-software-engineering.md](../career/12-software-engineering.md),
and powers the OSINT/sensemaking work of [35-osint-verification-and-sensemaking.md](../information-environment/35-osint-verification-and-sensemaking.md)
and the vertical-integration data strategy of [41-companies-tesla-vertical-integration-data.md](../companies/41-tesla-vertical-integration-data.md).

---

## Table of Contents

1. [The data model spectrum](#1-the-data-model-spectrum)
2. [How a database stores data — B-trees and LSM-trees](#2-how-a-database-stores-data--b-trees-and-lsm-trees)
3. [Indexing and the query planner](#3-indexing-and-the-query-planner)
4. [Transactions, ACID, and isolation](#4-transactions-acid-and-isolation)
5. [Time-series and columnar stores](#5-time-series-and-columnar-stores)
6. [Streaming pipelines and the log](#6-streaming-pipelines-and-the-log)
7. [Batch, lakes, and the modern stack](#7-batch-lakes-and-the-modern-stack)
8. [Practice this week](#8-practice-this-week)
9. [Sources & further study](#9-sources--further-study)

---

## 1. The data model spectrum

There is no universal database; you choose the model that matches the access pattern.

| Model | Strength | Weakness | Example |
|---|---|---|---|
| Relational (SQL) | joins, constraints, ACID, flexible queries | rigid schema, scale-out harder | Postgres, MySQL |
| Document | flexible schema, locality of one object | weak cross-document joins | MongoDB |
| Key-value | fastest point lookup, simple | no query beyond the key | Redis, DynamoDB |
| Wide-column | huge write throughput, partition-tolerant | limited query model | Cassandra, ScyllaDB |
| Time-series | append-heavy, time-range queries, downsampling | not for general queries | TimescaleDB, InfluxDB |
| Columnar / OLAP | analytical scans, aggregation | poor point writes | ClickHouse, DuckDB |
| Graph | relationship traversal | scaling, niche | Neo4j |

The deepest split is **OLTP vs OLAP**. **OLTP** (online transaction processing) is many small
reads/writes of individual rows — row-oriented storage, B-trees, strong transactions (Postgres
running the fleet's task assignments). **OLAP** (analytical processing) is few queries that scan
millions of rows to aggregate — column-oriented storage, vectorized execution (ClickHouse
answering "average detection latency across last month's sorties"). Forcing one engine to do both
is the most common architecture mistake; the modern answer is to *separate* them and stream from
OLTP to OLAP.

---

## 2. How a database stores data — B-trees and LSM-trees

Two storage-engine families dominate, and the choice shapes everything above it.

### 2.1 B-trees (read-optimized, in-place)

A **B-tree** keeps data sorted in fixed-size pages, balanced so every lookup is $O(\log n)$ disk
reads. Writes update pages **in place** (with a write-ahead log for crash safety). This is the
engine in Postgres, MySQL/InnoDB, and most relational stores — excellent for reads and
range scans, with predictable space.

```
 B-tree (order simplified):
            [ 30 | 60 ]
           /     |     \
     [10|20] [40|50] [70|80|90]      lookups: root → branch → leaf, O(log n)
```

### 2.2 LSM-trees (write-optimized, append + compact)

A **log-structured merge-tree** buffers writes in memory (a memtable), flushes them as immutable
sorted files (SSTables), and **compacts** them in the background. Writes are sequential (fast on
both SSD and HDD); reads may check several SSTables (mitigated by Bloom filters). This powers
Cassandra, RocksDB, LevelDB, and most write-heavy stores — ideal for telemetry ingest where
writes vastly outnumber reads.

```
 LSM:  writes ─▶ memtable ─flush─▶ SSTable_0
                                   SSTable_1   ─compact─▶ merged, sorted, dedup'd
                                   SSTable_2
       reads check memtable + SSTables (Bloom filter skips most)
```

The tradeoff is **write amplification** (compaction rewrites data) vs **read amplification**
(checking multiple files). Telemetry firehose → LSM; transactional state with heavy reads →
B-tree. Knowing which engine is underneath tells you the performance profile before you benchmark.

---

## 3. Indexing and the query planner

An **index** is a secondary data structure (usually a B-tree or hash) that turns a full table
scan into a targeted lookup. The discipline is choosing the *right* indexes — each one speeds
reads but slows writes and costs space.

```sql
-- Without an index this scans every row; with it, the planner does an index seek.
CREATE INDEX idx_detections_time_vehicle
    ON detections (vehicle_id, detected_at DESC);   -- composite, leftmost-prefix usable

-- The planner reveals its strategy; read it before optimizing.
EXPLAIN ANALYZE
SELECT * FROM detections
WHERE vehicle_id = 7 AND detected_at > now() - interval '1 hour'
ORDER BY detected_at DESC
LIMIT 50;
```

Key principles:

- **Selectivity:** an index helps only when it narrows results sharply. Indexing a boolean column
  is usually useless (a scan is cheaper than the index traversal plus row fetches).
- **Composite indexes** follow the **leftmost-prefix** rule: `(a, b)` serves queries on `a` and
  on `a, b`, but not on `b` alone.
- **Covering indexes** include all columns a query needs, so the engine never touches the table.
- The **query planner** estimates costs from table statistics and chooses a plan (index scan vs
  seq scan vs different join algorithms — nested loop, hash join, merge join). Stale statistics →
  bad plans; `EXPLAIN ANALYZE` shows estimate vs reality. Reading query plans is the single most
  valuable database debugging skill.

---

## 4. Transactions, ACID, and isolation

A **transaction** groups operations so they succeed or fail together. **ACID**:

- **Atomicity:** all-or-nothing (the WAL + rollback make this true even across a crash).
- **Consistency:** the DB moves from one valid state to another (constraints, foreign keys hold).
- **Isolation:** concurrent transactions don't corrupt each other — but *how much* isolation is
  tunable, and this is where bugs hide.
- **Durability:** once committed, it survives a crash (the WAL is `fsync`'d before ack).

**Isolation levels** trade correctness for concurrency. The SQL standard defines four, by which
anomalies they permit:

| Level | Dirty read | Non-repeatable read | Phantom | Write skew |
|---|---|---|---|---|
| Read Uncommitted | yes | yes | yes | yes |
| Read Committed | no | yes | yes | yes |
| Repeatable Read (snapshot) | no | no | (no in MVCC) | yes |
| Serializable | no | no | no | no |

Most databases default to **Read Committed**, which is fine for many apps but allows
**non-repeatable reads** and **write skew** — the bug where two transactions each read a
consistent snapshot, each individually valid, but their combined effect violates an invariant
(the classic "both doctors go off-call simultaneously" example). If correctness depends on a
multi-row invariant under concurrency, you need **Serializable** (often via Serializable Snapshot
Isolation) or explicit locking (`SELECT ... FOR UPDATE`). Most engineers underestimate how weak
the default is — pair this with the consistency models in
[80-software-distributed-systems-deep.md](80-distributed-systems-deep.md).

**MVCC** (multi-version concurrency control, used by Postgres) lets readers see a consistent
snapshot without blocking writers, by keeping multiple row versions — at the cost of needing
`VACUUM` to reclaim dead versions.

---

## 5. Time-series and columnar stores

Autonomy data is overwhelmingly **time-series**: a stream of (timestamp, vehicle, signal,
value) tuples. Specialized stores exploit this:

- **Append-only, time-partitioned:** data is written in time order and stored in chunks by time
  range, so old chunks compress and drop cheaply (retention policies).
- **Downsampling / continuous aggregates:** raw 1 kHz data rolls up into 1 Hz summaries for
  long-term storage and fast dashboards.
- **Columnar layout:** storing each column contiguously makes analytical scans ("max altitude
  over the sortie") read only the columns needed and compress them well (same values cluster).

$$
\text{columnar scan cost} \propto (\text{columns read}) \times (\text{rows}), \quad \text{not all columns}
$$

```sql
-- TimescaleDB: a hypertable auto-partitions by time; a continuous aggregate
-- precomputes per-minute rollups so dashboards never scan raw samples.
SELECT time_bucket('1 minute', detected_at) AS minute,
       vehicle_id,
       avg(confidence)  AS avg_conf,
       max(range_m)     AS max_range
FROM detections
GROUP BY minute, vehicle_id;
```

The columnar OLAP stores (ClickHouse, DuckDB, Parquet-on-a-lake) are the analytical backbone:
vectorized execution processes columns in SIMD batches, achieving scan rates an OLTP row store
cannot approach. This is where post-mission analysis and training-data extraction live.

---

## 6. Streaming pipelines and the log

The unifying abstraction of modern data engineering is **the log** — an append-only, ordered,
replayable sequence of events. **Apache Kafka** is the canonical implementation, and Kleppmann's
key insight is that *the log is the source of truth* and every database, index, and cache is a
**materialized view** derived from it.

```
 Producers ─▶ Kafka topic (partitioned, ordered log, retained) ─▶ Consumers
   sensors        [e0 e1 e2 e3 e4 ...]   replayable                ├─▶ Postgres (OLTP view)
   vehicles       partition 0,1,2...     per-partition order       ├─▶ ClickHouse (OLAP view)
                                                                    └─▶ ML feature pipeline
```

Why this matters:

- **Decoupling:** producers and consumers scale independently; a new consumer (e.g. a new ML
  feature) replays history without touching producers.
- **Ordering and partitioning:** order is guaranteed *within a partition*; the partition key
  (e.g. `vehicle_id`) groups related events so they stay ordered.
- **Delivery semantics:** at-least-once by default; exactly-once *effects* via idempotent
  consumers and transactional writes (the same idempotency story as
  [80-software-distributed-systems-deep.md](80-distributed-systems-deep.md)).
- **Stream processing** (Flink, Kafka Streams, Spark Structured Streaming): windowed aggregations,
  joins, and enrichment on the stream, with **event-time** vs **processing-time** semantics and
  **watermarks** to handle late, out-of-order data (which is the norm on a lossy telemetry link).

A robust pipeline is **idempotent and replayable**: if it crashes and restarts, reprocessing
produces the same result, no duplicates and no gaps. Design every stage that way and operations
become recoverable instead of fragile.

---

## 7. Batch, lakes, and the modern stack

Not everything is streaming. **Batch** processing (Spark, dbt) transforms large datasets on a
schedule, and the modern architecture blends both:

- **Data lake:** cheap object storage (S3) holding raw and processed data as columnar files
  (Parquet) with open table formats (Apache Iceberg, Delta Lake) that add ACID transactions,
  schema evolution, and time travel on top of files — the "lakehouse."
- **ELT over ETL:** load raw data first, transform in the warehouse with SQL (dbt), keeping the
  raw source for reprocessing when requirements change.
- **Orchestration:** DAG schedulers (Airflow, Dagster) sequence pipeline steps with dependencies,
  retries, and backfills — the operational glue.
- **Data quality & lineage:** tests, schemas (great_expectations), and lineage tracking so a bad
  upstream change is caught before it poisons a training set — the data-engineering analogue of
  the verification discipline in [06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

The fielded-autonomy version of this stack is the **data flywheel**: vehicles generate telemetry →
log (Kafka) → lake (Parquet/Iceberg) → labeled training sets → better models
([85-software-mlops-and-ml-infrastructure.md](85-mlops-and-ml-infrastructure.md)) →
better vehicles → more/better telemetry. The company that closes this loop fastest wins, and the
loop is, end to end, a data-engineering artifact.

---

## 8. Practice this week

1. Load a million-row telemetry table into Postgres; write a slow query, read its `EXPLAIN
   ANALYZE` plan, add the right composite index, and confirm the seq scan became an index seek.
2. Construct a write-skew anomaly under Read Committed (two concurrent transactions that each
   pass their check but jointly break an invariant), then re-run under Serializable and show it
   is prevented.
3. Stand up a single-partition Kafka topic; write an idempotent consumer that materializes the
   log into both a Postgres view and a Parquet file; kill and restart it mid-stream and prove no
   duplicates or gaps.
4. Take the same telemetry into a row store and a columnar store (DuckDB/ClickHouse); benchmark a
   wide aggregation query and explain the difference from the storage layout.

---

## 9. Sources & further study

- **Kleppmann — *Designing Data-Intensive Applications (DDIA)*.** The single best book here:
  storage engines, indexing, transactions, the log, stream vs batch. Read it twice.
- **Garcia-Molina, Ullman & Widom — *Database Systems: The Complete Book*.** The rigorous
  internals reference (query processing, transactions, recovery).
- **Hellerstein & Stonebraker — *Readings in Database Systems* (the "Red Book").** Curated
  foundational papers with commentary.
- **Reis & Housley — *Fundamentals of Data Engineering*.** The modern lifecycle: ingestion,
  storage, transformation, serving.
- **Kafka & Apache Iceberg / Delta Lake documentation.** The log and the lakehouse from the
  source.
- **Postgres documentation (MVCC, indexes, EXPLAIN).** The best-documented production database.
- **Petrov — *Database Internals*.** Deep on B-trees, LSM-trees, and distributed database guts.

> Framing note: A database is not a place you put data and forget it — it is a set of explicit
> promises about how data is stored, queried, and kept consistent under concurrency and failure,
> and every one of those promises has a cost you pay in latency, throughput, or correctness. The
> engineers who close the data flywheel treat the log as the truth, choose the storage engine
> that matches the access pattern, read the query plan instead of guessing, and build pipelines
> that can crash, restart, and replay without losing or duplicating a single event — because the
> data trail is both the debugging record and the fuel for every model that comes next.
