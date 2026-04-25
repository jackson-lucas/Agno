# SQL Optimization Cheatsheet

## Index Types
- **B-Tree**: Default. Good for ranges and equality.
- **GIN**: Best for JSONB, Array, and Full-Text Search.
- **BRIN**: Best for very large tables with timestamp or sequential data.
- **Hash**: Fast equality, but not for range queries.

## Common Bottlenecks
| Bottleneck | Sign in Plan | Fix |
|---|---|---|
| Large Seq Scans | `Seq Scan` with high rows | Add Index on Filter |
| Disk I/O Scans | `Buffers: Read=...` | Increase `shared_buffers` or optimize index |
| Inefficient Joins | `Hash Join` or `Nested Loop` without Index | Cluster tables or add join indexes |
| Large Sorts | `Sort Method: external merge` | Increase `work_mem` |

## PostgreSQL Best Practices
- Vacuum/Analyze regularly to keep statistics fresh.
- Use `partial indexes` for filtered queries (e.g. `WHERE active = true`).
- Use `covering indexes` (INCLUDE clause) to avoid heap fetches.
