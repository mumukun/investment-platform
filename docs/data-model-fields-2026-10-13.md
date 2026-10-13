# 平台数据模型字段附录

核对日期：2026-10-13。由当前工作区源码静态提取，不连接生产数据库。股票/Dashboard包含CHG-20261013-002未发布改动。本文是字段定义清单，不是数据库安装脚本；SQL部分含基础建表、相关增量列语句和显式索引，实际部署以仓库迁移逻辑为准。

Dashboard字段保留SQLAlchemy源码表达式，UUID、DateTime、JSONB分别对应PostgreSQL UUID、带时区时间、JSONB。TimestampMixin的created_at/updated_at列在适用表中展开。

## stock-analyzer

来源：[local_db.py](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py)

### market_structure_fact

```sql
CREATE TABLE IF NOT EXISTS market_structure_fact (
      kind TEXT NOT NULL, entity_id TEXT NOT NULL, trade_date TEXT NOT NULL,
      fact_hash TEXT NOT NULL, first_seen_at TIMESTAMPTZ NOT NULL,
      payload JSONB NOT NULL,
      PRIMARY KEY (kind, entity_id, trade_date, fact_hash));
CREATE INDEX IF NOT EXISTS idx_ms_fact_date ON market_structure_fact(kind,trade_date,entity_id);
```

### market_structure_generation

```sql
CREATE TABLE IF NOT EXISTS market_structure_generation (
      trade_date TEXT NOT NULL, phase TEXT NOT NULL, rules_version TEXT NOT NULL,
      input_hash TEXT NOT NULL, first_available_at TIMESTAMPTZ NOT NULL,
      payload JSONB NOT NULL,
      PRIMARY KEY (trade_date,phase,rules_version,input_hash));
CREATE INDEX IF NOT EXISTS idx_ms_generation_date ON market_structure_generation(trade_date,first_available_at);
```

### a_share_snapshot

```sql
CREATE TABLE IF NOT EXISTS a_share_snapshot (
      trade_date TEXT NOT NULL, update_time TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL,
      close DOUBLE PRECISION NOT NULL, change_pct DOUBLE PRECISION NOT NULL, amount DOUBLE PRECISION NOT NULL DEFAULT 0,
      turnover_pct DOUBLE PRECISION, pe_ttm DOUBLE PRECISION, high DOUBLE PRECISION, low DOUBLE PRECISION,
      industry TEXT, subindustry TEXT, limit_pct DOUBLE PRECISION,
      is_limit_up BOOLEAN NOT NULL DEFAULT FALSE, is_20cm BOOLEAN NOT NULL DEFAULT FALSE,
      is_30cm BOOLEAN NOT NULL DEFAULT FALSE, is_st BOOLEAN NOT NULL DEFAULT FALSE,
      limit_streak INTEGER NOT NULL DEFAULT 0, first_limit_time TEXT, is_one_word_limit BOOLEAN NOT NULL DEFAULT FALSE,
      PRIMARY KEY (trade_date, code));
ALTER TABLE a_share_snapshot ADD COLUMN IF NOT EXISTS pe_ttm DOUBLE PRECISION;
ALTER TABLE a_share_snapshot ADD COLUMN IF NOT EXISTS open DOUBLE PRECISION;
CREATE INDEX IF NOT EXISTS idx_a_share_snapshot_update ON a_share_snapshot(trade_date, update_time);
```

### a_share_daily_close

```sql
CREATE TABLE IF NOT EXISTS a_share_daily_close (
      trade_date TEXT NOT NULL, code TEXT NOT NULL, close DOUBLE PRECISION NOT NULL,
      amount DOUBLE PRECISION NOT NULL DEFAULT 0, PRIMARY KEY (trade_date, code));
```

### a_share_daily_metric

```sql
CREATE TABLE IF NOT EXISTS a_share_daily_metric (
      trade_date TEXT NOT NULL, code TEXT NOT NULL,
      pct_3 DOUBLE PRECISION, pct_5 DOUBLE PRECISION, pct_10 DOUBLE PRECISION, pct_20 DOUBLE PRECISION,
      pct_30 DOUBLE PRECISION, pct_60 DOUBLE PRECISION,
      ma5_distance DOUBLE PRECISION, ma20_distance DOUBLE PRECISION, ma60_distance DOUBLE PRECISION,
      rs5 DOUBLE PRECISION, rs20 DOUBLE PRECISION, rs30 DOUBLE PRECISION, rs60 DOUBLE PRECISION,
      industry_rs5 DOUBLE PRECISION, industry_rs20 DOUBLE PRECISION, industry_rs60 DOUBLE PRECISION,
      high5_distance DOUBLE PRECISION, high20_distance DOUBLE PRECISION, high60_distance DOUBLE PRECISION,
      max_drawdown60 DOUBLE PRECISION, avg_amount20 DOUBLE PRECISION, avg_amount60 DOUBLE PRECISION,
      amount_ratio5_20 DOUBLE PRECISION, is_high20 BOOLEAN NOT NULL DEFAULT FALSE,
      strength_score DOUBLE PRECISION, trend_score DOUBLE PRECISION, fund_score DOUBLE PRECISION,
      industry_score DOUBLE PRECISION, position_score DOUBLE PRECISION, risk_score DOUBLE PRECISION,
      updated_at TEXT NOT NULL, PRIMARY KEY (trade_date, code));
ALTER TABLE a_share_daily_metric ADD COLUMN IF NOT EXISTS trend_score DOUBLE PRECISION;
ALTER TABLE a_share_daily_metric ADD COLUMN IF NOT EXISTS fund_score DOUBLE PRECISION;
ALTER TABLE a_share_daily_metric ADD COLUMN IF NOT EXISTS industry_score DOUBLE PRECISION;
ALTER TABLE a_share_daily_metric ADD COLUMN IF NOT EXISTS position_score DOUBLE PRECISION;
ALTER TABLE a_share_daily_metric ADD COLUMN IF NOT EXISTS risk_score DOUBLE PRECISION;
ALTER TABLE a_share_daily_metric ADD COLUMN IF NOT EXISTS pct_30 DOUBLE PRECISION;
ALTER TABLE a_share_daily_metric ADD COLUMN IF NOT EXISTS rs30 DOUBLE PRECISION;
```

