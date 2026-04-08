import json
import re

def analyze_sql_plan(plan_text: str):
    """
    Parses a PostgreSQL EXPLAIN ANALYZE plan and provides basic insights.
    """
    insights = []
    
    if "Seq Scan" in plan_text:
        table_match = re.search(r"Seq Scan on (\w+)", plan_text)
        table_name = table_match.group(1) if table_match else "unknown"
        insights.append(f"[CRITICAL] Sequential Scan detected on table '{table_name}'. Consider adding an index on filter columns.")
        
    if "Nested Loop" in plan_text:
        insights.append("[INFO] Nested Loop join detected. Ensure the inner table has appropriate indexes.")
        
    if "Sort" in plan_text:
        insights.append("[WARNING] Sort operation found. Check if work_mem is sufficient or if an index can provide ordering.")

    if "Parallel" in plan_text:
        insights.append("[INFO] Parallel query used. Worker processes are contributing to performance.")

    return {
        "summary": "Query analysis complete.",
        "insights": insights,
        "recommendation": "Review the critical items above to improve query performance."
    }

if __name__ == "__main__":
    # Mock plan for testing
    mock_plan = """
    Nested Loop  (cost=4.63..1035.79 rows=1 width=113) (actual time=0.045..0.048 rows=1 loops=1)
      ->  Seq Scan on users  (cost=0.00..32.40 rows=1 width=37) (actual time=0.015..0.017 rows=1 loops=1)
            Filter: (id = 123)
      ->  Index Scan using orders_user_id_idx on orders  (cost=0.29..8.30 rows=1 width=76) (actual time=0.024..0.025 rows=1 loops=1)
            Index Cond: (user_id = users.id)
    """
    print(json.dumps(analyze_sql_plan(mock_plan), indent=2))
