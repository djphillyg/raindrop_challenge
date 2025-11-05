from textwrap import dedent

# CFG Grammar for SQL Output (not English input!)
# This constrains GPT-5 to OUTPUT valid SQL for garmin_active_cal_data table
# INPUT: English query from user
# OUTPUT: SQL query (constrained by this grammar)


FITNESS_SQL_GRAMMAR = dedent(r"""
     // ---------- Punctuation & operators ----------
    SP: " "
    COMMA: ","
    LPAREN: "("
    RPAREN: ")"
    STAR: "*"
    GT: ">"
    LT: "<"
    EQ: "="
    GTE: ">="
    LTE: "<="
    NEQ: "!="

    // ---------- Start ----------
    start: query

    query: "SELECT" SP select_clause SP "FROM" SP "garmin_active_cal_data" where_clause? order_clause? limit_clause?

    // ---------- Select clause ----------
    select_clause: STAR
                 | column_list
                 | agg_clause

    column_list: column (COMMA SP column)*

    column: "timestamp_day"
          | "active_calories"
          | "active_time"
          | "distance"
          | "activity_type"
          | "duration_min"
          | "steps"

    // ---------- Aggregations ----------
    agg_clause: aggregation (COMMA SP (column | aggregation))*

    aggregation: agg_func LPAREN agg_target RPAREN

    agg_target: column | STAR

    agg_func: "SUM" | "AVG" | "COUNT" | "MAX" | "MIN"

    // ---------- WHERE clause ----------
    where_clause: SP "WHERE" SP condition (SP "AND" SP condition)*

    condition: column SP operator SP value
             | column SP operator SP "today()" SP "-" SP "toIntervalDay" LPAREN NUMBER RPAREN

    operator: EQ | GT | LT | GTE | LTE | NEQ

    value: NUMBER

    // ---------- ORDER BY clause ----------
    order_clause: SP "ORDER" SP "BY" SP column (SP order_dir)?

    order_dir: "ASC" | "DESC"

    // ---------- LIMIT clause ----------
    limit_clause: SP "LIMIT" SP NUMBER

    // ---------- Terminals ----------
    NUMBER: /[0-9]+/
""")

sql_grammar_tool = {
    "type": "custom",
    "name": "sql_grammar",
    "description": "Executes read-only PostgreSQL queries limited to SELECT statements with LIMIT and basic WHERE/ORDER BY. YOU MUST REASON HEAVILY ABOUT THE QUERY AND MAKE SURE IT OBEYS THE GRAMMAR.",
    "format": {
        "type": "grammar",
        "syntax": "lark",
        "definition": FITNESS_SQL_GRAMMAR,
    }
}