### a_share_security_profile

```sql
CREATE TABLE IF NOT EXISTS a_share_security_profile (
      code TEXT PRIMARY KEY, name TEXT, industry TEXT, subindustry TEXT, detail TEXT,
      limit_pct DOUBLE PRECISION, board TEXT, updated_at TEXT NOT NULL);
ALTER TABLE a_share_security_profile ADD COLUMN IF NOT EXISTS industry_taxonomy TEXT;
ALTER TABLE a_share_security_profile ADD COLUMN IF NOT EXISTS industry_source TEXT;
ALTER TABLE a_share_security_profile ADD COLUMN IF NOT EXISTS industry_effective_date TEXT;
```

### security_classification_snapshot

```sql
CREATE TABLE IF NOT EXISTS security_classification_snapshot (
      snapshot_date TEXT NOT NULL, classification_type TEXT NOT NULL, source TEXT NOT NULL,
      status TEXT NOT NULL, expected_count INTEGER NOT NULL DEFAULT 0,
      succeeded_count INTEGER NOT NULL DEFAULT 0, message TEXT,
      generated_at TEXT NOT NULL,
      PRIMARY KEY (snapshot_date, classification_type, source));
```

### security_concept_membership

```sql
CREATE TABLE IF NOT EXISTS security_concept_membership (
      snapshot_date TEXT NOT NULL, code TEXT NOT NULL, concept_code TEXT NOT NULL DEFAULT '',
      concept_name TEXT NOT NULL, source TEXT NOT NULL, generated_at TEXT NOT NULL,
      PRIMARY KEY (snapshot_date, code, concept_name, source));
CREATE INDEX IF NOT EXISTS idx_security_concept_code_date ON security_concept_membership(code, snapshot_date DESC);
```

### job_run

```sql
CREATE TABLE IF NOT EXISTS job_run (
      id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, job_name TEXT NOT NULL, trade_date TEXT,
      started_at TEXT NOT NULL, finished_at TEXT, status TEXT NOT NULL, message TEXT);
```

### security_trade_rule

```sql
CREATE TABLE IF NOT EXISTS security_trade_rule (
      trade_date TEXT NOT NULL, code TEXT NOT NULL, exchange TEXT, board TEXT, security_name TEXT,
      is_st BOOLEAN NOT NULL DEFAULT FALSE, is_suspended BOOLEAN NOT NULL DEFAULT FALSE,
      listing_date TEXT, price_limit_pct DOUBLE PRECISION, limit_up_price DOUBLE PRECISION,
      limit_down_price DOUBLE PRECISION, price_tick DOUBLE PRECISION,
      is_no_limit_day BOOLEAN NOT NULL DEFAULT FALSE, updated_at TEXT NOT NULL,
      PRIMARY KEY (trade_date, code));
```

### limit_up_snapshot_run

```sql
CREATE TABLE IF NOT EXISTS limit_up_snapshot_run (
      trade_date TEXT NOT NULL, snapshot_time TEXT NOT NULL,
      source TEXT NOT NULL, status TEXT NOT NULL, is_final BOOLEAN NOT NULL DEFAULT FALSE,
      item_count INTEGER NOT NULL DEFAULT 0, issues JSONB NOT NULL DEFAULT '[]'::jsonb,
      created_at TEXT NOT NULL,
      PRIMARY KEY (trade_date, snapshot_time));
CREATE INDEX IF NOT EXISTS idx_limit_up_run_date_time ON limit_up_snapshot_run(trade_date DESC, snapshot_time DESC);
```

### limit_up_snapshot

```sql
CREATE TABLE IF NOT EXISTS limit_up_snapshot (
      trade_date TEXT NOT NULL, snapshot_time TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL,
      close DOUBLE PRECISION, change_pct DOUBLE PRECISION, amount DOUBLE PRECISION,
      turnover_pct DOUBLE PRECISION, exchange TEXT, board TEXT, price_limit_pct DOUBLE PRECISION,
      is_st BOOLEAN NOT NULL DEFAULT FALSE, is_no_limit_day BOOLEAN NOT NULL DEFAULT FALSE,
      industry_l1 TEXT, industry_l2 TEXT, industry_taxonomy TEXT,
      industry_source TEXT, industry_effective_date TEXT,
      limit_streak INTEGER NOT NULL DEFAULT 1, first_limit_time TEXT, last_limit_time TEXT,
      break_count INTEGER, seal_amount DOUBLE PRECISION, recent_limit_stats TEXT,
      is_one_word_limit BOOLEAN NOT NULL DEFAULT FALSE, related_themes JSONB NOT NULL DEFAULT '[]'::jsonb,
      limit_reason TEXT, reason_kind TEXT NOT NULL DEFAULT 'unavailable',
      reason_source TEXT, reason_evidence TEXT, reason_quality TEXT NOT NULL DEFAULT 'unavailable',
      quality TEXT NOT NULL, issues JSONB NOT NULL DEFAULT '[]'::jsonb,
      PRIMARY KEY (trade_date, snapshot_time, code));
CREATE INDEX IF NOT EXISTS idx_limit_up_snapshot_date_code ON limit_up_snapshot(trade_date DESC, code);
```

### intraday_market_snapshot

```sql
CREATE TABLE IF NOT EXISTS intraday_market_snapshot (
      trade_date TEXT NOT NULL, snapshot_time TEXT NOT NULL, up_ratio DOUBLE PRECISION,
      limit_up_count INTEGER, limit_down_count INTEGER, broken_limit_ratio DOUBLE PRECISION,
      total_amount DOUBLE PRECISION, regime TEXT, regime_confidence DOUBLE PRECISION,
      regime_reasons TEXT, generated_at TEXT NOT NULL, PRIMARY KEY (trade_date, snapshot_time));
```

### intraday_sector_snapshot

```sql
CREATE TABLE IF NOT EXISTS intraday_sector_snapshot (
      trade_date TEXT NOT NULL, snapshot_time TEXT NOT NULL, sector_type TEXT NOT NULL,
      sector_code TEXT NOT NULL, strength DOUBLE PRECISION, breadth DOUBLE PRECISION,
      amount_increment DOUBLE PRECISION, flow_continuity DOUBLE PRECISION, lifecycle TEXT,
      core_structure TEXT, generated_at TEXT NOT NULL,
      PRIMARY KEY (trade_date, snapshot_time, sector_type, sector_code));
```

### intraday_stock_bar

```sql
CREATE TABLE IF NOT EXISTS intraday_stock_bar (
      trade_date TEXT NOT NULL, minute TEXT NOT NULL, code TEXT NOT NULL,
      open DOUBLE PRECISION, high DOUBLE PRECISION, low DOUBLE PRECISION, close DOUBLE PRECISION,
      volume DOUBLE PRECISION, amount DOUBLE PRECISION, vwap DOUBLE PRECISION,
      PRIMARY KEY (trade_date, minute, code));
```

### short_candidate_snapshot

```sql
CREATE TABLE IF NOT EXISTS short_candidate_snapshot (
      trade_date TEXT NOT NULL, snapshot_time TEXT NOT NULL, code TEXT NOT NULL, rules_version TEXT NOT NULL,
      candidate_type TEXT, stock_role TEXT, sector_lifecycle TEXT, primary_theme TEXT,
      opportunity_score DOUBLE PRECISION, risk_score DOUBLE PRECISION, grade TEXT, state TEXT,
      change_pct DOUBLE PRECISION, amount_yi DOUBLE PRECISION, gain_position_pct DOUBLE PRECISION,
      reasons TEXT, risk_reasons TEXT, data_time TEXT, pending_streak INTEGER NOT NULL DEFAULT 0,
      signal_time TEXT,
      PRIMARY KEY (trade_date, snapshot_time, code, rules_version));
```

### short_signal_event

```sql
CREATE TABLE IF NOT EXISTS short_signal_event (
      signal_id TEXT PRIMARY KEY, trade_date TEXT NOT NULL, code TEXT NOT NULL,
      previous_state TEXT, new_state TEXT NOT NULL, signal_time TEXT NOT NULL, data_time TEXT,
      opportunity_score DOUBLE PRECISION, risk_score DOUBLE PRECISION, grade TEXT,
      candidate_type TEXT, reasons TEXT, rules_version TEXT NOT NULL,
      theoretical_entry DOUBLE PRECISION);
```

### short_signal_outcome

```sql
CREATE TABLE IF NOT EXISTS short_signal_outcome (
      signal_id TEXT PRIMARY KEY, trade_date TEXT NOT NULL, code TEXT NOT NULL, rules_version TEXT NOT NULL,
      entry_price DOUBLE PRECISION, next_open_change DOUBLE PRECISION, next_low_change DOUBLE PRECISION,
      next_close_change DOUBLE PRECISION, pct_3 DOUBLE PRECISION, pct_5 DOUBLE PRECISION,
      mfe DOUBLE PRECISION, mae DOUBLE PRECISION, path_label TEXT,
      untradeable BOOLEAN NOT NULL DEFAULT FALSE, next_gap_down_severe BOOLEAN,
      high_open_low_close BOOLEAN, updated_at TEXT NOT NULL);
```

### setup_pattern_ledger

```sql
CREATE TABLE IF NOT EXISTS setup_pattern_ledger (
      trade_date TEXT NOT NULL, code TEXT NOT NULL, pattern TEXT NOT NULL,
      setup_score DOUBLE PRECISION, matched JSONB, key_level DOUBLE PRECISION,
      triggered BOOLEAN NOT NULL DEFAULT FALSE, triggered_date TEXT,
      pct_5_after DOUBLE PRECISION, pct_10_after DOUBLE PRECISION, settled_at TEXT,
      PRIMARY KEY (trade_date, code, pattern));
```

### short_factor_ledger

```sql
CREATE TABLE IF NOT EXISTS short_factor_ledger (
      trade_date TEXT NOT NULL, code TEXT NOT NULL, reversal_risk DOUBLE PRECISION,
      bucket TEXT, factors JSONB, entry_price DOUBLE PRECISION,
      next_close_change DOUBLE PRECISION, next_win BOOLEAN, pct_3 DOUBLE PRECISION,
      mae DOUBLE PRECISION, settled_at TEXT, PRIMARY KEY (trade_date, code));
```

### swing_daily_bar

```sql
CREATE TABLE IF NOT EXISTS swing_daily_bar (
      trade_date TEXT NOT NULL, code TEXT NOT NULL,
      open DOUBLE PRECISION, high DOUBLE PRECISION, low DOUBLE PRECISION, close DOUBLE PRECISION,
      amount DOUBLE PRECISION, volume DOUBLE PRECISION, turnover_pct DOUBLE PRECISION,
      adjusted_open DOUBLE PRECISION, adjusted_high DOUBLE PRECISION,
      adjusted_low DOUBLE PRECISION, adjusted_close DOUBLE PRECISION,
      PRIMARY KEY (trade_date, code));
ALTER TABLE swing_daily_bar ADD COLUMN IF NOT EXISTS volume DOUBLE PRECISION;
CREATE INDEX IF NOT EXISTS idx_swing_daily_bar_code_date ON swing_daily_bar(code, trade_date);
```

### swing_index_daily

```sql
CREATE TABLE IF NOT EXISTS swing_index_daily (
      trade_date TEXT NOT NULL, index_code TEXT NOT NULL, close DOUBLE PRECISION NOT NULL,
      PRIMARY KEY (trade_date, index_code));
```

### swing_feature_snapshot

```sql
CREATE TABLE IF NOT EXISTS swing_feature_snapshot (
      trade_date TEXT NOT NULL, code TEXT NOT NULL, data_time TEXT, feature_version TEXT NOT NULL,
      valid_bar_count INTEGER, close DOUBLE PRECISION, bar_end_date TEXT,
      position_40 DOUBLE PRECISION, position_120 DOUBLE PRECISION,
      range_5 DOUBLE PRECISION, range_10 DOUBLE PRECISION,
      range_20 DOUBLE PRECISION, range_60 DOUBLE PRECISION,
      atr_5 DOUBLE PRECISION, atr_20 DOUBLE PRECISION,
      natr_20 DOUBLE PRECISION, volatility_5 DOUBLE PRECISION, volatility_20 DOUBLE PRECISION,
      slope_20 DOUBLE PRECISION, trend_r2_20 DOUBLE PRECISION, residual_zscore DOUBLE PRECISION,
      max_drawdown_20 DOUBLE PRECISION, max_drawdown_40 DOUBLE PRECISION,
      max_drawdown_60 DOUBLE PRECISION,
      ma5 DOUBLE PRECISION, ma10 DOUBLE PRECISION, ma20 DOUBLE PRECISION, ma60 DOUBLE PRECISION,
      ma10_slope DOUBLE PRECISION, ma20_slope DOUBLE PRECISION, ma60_slope DOUBLE PRECISION,
      amount_ratio_5_20 DOUBLE PRECISION, amount_ratio_10_60 DOUBLE PRECISION,
      down_amount_ratio_10_60 DOUBLE PRECISION, up_down_amount_ratio_20 DOUBLE PRECISION,
      obv_slope_20 DOUBLE PRECISION,
      rs10_index DOUBLE PRECISION, rs20_index DOUBLE PRECISION, rs10_sector DOUBLE PRECISION,
      pivot_20 DOUBLE PRECISION, pivot_40 DOUBLE PRECISION, pivot_60 DOUBLE PRECISION, pivot_10 DOUBLE PRECISION,
      high_5 DOUBLE PRECISION, high_5_prev DOUBLE PRECISION,
      low_5 DOUBLE PRECISION, low_10 DOUBLE PRECISION,
      low_prev_10 DOUBLE PRECISION, low_20 DOUBLE PRECISION,
      above_ma20_days_5 INTEGER, higher_low_atr_20 DOUBLE PRECISION,
      max_single_day_gain_20 DOUBLE PRECISION, positive_gain_sum_20 DOUBLE PRECISION,
      upper_shadow_pct_5_max DOUBLE PRECISION,
      coverage DOUBLE PRECISION,
      created_at TEXT NOT NULL,
      PRIMARY KEY (trade_date, code, feature_version));
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS valid_bar_count INTEGER;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS close DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS bar_end_date TEXT;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS position_120 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS range_60 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS max_drawdown_60 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS ma60 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS ma60_slope DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS amount_ratio_10_60 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS down_amount_ratio_10_60 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS pivot_60 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS higher_low_atr_20 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS pivot_10 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS high_5 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS high_5_prev DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS low_5 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS low_10 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS low_prev_10 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS low_20 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS above_ma20_days_5 INTEGER;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS max_single_day_gain_20 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS positive_gain_sum_20 DOUBLE PRECISION;
ALTER TABLE swing_feature_snapshot ADD COLUMN IF NOT EXISTS upper_shadow_pct_5_max DOUBLE PRECISION;
```

### swing_setup_snapshot

```sql
CREATE TABLE IF NOT EXISTS swing_setup_snapshot (
      trade_date TEXT NOT NULL, code TEXT NOT NULL, pattern TEXT NOT NULL, rules_version TEXT NOT NULL,
      setup_score DOUBLE PRECISION, opportunity_score DOUBLE PRECISION, risk_score DOUBLE PRECISION,
      grade TEXT, matched JSONB, missing JSONB, risk_reasons JSONB,
      key_level DOUBLE PRECISION, stop_reference DOUBLE PRECISION, risk_distance_pct DOUBLE PRECISION,
      sector_score DOUBLE PRECISION, sector_lifecycle TEXT, market_regime TEXT,
      state TEXT, expiry_date TEXT, data_time TEXT,
      bar_end_date TEXT, board TEXT, structure_completion DOUBLE PRECISION,
      peer_percentile DOUBLE PRECISION, risk_distance_atr DOUBLE PRECISION,
      confirmation_state TEXT, data_confidence TEXT,
      participation_decision TEXT, execution_action TEXT, decision_reason TEXT,
      PRIMARY KEY (trade_date, code, pattern, rules_version));
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS current_price DOUBLE PRECISION;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS vwap DOUBLE PRECISION;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS same_time_amount_ratio DOUBLE PRECISION;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS daily_amount_ratio DOUBLE PRECISION;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS close_location_pct DOUBLE PRECISION;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS signal_basis TEXT;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS bar_end_date TEXT;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS board TEXT;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS structure_completion DOUBLE PRECISION;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS peer_percentile DOUBLE PRECISION;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS risk_distance_atr DOUBLE PRECISION;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS confirmation_state TEXT;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS data_confidence TEXT;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS participation_decision TEXT;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS execution_action TEXT;
ALTER TABLE swing_setup_snapshot ADD COLUMN IF NOT EXISTS decision_reason TEXT;
```

### swing_state_event

```sql
CREATE TABLE IF NOT EXISTS swing_state_event (
      event_id TEXT PRIMARY KEY, trade_date TEXT NOT NULL, code TEXT NOT NULL, pattern TEXT NOT NULL,
      previous_state TEXT, new_state TEXT NOT NULL, event_time TEXT, data_time TEXT,
      price DOUBLE PRECISION, vwap DOUBLE PRECISION, same_time_amount_ratio DOUBLE PRECISION,
      opportunity_score DOUBLE PRECISION, risk_score DOUBLE PRECISION, grade TEXT,
      key_level DOUBLE PRECISION, stop_reference DOUBLE PRECISION,
      reasons JSONB, rules_version TEXT NOT NULL);
ALTER TABLE swing_state_event ADD COLUMN IF NOT EXISTS daily_amount_ratio DOUBLE PRECISION;
ALTER TABLE swing_state_event ADD COLUMN IF NOT EXISTS signal_basis TEXT;
ALTER TABLE swing_state_event ADD COLUMN IF NOT EXISTS participation_decision TEXT;
CREATE INDEX IF NOT EXISTS idx_swing_state_event_day ON swing_state_event(trade_date, code, pattern);
```

### swing_signal_outcome

```sql
CREATE TABLE IF NOT EXISTS swing_signal_outcome (
      event_id TEXT PRIMARY KEY, trade_date TEXT NOT NULL, code TEXT NOT NULL, pattern TEXT NOT NULL,
      rules_version TEXT NOT NULL, entry_time TEXT, entry_price DOUBLE PRECISION, entry_source TEXT,
      stop_reference DOUBLE PRECISION, risk_r DOUBLE PRECISION,
      next_open_return DOUBLE PRECISION, next_low_return DOUBLE PRECISION, next_close_return DOUBLE PRECISION,
      pct_3 DOUBLE PRECISION, pct_5 DOUBLE PRECISION, pct_10 DOUBLE PRECISION,
      mfe_5 DOUBLE PRECISION, mae_5 DOUBLE PRECISION, mfe_10 DOUBLE PRECISION, mae_10 DOUBLE PRECISION,
      relative_sector_5 DOUBLE PRECISION, relative_index_5 DOUBLE PRECISION,
      path_label_5 TEXT, path_label_10 TEXT,
      untradeable BOOLEAN NOT NULL DEFAULT FALSE, gap_down_severe BOOLEAN, liquidity_failure BOOLEAN,
      settled_at TEXT);
```

### us_market_snapshot

```sql
CREATE TABLE IF NOT EXISTS us_market_snapshot (
      snapshot_id TEXT PRIMARY KEY,
      trade_date TEXT NOT NULL,
      us_trade_date TEXT NOT NULL,
      snapshot_kind TEXT NOT NULL,
      generated_at TEXT NOT NULL,
      as_of TEXT NOT NULL,
      contract_version TEXT NOT NULL,
      feature_version TEXT NOT NULL,
      mapping_version TEXT NOT NULL,
      model_version TEXT,
      quality TEXT NOT NULL,
      coverage DOUBLE PRECISION NOT NULL,
      is_mock BOOLEAN NOT NULL DEFAULT FALSE,
      payload JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_us_market_snapshot_latest ON us_market_snapshot(snapshot_kind, trade_date DESC, generated_at DESC);
```

### us_market_calendar_event

```sql
CREATE TABLE IF NOT EXISTS us_market_calendar_event (
      event_id TEXT PRIMARY KEY,
      event_type TEXT NOT NULL,
      category TEXT NOT NULL,
      name TEXT NOT NULL,
      scheduled_at TEXT NOT NULL,
      importance TEXT NOT NULL,
      status TEXT NOT NULL,
      session TEXT NOT NULL,
      source_name TEXT NOT NULL,
      source_url TEXT NOT NULL,
      related_us_assets JSONB NOT NULL DEFAULT '[]'::jsonb,
      related_a_sectors JSONB NOT NULL DEFAULT '[]'::jsonb,
      actual TEXT,
      consensus TEXT,
      previous TEXT,
      is_mock BOOLEAN NOT NULL DEFAULT FALSE,
      last_checked_at TEXT NOT NULL,
      payload JSONB NOT NULL DEFAULT '{}'::jsonb);
CREATE INDEX IF NOT EXISTS idx_us_market_calendar_scheduled ON us_market_calendar_event(scheduled_at);
```

### us_market_calendar_run

```sql
CREATE TABLE IF NOT EXISTS us_market_calendar_run (
      run_id TEXT PRIMARY KEY,
      generated_at TEXT NOT NULL,
      date_from TEXT NOT NULL,
      date_to TEXT NOT NULL,
      quality TEXT NOT NULL,
      coverage DOUBLE PRECISION NOT NULL,
      issues JSONB NOT NULL DEFAULT '[]'::jsonb);
CREATE INDEX IF NOT EXISTS idx_us_market_calendar_run_latest ON us_market_calendar_run(generated_at DESC);
```

### watchlist_item

```sql
CREATE TABLE IF NOT EXISTS watchlist_item (
      id TEXT PRIMARY KEY,
      security_id TEXT NOT NULL UNIQUE,
      code TEXT NOT NULL,
      name TEXT NOT NULL,
      market TEXT NOT NULL,
      exchange TEXT,
      security_type TEXT,
      attention_level TEXT NOT NULL DEFAULT '中关注',
      industry TEXT,
      sub_industry TEXT,
      industry_detail TEXT,
      theme_tags JSONB NOT NULL DEFAULT '[]'::jsonb,
      description TEXT,
      attention_reason TEXT,
      joined_on TEXT,
      current_price DOUBLE PRECISION,
      change_pct DOUBLE PRECISION,
      turnover_pct DOUBLE PRECISION,
      quote_date TEXT,
      quote_source TEXT,
      quote_quality TEXT NOT NULL DEFAULT 'unavailable',
      moving_average_status TEXT,
      distance_ma20_pct DOUBLE PRECISION,
      relative_strength_rs20 DOUBLE PRECISION,
      volume_status TEXT,
      breakout_status TEXT,
      signal_updated_at TEXT,
      source_version TEXT NOT NULL DEFAULT 'watchlist-store-v1',
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      revision BIGINT NOT NULL DEFAULT 1);
CREATE INDEX IF NOT EXISTS idx_watchlist_item_status_code ON watchlist_item(attention_level, code);
```

### watchlist_strategy_snapshot

```sql
CREATE TABLE IF NOT EXISTS watchlist_strategy_snapshot (
      id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
      trade_date TEXT NOT NULL,
      generated_at TEXT NOT NULL,
      watchlist_revision BIGINT NOT NULL,
      contract_version TEXT NOT NULL,
      short_rules_version TEXT,
      swing_rules_version TEXT,
      quality TEXT NOT NULL,
      payload JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_watchlist_strategy_snapshot_latest ON watchlist_strategy_snapshot(generated_at DESC);
```

### watchlist_alert_event

```sql
CREATE TABLE IF NOT EXISTS watchlist_alert_event (
      id TEXT PRIMARY KEY,
      security_id TEXT NOT NULL,
      triggered_at TEXT NOT NULL,
      code TEXT NOT NULL,
      name TEXT NOT NULL,
      trigger_type TEXT NOT NULL,
      direction TEXT NOT NULL,
      rung TEXT NOT NULL,
      price DOUBLE PRECISION,
      change_pct DOUBLE PRECISION,
      delivery_channels JSONB NOT NULL DEFAULT '[]'::jsonb,
      created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_watchlist_alert_event_latest ON watchlist_alert_event(triggered_at DESC);
```

## marketNewsFeed

来源：[db_schema.py](/Users/mukun/work/workspace/stock/marketNewsFeed/src/common/db_schema.py)

### events

```sql
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_id TEXT,
    source_url TEXT,
    category TEXT,
    author TEXT,
    title_original TEXT,
    title_zh TEXT,
    content_original TEXT,
    content_zh TEXT,
    language TEXT,
    pub_time TEXT,
    fetched_at TEXT NOT NULL,
    relevance_status TEXT DEFAULT 'pending',
    is_relevant INTEGER,
    level INTEGER,
    is_pushed INTEGER DEFAULT 0,
    push_status TEXT DEFAULT 'pending',
    push_error TEXT,
    is_catchup INTEGER DEFAULT 0,
    raw_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_source_pub_time ON events(source, pub_time);
CREATE INDEX IF NOT EXISTS idx_events_push_status ON events(push_status);
CREATE INDEX IF NOT EXISTS idx_events_level ON events(level);
```

### signals

```sql
CREATE TABLE IF NOT EXISTS signals (
    event_id TEXT PRIMARY KEY,
    level INTEGER,
    title_optimized TEXT,
    summary TEXT,
    insight TEXT,
    ustock TEXT,
    ashare TEXT,
    direction TEXT,
    catalyst TEXT,
    strength INTEGER,
    duration TEXT,
    topics TEXT,
    material TEXT,
    price_signal TEXT,
    supply_chain TEXT,
    risk TEXT,
    model TEXT,
    analysis_json TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### topic_heat

```sql
CREATE TABLE IF NOT EXISTS topic_heat (
    topic_date TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    heat_date TEXT NOT NULL,
    event_count INTEGER DEFAULT 0,
    heat_score DOUBLE PRECISION DEFAULT 0,
    level3_count INTEGER DEFAULT 0,
    level2_count INTEGER DEFAULT 0,
    avg_strength DOUBLE PRECISION DEFAULT 0,
    trend TEXT DEFAULT '',
    summary TEXT DEFAULT '',
    last_event_id TEXT,
    last_seen_at TEXT,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_topic_heat_date_score ON topic_heat(heat_date, heat_score);
```

### ashare_map

```sql
CREATE TABLE IF NOT EXISTS ashare_map (
    topic TEXT NOT NULL,
    ticker TEXT NOT NULL,
    name TEXT NOT NULL,
    sector TEXT,
    weight DOUBLE PRECISION DEFAULT 1,
    note TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY(topic, ticker)
);
```

### daily_briefings

```sql
CREATE TABLE IF NOT EXISTS daily_briefings (
    briefing_date TEXT PRIMARY KEY,
    content_json TEXT NOT NULL,
    sent_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### source_runtime_state

```sql
CREATE TABLE IF NOT EXISTS source_runtime_state (
    source TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'healthy',
    failure_count INTEGER NOT NULL DEFAULT 0,
    blocked_until TEXT,
    last_error TEXT,
    last_success_at TEXT,
    updated_at TEXT NOT NULL
);
```

### feishu_sync_queue

```sql
CREATE TABLE IF NOT EXISTS feishu_sync_queue (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    next_retry_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_feishu_sync_queue_status ON feishu_sync_queue(status, next_retry_at);
```

### feishu_record_map

```sql
CREATE TABLE IF NOT EXISTS feishu_record_map (
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    table_id TEXT NOT NULL,
    record_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY(object_type, object_id, table_id)
);
```

### x_watch_users

```sql
CREATE TABLE IF NOT EXISTS x_watch_users (
    user_id TEXT PRIMARY KEY,
    username TEXT,
    name TEXT,
    list_id TEXT,
    active INTEGER DEFAULT 1,
    latest_post_id TEXT,
    latest_checked_at TEXT,
    first_seen_at TEXT,
    updated_at TEXT,
    raw_json TEXT
);
```

### x_watch_posts

```sql
CREATE TABLE IF NOT EXISTS x_watch_posts (
    post_id TEXT PRIMARY KEY,
    user_id TEXT,
    username TEXT,
    name TEXT,
    text TEXT,
    lang TEXT,
    created_at TEXT,
    url TEXT,
    raw_json TEXT,
    llm_translation TEXT,
    llm_summary TEXT,
    llm_insight TEXT,
    llm_ashare TEXT,
    llm_ustock TEXT,
    llm_topics TEXT,
    llm_risk TEXT,
    llm_error TEXT,
    discord_status TEXT,
    feishu_status TEXT,
    feishu_extra_status TEXT DEFAULT 'skipped',
    push_status TEXT,
    push_attempts INTEGER DEFAULT 0,
    first_seen_at TEXT,
    pushed_at TEXT
);
```

### x_watch_api_usage

```sql
CREATE TABLE IF NOT EXISTS x_watch_api_usage (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    endpoint TEXT,
    resource_type TEXT,
    resource_count INTEGER,
    estimated_cost DOUBLE PRECISION,
    trigger TEXT,
    reason TEXT,
    created_at TEXT
);
```

## investment-research-dashboard

来源：[models.py](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/models.py)

### dashboard_users

ORM模型：`DashboardUser`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `username` | `Mapped[str]` | `mapped_column(String(40), unique=True, index=True)` |
| `password_hash` | `Mapped[str]` | `mapped_column(String(200))` |
| `display_name` | `Mapped[str]` | `mapped_column(String(80))` |
| `role` | `Mapped[str]` | `mapped_column(String(20), default='viewer')` |
| `is_active` | `Mapped[bool]` | `mapped_column(Boolean, default=True)` |
| `last_login_at` | `Mapped[datetime \| None]` | `mapped_column(DateTime(timezone=True), nullable=True)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### captcha_challenges

ORM模型：`CaptchaChallenge`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `source_hash` | `Mapped[str]` | `mapped_column(String(64), index=True)` |
| `target_x` | `Mapped[int]` | `mapped_column(Integer)` |
| `expires_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), index=True)` |
| `verified_at` | `Mapped[datetime \| None]` | `mapped_column(DateTime(timezone=True), nullable=True)` |
| `consumed_at` | `Mapped[datetime \| None]` | `mapped_column(DateTime(timezone=True), nullable=True)` |
| `token_hash` | `Mapped[str \| None]` | `mapped_column(String(64), unique=True, nullable=True)` |
| `failed_attempts` | `Mapped[int]` | `mapped_column(Integer, default=0)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### login_attempts

ORM模型：`LoginAttempt`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `occurred_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)` |
| `subject_hash` | `Mapped[str]` | `mapped_column(String(64), index=True)` |
| `source_hash` | `Mapped[str]` | `mapped_column(String(64), index=True)` |

### snapshots

表级索引/约束声明：

```python
__table_args__ = (Index('uq_market_structure_projection', 'domain', 'key', 'version', unique=True, postgresql_where=text("domain = 'market-structure'")), Index('ix_market_structure_history', 'domain', 'version', 'business_time', 'created_at'))
```

ORM模型：`Snapshot`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `domain` | `Mapped[str]` | `mapped_column(String(40), index=True)` |
| `key` | `Mapped[str]` | `mapped_column(String(80), index=True)` |
| `session` | `Mapped[str \| None]` | `mapped_column(String(20), index=True)` |
| `source` | `Mapped[str]` | `mapped_column(String(120))` |
| `business_time` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), index=True)` |
| `quality` | `Mapped[str]` | `mapped_column(String(20), default='healthy')` |
| `version` | `Mapped[str]` | `mapped_column(String(80))` |
| `is_mock` | `Mapped[bool]` | `mapped_column(Boolean, default=True)` |
| `payload` | `Mapped[dict[str, Any]]` | `mapped_column(JSONB)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### seat_subscriptions

ORM模型：`SeatSubscription`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `code` | `Mapped[str]` | `mapped_column(String(16), unique=True, index=True)` |
| `name` | `Mapped[str]` | `mapped_column(String(160))` |
| `label` | `Mapped[str]` | `mapped_column(String(80), default='')` |
| `aliases` | `Mapped[list[dict[str, Any]]]` | `mapped_column(JSONB, default=list)` |
| `note` | `Mapped[str]` | `mapped_column(Text, default='')` |
| `priority` | `Mapped[int]` | `mapped_column(Integer, default=0)` |
| `active` | `Mapped[bool]` | `mapped_column(Boolean, default=True)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### seat_reviews

ORM模型：`SeatReview`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `kind` | `Mapped[str]` | `mapped_column(String(20), index=True)` |
| `key` | `Mapped[str]` | `mapped_column(String(160), unique=True)` |
| `observation_date` | `Mapped[str]` | `mapped_column(String(10), index=True)` |
| `payload` | `Mapped[dict[str, Any]]` | `mapped_column(JSONB)` |
| `note` | `Mapped[str]` | `mapped_column(Text, default='')` |
| `favorite` | `Mapped[bool]` | `mapped_column(Boolean, default=False)` |
| `feedback` | `Mapped[str]` | `mapped_column(String(20), default='未到期')` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### watchlist_items

ORM模型：`WatchlistItem`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `upstream_id` | `Mapped[str]` | `mapped_column(String(80), unique=True, index=True)` |
| `code` | `Mapped[str]` | `mapped_column(String(20), index=True)` |
| `name` | `Mapped[str]` | `mapped_column(String(80))` |
| `market` | `Mapped[str]` | `mapped_column(String(20))` |
| `board` | `Mapped[str]` | `mapped_column(String(40))` |
| `research_status` | `Mapped[str]` | `mapped_column(String(30), default='发现')` |
| `strategy_preference` | `Mapped[str]` | `mapped_column(String(20), default='未指定')` |
| `position_stage` | `Mapped[str]` | `mapped_column(String(20), default='观察')` |
| `attention_level` | `Mapped[str]` | `mapped_column(String(20), default='普通')` |
| `reason` | `Mapped[str]` | `mapped_column(Text)` |
| `catalyst` | `Mapped[str]` | `mapped_column(Text)` |
| `trigger_condition` | `Mapped[str]` | `mapped_column(Text)` |
| `invalidation_condition` | `Mapped[str]` | `mapped_column(Text)` |
| `risk` | `Mapped[str]` | `mapped_column(Text)` |
| `quote` | `Mapped[dict[str, Any]]` | `mapped_column(JSONB)` |
| `source` | `Mapped[str]` | `mapped_column(String(80), default='stock-analyzer-demo')` |
| `business_time` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True))` |
| `data_version` | `Mapped[str]` | `mapped_column(String(40))` |
| `is_mock` | `Mapped[bool]` | `mapped_column(Boolean, default=True)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### decisions

ORM模型：`Decision`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `strategy_type` | `Mapped[str]` | `mapped_column(String(20), default='intraday', index=True)` |
| `trading_date` | `Mapped[str]` | `mapped_column(String(10), index=True)` |
| `priority` | `Mapped[int]` | `mapped_column(Integer, default=0)` |
| `scope_type` | `Mapped[str]` | `mapped_column(String(30), index=True)` |
| `scope_key` | `Mapped[str]` | `mapped_column(String(80), index=True)` |
| `action` | `Mapped[str]` | `mapped_column(String(30))` |
| `conclusion` | `Mapped[str]` | `mapped_column(Text)` |
| `confidence` | `Mapped[str]` | `mapped_column(String(20))` |
| `data_cutoff` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True))` |
| `data_quality` | `Mapped[str]` | `mapped_column(String(20))` |
| `evidence` | `Mapped[list[dict[str, Any]]]` | `mapped_column(JSONB)` |
| `counter_evidence` | `Mapped[list[dict[str, Any]]]` | `mapped_column(JSONB)` |
| `trigger_condition` | `Mapped[str]` | `mapped_column(Text)` |
| `invalidation_condition` | `Mapped[str]` | `mapped_column(Text)` |
| `risk` | `Mapped[str]` | `mapped_column(Text)` |
| `model_name` | `Mapped[str]` | `mapped_column(String(80))` |
| `model_version` | `Mapped[str]` | `mapped_column(String(40))` |
| `strategy_version` | `Mapped[str]` | `mapped_column(String(40))` |
| `change_summary` | `Mapped[str \| None]` | `mapped_column(Text)` |
| `input_summary` | `Mapped[dict[str, Any]]` | `mapped_column(JSONB)` |
| `user_status` | `Mapped[str]` | `mapped_column(String(20), default='待确认')` |
| `user_reason` | `Mapped[str \| None]` | `mapped_column(Text)` |
| `is_mock` | `Mapped[bool]` | `mapped_column(Boolean, default=True)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### market_events

ORM模型：`MarketEvent`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `upstream_id` | `Mapped[str \| None]` | `mapped_column(String(80), unique=True, index=True)` |
| `event_type` | `Mapped[str]` | `mapped_column(String(40), index=True)` |
| `occurred_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), index=True)` |
| `impact_scope` | `Mapped[str]` | `mapped_column(String(80))` |
| `before_value` | `Mapped[str]` | `mapped_column(String(80))` |
| `after_value` | `Mapped[str]` | `mapped_column(String(80))` |
| `trigger_rule` | `Mapped[str]` | `mapped_column(Text)` |
| `severity` | `Mapped[str]` | `mapped_column(String(20))` |
| `status` | `Mapped[str]` | `mapped_column(String(20), default='未处理')` |
| `details` | `Mapped[dict[str, Any]]` | `mapped_column(JSONB, default=dict)` |
| `is_mock` | `Mapped[bool]` | `mapped_column(Boolean, default=True)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### research_items

ORM模型：`ResearchItem`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `upstream_id` | `Mapped[str \| None]` | `mapped_column(String(160), unique=True, index=True)` |
| `title` | `Mapped[str]` | `mapped_column(String(240))` |
| `information_type` | `Mapped[str]` | `mapped_column(String(30))` |
| `source_name` | `Mapped[str]` | `mapped_column(String(100))` |
| `source_url` | `Mapped[str \| None]` | `mapped_column(Text)` |
| `published_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True))` |
| `summary` | `Mapped[str]` | `mapped_column(Text)` |
| `related_objects` | `Mapped[list[dict[str, Any]]]` | `mapped_column(JSONB)` |
| `source_payload` | `Mapped[dict[str, Any]]` | `mapped_column(JSONB, default=dict)` |
| `analysis` | `Mapped[dict[str, Any]]` | `mapped_column(JSONB, default=dict)` |
| `source_version` | `Mapped[str]` | `mapped_column(String(60), default='local-v1')` |
| `source_updated_at` | `Mapped[datetime \| None]` | `mapped_column(DateTime(timezone=True))` |
| `synced_at` | `Mapped[datetime \| None]` | `mapped_column(DateTime(timezone=True))` |
| `is_mock` | `Mapped[bool]` | `mapped_column(Boolean, default=True)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### reviews

ORM模型：`Review`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `trading_date` | `Mapped[str]` | `mapped_column(String(10), unique=True, index=True)` |
| `market_summary` | `Mapped[str]` | `mapped_column(Text)` |
| `decision_result` | `Mapped[str]` | `mapped_column(String(30))` |
| `error_type` | `Mapped[str \| None]` | `mapped_column(String(40))` |
| `user_note` | `Mapped[str]` | `mapped_column(Text, default='')` |
| `metrics` | `Mapped[dict[str, Any]]` | `mapped_column(JSONB)` |
| `timeline` | `Mapped[list[dict[str, Any]]]` | `mapped_column(JSONB)` |
| `is_mock` | `Mapped[bool]` | `mapped_column(Boolean, default=True)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### decision_feedback

ORM模型：`DecisionFeedback`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `decision_id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), ForeignKey('decisions.id', ondelete='CASCADE'), index=True)` |
| `status` | `Mapped[str]` | `mapped_column(String(20))` |
| `reason` | `Mapped[str]` | `mapped_column(Text)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### audit_logs

ORM模型：`AuditLog`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `occurred_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)` |
| `actor` | `Mapped[str]` | `mapped_column(String(80), default='local-user')` |
| `action` | `Mapped[str]` | `mapped_column(String(80), index=True)` |
| `target_type` | `Mapped[str]` | `mapped_column(String(40))` |
| `target_id` | `Mapped[str]` | `mapped_column(String(80))` |
| `detail` | `Mapped[dict[str, Any]]` | `mapped_column(JSONB)` |

### sync_states

ORM模型：`SyncState`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `upstream` | `Mapped[str]` | `mapped_column(String(80), unique=True)` |
| `status` | `Mapped[str]` | `mapped_column(String(20))` |
| `last_success_at` | `Mapped[datetime \| None]` | `mapped_column(DateTime(timezone=True))` |
| `records_synced` | `Mapped[int]` | `mapped_column(default=0)` |
| `message` | `Mapped[str]` | `mapped_column(Text)` |
| `source_version` | `Mapped[str]` | `mapped_column(String(40))` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |

### sector_scores

ORM模型：`SectorScore`。

| 字段 | 应用类型 | 数据库声明/约束 |
| --- | --- | --- |
| `id` | `Mapped[UUID]` | `mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)` |
| `category` | `Mapped[str]` | `mapped_column(String(30), index=True)` |
| `name` | `Mapped[str]` | `mapped_column(String(80), index=True)` |
| `change` | `Mapped[float]` | `mapped_column(Float)` |
| `fund_flow` | `Mapped[float]` | `mapped_column(Float)` |
| `activity` | `Mapped[float]` | `mapped_column(Float)` |
| `diffusion` | `Mapped[float]` | `mapped_column(Float)` |
| `score` | `Mapped[float]` | `mapped_column(Float, index=True)` |
| `core_stocks` | `Mapped[list[dict[str, Any]]]` | `mapped_column(JSONB)` |
| `evidence_kind` | `Mapped[str]` | `mapped_column(String(30))` |
| `business_time` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True))` |
| `is_mock` | `Mapped[bool]` | `mapped_column(Boolean, default=True)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)` |
