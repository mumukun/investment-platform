# 数据表—函数读写索引（细化版）

核对日期2026-10-13。覆盖全部58张当前模型表。以下为静态源码证据，不执行采集、SQL或业务代码。

判读规则：SQL INSERT/UPDATE/DELETE/FROM/JOIN是函数中出现的文字证据；ORM select/insert及模型引用只描述源码用法，不把任意引用冒充写操作。动态表名参数保留为待沿helper确认的引用。DELETE语句也含FROM，所以可能同时列为SQL读；这不是第二次真实查询。初始化DDL、测试及self_test不是业务数据血缘。函数中嵌套函数的证据另列，不声称运行调用次数或完整调用闭包。

本文结合[细粒度业务数据手册](/Users/mukun/.codex/worktrees/market-structure-etf/investment-platform/docs/data-architecture-detail-2026-10-13.md)阅读；字段定义见[完整字段附录](/Users/mukun/.codex/worktrees/market-structure-etf/investment-platform/docs/data-model-fields-2026-10-13.md)。

## stock-analyzer

### market_structure_fact

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_facts` | [stock_analyzer/market_structure_store.py:17](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/market_structure_store.py:17) |
| SQL读 FROM/JOIN | `load_facts` | [stock_analyzer/market_structure_store.py:47](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/market_structure_store.py:47) |
| SQL读 FROM/JOIN | `collect` | [stock_analyzer/market_structure_sync.py:78](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/market_structure_sync.py:78) |

### market_structure_generation

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_generation` | [stock_analyzer/market_structure_store.py:130](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/market_structure_store.py:130) |
| SQL读 FROM/JOIN | `generations` | [stock_analyzer/market_structure_store.py:149](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/market_structure_store.py:149) |

### a_share_snapshot

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `_upsert_snapshot` | [stock_analyzer/local_db.py:469](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:469) |
| SQL读 FROM/JOIN | `latest_snapshot` | [stock_analyzer/local_db.py:511](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:511) |
| SQL读 FROM/JOIN | `load_limit_up_history` | [stock_analyzer/local_db.py:693](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:693) |
| SQL读 FROM/JOIN | `latest_scored_snapshot` | [stock_analyzer/local_db.py:773](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:773) |
| SQL读 FROM/JOIN | `previous_limit_streaks` | [stock_analyzer/local_db.py:855](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:855) |
| SQL读 FROM/JOIN | `load_eod_history_for_codes` | [stock_analyzer/local_db.py:864](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:864) |
| SQL读 FROM/JOIN | `collect` | [stock_analyzer/market_structure_sync.py:78](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/market_structure_sync.py:78) |
| SQL读 FROM/JOIN | `compute` | [stock_analyzer/market_structure_sync.py:342](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/market_structure_sync.py:342) |
| SQL读 FROM/JOIN | `_cached_industry_contract` | [stock_analyzer/sector_activity_contract.py:496](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/sector_activity_contract.py:496) |
| SQL读 FROM/JOIN | `build_sector_workbench_envelope` | [stock_analyzer/sector_activity_contract.py:573](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/sector_activity_contract.py:573) |
| SQL读 FROM/JOIN | `_previous_trade_date` | [stock_analyzer/short_engine_contract.py:73](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_contract.py:73) |
| SQL读 FROM/JOIN | `_yesterday_limit_avg_change` | [stock_analyzer/short_engine_contract.py:81](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_contract.py:81) |
| SQL读 FROM/JOIN | `_daily_path` | [stock_analyzer/short_engine_outcomes.py:59](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_outcomes.py:59) |
| SQL读 FROM/JOIN | `_atr_proxy` | [stock_analyzer/short_engine_outcomes.py:75](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_outcomes.py:75) |
| SQL读 FROM/JOIN | `append_completed_snapshot_bars` | [stock_analyzer/swing_daily_data.py:220](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_daily_data.py:220) |
| SQL读 FROM/JOIN | `liquid_universe` | [stock_analyzer/swing_daily_data.py:320](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_daily_data.py:320) |
| SQL读 FROM/JOIN | `_post_daily_bars` | [stock_analyzer/swing_outcomes.py:83](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_outcomes.py:83) |
| SQL读 FROM/JOIN | `settle_event` | [stock_analyzer/swing_outcomes.py:157](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_outcomes.py:157) |
| SQL读 FROM/JOIN | `load_sector_history_means` | [stock_analyzer/swing_store.py:646](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:646) |
| SQL读 FROM/JOIN | `load_daily_history` | [stock_analyzer/watchlist_report.py:173](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_report.py:173) |

### a_share_daily_close

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `build_rules` | [scripts/import_trade_rules.py:113](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/scripts/import_trade_rules.py:113) |
| SQL写 INSERT | `save_snapshot` | [stock_analyzer/local_db.py:490](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:490) |
| SQL读 FROM/JOIN | `_history` | [stock_analyzer/local_db.py:806](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:806) |
| SQL读 FROM/JOIN | `close_history_count` | [stock_analyzer/local_db.py:840](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:840) |
| SQL写 INSERT | `save_close_history` | [stock_analyzer/local_db.py:845](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:845) |
| SQL读 FROM/JOIN | `_amount_vs_5d_avg` | [stock_analyzer/short_engine_contract.py:99](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_contract.py:99) |
| SQL读 FROM/JOIN | `_minimum_listing_date_cutoff` | [stock_analyzer/short_engine_contract.py:112](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_contract.py:112) |

### a_share_daily_metric

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `latest_scored_snapshot` | [stock_analyzer/local_db.py:773](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:773) |
| SQL写 INSERT | `_upsert_metrics` | [stock_analyzer/local_db.py:948](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:948) |
| SQL读 FROM/JOIN | `liquid_universe` | [stock_analyzer/swing_daily_data.py:320](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_daily_data.py:320) |
| SQL读 FROM/JOIN | `latest_daily_metrics_for_codes` | [stock_analyzer/swing_store.py:417](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:417) |
| SQL读 FROM/JOIN | `load_metric_rows` | [stock_analyzer/swing_store.py:826](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:826) |

### a_share_security_profile

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `load_limit_up_history` | [stock_analyzer/local_db.py:693](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:693) |
| SQL读 FROM/JOIN | `load_security_profiles` | [stock_analyzer/local_db.py:895](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:895) |
| SQL写 INSERT | `save_security_profiles` | [stock_analyzer/local_db.py:924](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:924) |
| SQL读 FROM/JOIN | `_cached_industry_contract` | [stock_analyzer/sector_activity_contract.py:496](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/sector_activity_contract.py:496) |

### security_classification_snapshot

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_concept_snapshot` | [stock_analyzer/security_classification.py:217](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/security_classification.py:217) |
| SQL读 FROM/JOIN | `refresh_concept_snapshot` | [stock_analyzer/security_classification.py:277](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/security_classification.py:277) |
| SQL读 FROM/JOIN | `_latest_healthy_concept_snapshot` | [stock_analyzer/security_classification.py:320](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/security_classification.py:320) |
| SQL读 FROM/JOIN | `_latest_partial_concept_snapshot` | [stock_analyzer/security_classification.py:336](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/security_classification.py:336) |

### security_concept_membership

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `save_limit_up_snapshot` | [stock_analyzer/local_db.py:520](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:520) |
| SQL写 INSERT / SQL删 DELETE / SQL读 FROM/JOIN | `save_concept_snapshot` | [stock_analyzer/security_classification.py:217](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/security_classification.py:217) |
| SQL读 FROM/JOIN | `load_security_classifications` | [stock_analyzer/security_classification.py:352](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/security_classification.py:352) |

### job_run

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT / SQL改 UPDATE | `job_run` | [stock_analyzer/local_db.py:454](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:454) |
| SQL写 INSERT | `record_job_result` | [stock_analyzer/local_db.py:973](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:973) |

### security_trade_rule

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `save_limit_up_snapshot` | [stock_analyzer/local_db.py:520](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:520) |
| SQL读 FROM/JOIN | `load_limit_up_history` | [stock_analyzer/local_db.py:693](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:693) |
| SQL读 FROM/JOIN | `load_security_profiles` | [stock_analyzer/local_db.py:895](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:895) |
| SQL读 FROM/JOIN | `compute` | [stock_analyzer/market_structure_sync.py:342](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/market_structure_sync.py:342) |
| SQL写 INSERT | `upsert_trade_rules` | [stock_analyzer/short_engine_store.py:53](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:53) |
| SQL读 FROM/JOIN | `load_trade_rules` | [stock_analyzer/short_engine_store.py:108](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:108) |
| SQL读 FROM/JOIN | `liquid_universe` | [stock_analyzer/swing_daily_data.py:320](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_daily_data.py:320) |
| SQL读 FROM/JOIN | `load_trade_rules` | [stock_analyzer/swing_store.py:680](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:680) |

### limit_up_snapshot_run

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_limit_up_snapshot` | [stock_analyzer/local_db.py:520](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:520) |
| SQL读 FROM/JOIN | `load_limit_up_history` | [stock_analyzer/local_db.py:693](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:693) |

### limit_up_snapshot

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_limit_up_snapshot` | [stock_analyzer/local_db.py:520](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:520) |
| SQL读 FROM/JOIN | `load_limit_up_history` | [stock_analyzer/local_db.py:693](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/local_db.py:693) |

### intraday_market_snapshot

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_market_snapshot_row` | [stock_analyzer/short_engine_store.py:370](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:370) |

### intraday_sector_snapshot

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_sector_snapshot_rows` | [stock_analyzer/short_engine_store.py:392](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:392) |

### intraday_stock_bar

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_intraday_bars` | [stock_analyzer/short_engine_store.py:273](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:273) |
| SQL读 FROM/JOIN | `load_intraday_bars` | [stock_analyzer/short_engine_store.py:299](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:299) |
| SQL读 FROM/JOIN | `load_historical_poll_bars` | [stock_analyzer/short_engine_store.py:321](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:321) |
| SQL读 FROM/JOIN | `_entry_from_intraday` | [stock_analyzer/swing_outcomes.py:58](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_outcomes.py:58) |
| SQL写 INSERT | `save_intraday_bars` | [stock_analyzer/swing_store.py:500](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:500) |
| SQL写 INSERT | `insert_intraday_bars` | [stock_analyzer/swing_store.py:528](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:528) |
| SQL读 FROM/JOIN | `load_today_bars` | [stock_analyzer/swing_store.py:556](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:556) |
| SQL读 FROM/JOIN | `load_latest_today_bars` | [stock_analyzer/swing_store.py:579](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:579) |
| SQL读 FROM/JOIN | `load_same_time_amount_history` | [stock_analyzer/swing_store.py:601](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:601) |
| SQL读 FROM/JOIN | `count_intraday_history_days` | [stock_analyzer/swing_store.py:811](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:811) |

### short_candidate_snapshot

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_candidate_snapshots` | [stock_analyzer/short_engine_store.py:122](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:122) |
| SQL读 FROM/JOIN | `latest_candidate_states` | [stock_analyzer/short_engine_store.py:164](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:164) |

### short_signal_event

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `investment_dashboard_short_selection_history` | [stock_analyzer/api.py:805](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:805) |
| SQL读 FROM/JOIN | `_events_to_settle` | [stock_analyzer/short_engine_outcomes.py:43](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_outcomes.py:43) |
| SQL写 INSERT | `record_signal_event` | [stock_analyzer/short_engine_store.py:184](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:184) |
| SQL读 FROM/JOIN | `list_signal_events` | [stock_analyzer/short_engine_store.py:210](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:210) |

### short_signal_outcome

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `_events_to_settle` | [stock_analyzer/short_engine_outcomes.py:43](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_outcomes.py:43) |
| SQL写 INSERT | `upsert_signal_outcomes` | [stock_analyzer/short_engine_store.py:231](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/short_engine_store.py:231) |

### setup_pattern_ledger

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| 未找到直接文字引用；不得推断已启用 | — | 模型定义存在，动态路径需进一步核对 |

### short_factor_ledger

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| 未找到直接文字引用；不得推断已启用 | — | 模型定义存在，动态路径需进一步核对 |

### swing_daily_bar

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `_latest_complete_bar_date` | [stock_analyzer/sector_activity_contract.py:34](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/sector_activity_contract.py:34) |
| SQL读 FROM/JOIN | `_cached_industry_contract` | [stock_analyzer/sector_activity_contract.py:496](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/sector_activity_contract.py:496) |
| SQL写 INSERT / SQL读 FROM/JOIN | `append_completed_snapshot_bars` | [stock_analyzer/swing_daily_data.py:220](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_daily_data.py:220) |
| SQL写 INSERT | `save_swing_daily_bars` | [stock_analyzer/swing_daily_data.py:261](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_daily_data.py:261) |
| SQL读 FROM/JOIN | `load_latest_bar_date` | [stock_analyzer/swing_daily_data.py:314](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_daily_data.py:314) |
| SQL读 FROM/JOIN | `recent_trade_dates` | [stock_analyzer/swing_intraday_data.py:169](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_intraday_data.py:169) |
| SQL读 FROM/JOIN | `load_swing_bars` | [stock_analyzer/swing_store.py:358](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:358) |

### swing_index_daily

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_index_daily` | [stock_analyzer/swing_daily_data.py:294](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_daily_data.py:294) |
| SQL读 FROM/JOIN | `load_index_closes` | [stock_analyzer/swing_store.py:393](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:393) |

### swing_feature_snapshot

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| 动态表名参数/常量引用 | `save_feature_snapshots` | [stock_analyzer/swing_store.py:91](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:91) |
| SQL读 FROM/JOIN | `load_feature_snapshot_map` | [stock_analyzer/swing_store.py:627](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:627) |

### swing_setup_snapshot

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `latest_setup_trade_date` | [stock_analyzer/swing_contract.py:641](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_contract.py:641) |
| SQL读 FROM/JOIN | `build_swing_stats_envelope` | [stock_analyzer/swing_contract.py:1703](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_contract.py:1703) |
| SQL读 FROM/JOIN | `latest_observation_codes` | [stock_analyzer/swing_intraday_data.py:185](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_intraday_data.py:185) |
| 动态表名参数/常量引用 | `save_setup_snapshots` | [stock_analyzer/swing_store.py:110](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:110) |
| SQL删 DELETE / SQL读 FROM/JOIN / 动态表名参数/常量引用 | `replace_daily_setup_snapshots` | [stock_analyzer/swing_store.py:132](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:132) |
| SQL读 FROM/JOIN | `load_setup_snapshots` | [stock_analyzer/swing_store.py:170](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:170) |
| SQL读 FROM/JOIN | `latest_setup_trade_date_before` | [stock_analyzer/swing_store.py:187](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:187) |
| SQL读 FROM/JOIN | `load_previous_setup_state` | [stock_analyzer/swing_store.py:204](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:204) |
| SQL读 FROM/JOIN | `load_setup_contexts` | [stock_analyzer/swing_store.py:224](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:224) |
| SQL读 FROM/JOIN | `observation_dates_count` | [stock_analyzer/swing_store.py:690](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:690) |
| SQL改 UPDATE | `update_setup_state` | [stock_analyzer/swing_store.py:709](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:709) |
| SQL改 UPDATE | `update_setup_states` | [stock_analyzer/swing_store.py:763](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:763) |

### swing_state_event

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `build_swing_history_envelope` | [stock_analyzer/swing_contract.py:1546](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_contract.py:1546) |
| SQL读 FROM/JOIN | `build_swing_stats_envelope` | [stock_analyzer/swing_contract.py:1703](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_contract.py:1703) |
| SQL写 INSERT | `record_state_event` | [stock_analyzer/swing_store.py:271](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:271) |
| SQL写 INSERT | `record_state_events` | [stock_analyzer/swing_store.py:289](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:289) |
| SQL读 FROM/JOIN | `load_state_events` | [stock_analyzer/swing_store.py:316](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:316) |
| SQL读 FROM/JOIN | `load_unsettled_events` | [stock_analyzer/swing_store.py:448](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:448) |

### swing_signal_outcome

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `build_swing_history_envelope` | [stock_analyzer/swing_contract.py:1546](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_contract.py:1546) |
| SQL读 FROM/JOIN | `build_swing_stats_envelope` | [stock_analyzer/swing_contract.py:1703](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_contract.py:1703) |
| 动态表名参数/常量引用 | `save_outcome` | [stock_analyzer/swing_store.py:436](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:436) |
| SQL读 FROM/JOIN | `load_unsettled_events` | [stock_analyzer/swing_store.py:448](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:448) |
| SQL读 FROM/JOIN | `load_outcomes` | [stock_analyzer/swing_store.py:836](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/swing_store.py:836) |

### us_market_snapshot

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_snapshot` | [stock_analyzer/us_market_store.py:13](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/us_market_store.py:13) |
| SQL读 FROM/JOIN | `latest_snapshot` | [stock_analyzer/us_market_store.py:52](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/us_market_store.py:52) |
| SQL读 FROM/JOIN | `snapshot_history` | [stock_analyzer/us_market_store.py:78](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/us_market_store.py:78) |

### us_market_calendar_event

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `upsert_calendar_events` | [stock_analyzer/us_market_store.py:93](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/us_market_store.py:93) |
| SQL删 DELETE / SQL读 FROM/JOIN | `delete_calendar_events_by_source` | [stock_analyzer/us_market_store.py:142](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/us_market_store.py:142) |
| SQL读 FROM/JOIN | `calendar_events` | [stock_analyzer/us_market_store.py:152](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/us_market_store.py:152) |

### us_market_calendar_run

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_calendar_run` | [stock_analyzer/us_market_store.py:171](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/us_market_store.py:171) |
| SQL读 FROM/JOIN | `latest_calendar_run` | [stock_analyzer/us_market_store.py:189](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/us_market_store.py:189) |

### watchlist_item

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `upsert_items` | [stock_analyzer/watchlist_store.py:209](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:209) |
| SQL读 FROM/JOIN | `list_items` | [stock_analyzer/watchlist_store.py:246](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:246) |
| SQL读 FROM/JOIN | `find_item` | [stock_analyzer/watchlist_store.py:270](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:270) |
| SQL改 UPDATE | `update_item` | [stock_analyzer/watchlist_store.py:284](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:284) |
| SQL改 UPDATE | `update_quotes` | [stock_analyzer/watchlist_store.py:309](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:309) |
| SQL读 FROM/JOIN | `current_revision` | [stock_analyzer/watchlist_store.py:337](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:337) |
| SQL读 FROM/JOIN | `latest_strategy_snapshot` | [stock_analyzer/watchlist_store.py:374](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:374) |

### watchlist_strategy_snapshot

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT / SQL删 DELETE / SQL读 FROM/JOIN | `save_strategy_snapshot` | [stock_analyzer/watchlist_store.py:346](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:346) |
| SQL读 FROM/JOIN | `latest_strategy_snapshot` | [stock_analyzer/watchlist_store.py:374](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:374) |

### watchlist_alert_event

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_alert_events` | [stock_analyzer/watchlist_store.py:400](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:400) |
| SQL改 UPDATE | `update_alert_deliveries` | [stock_analyzer/watchlist_store.py:434](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:434) |
| SQL读 FROM/JOIN | `list_alert_events` | [stock_analyzer/watchlist_store.py:451](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/watchlist_store.py:451) |

## marketNewsFeed

### events

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN / 动态表名参数/常量引用 | `load_events` | [src/research_feed/report_center.py:87](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/report_center.py:87) |
| 动态表名参数/常量引用 | `_compact_input` | [src/research_feed/report_center.py:147](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/report_center.py:147) |
| 动态表名参数/常量引用 | `call_llm` | [src/research_feed/report_center.py:283](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/report_center.py:283) |
| 动态表名参数/常量引用 | `run` | [src/research_feed/report_center.py:621](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/report_center.py:621) |
| SQL读 FROM/JOIN | `load_events` | [src/research_feed/report_doc.py:51](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/report_doc.py:51) |
| SQL写 INSERT | `upsert_event` | [src/research_feed/storage.py:311](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:311) |
| SQL改 UPDATE | `update_relevance` | [src/research_feed/storage.py:389](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:389) |
| SQL改 UPDATE | `upsert_signal` | [src/research_feed/storage.py:407](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:407) |
| SQL读 FROM/JOIN | `get_event_state` | [src/research_feed/storage.py:501](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:501) |
| SQL读 FROM/JOIN | `list_dashboard_research` | [src/research_feed/storage.py:576](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:576) |
| SQL读 FROM/JOIN | `build_briefing` | [src/research_feed/storage.py:812](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:812) |
| SQL改 UPDATE | `update_push_status` | [src/research_feed/storage.py:950](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:950) |
| SQL改 UPDATE | `update_pending_push_status` | [src/research_feed/storage.py:978](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:978) |
| SQL读 FROM/JOIN | `get_feishu_retention_candidates` | [src/research_feed/storage.py:1167](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1167) |
| SQL读 FROM/JOIN | `get_feishu_recency_candidates` | [src/research_feed/storage.py:1265](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1265) |
| SQL读 FROM/JOIN | `_recent_events` | [src/research_feed/trend_stock_report.py:94](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/trend_stock_report.py:94) |
| 动态表名参数/常量引用 | `_topic_stats` | [src/research_feed/trend_stock_report.py:115](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/trend_stock_report.py:115) |
| 动态表名参数/常量引用 | `build_candidates` | [src/research_feed/trend_stock_report.py:207](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/trend_stock_report.py:207) |

### signals

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `load_events` | [src/research_feed/report_center.py:87](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/report_center.py:87) |
| SQL读 FROM/JOIN | `load_events` | [src/research_feed/report_doc.py:51](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/report_doc.py:51) |
| 动态表名参数/常量引用 | `_migrate_signals` | [src/research_feed/storage.py:282](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:282) |
| SQL写 INSERT | `upsert_signal` | [src/research_feed/storage.py:407](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:407) |
| SQL读 FROM/JOIN | `get_signal_analysis` | [src/research_feed/storage.py:517](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:517) |
| SQL读 FROM/JOIN | `list_dashboard_research` | [src/research_feed/storage.py:576](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:576) |
| SQL读 FROM/JOIN | `build_briefing` | [src/research_feed/storage.py:812](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:812) |
| SQL读 FROM/JOIN | `get_feishu_retention_candidates` | [src/research_feed/storage.py:1167](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1167) |
| SQL读 FROM/JOIN | `_recent_events` | [src/research_feed/trend_stock_report.py:94](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/trend_stock_report.py:94) |

### topic_heat

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| 动态表名参数/常量引用 | `_upsert_topic_heat` | [src/research_feed/feishu_sync.py:357](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/feishu_sync.py:357) |
| 动态表名参数/常量引用 | `sync_pending` | [src/research_feed/feishu_sync.py:399](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/feishu_sync.py:399) |
| 动态表名参数/常量引用 | `refresh_recency_flags` | [src/research_feed/feishu_sync.py:480](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/feishu_sync.py:480) |
| 动态表名参数/常量引用 | `_queue_feishu_topic_heat` | [src/research_feed/monitor.py:1208](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/monitor.py:1208) |
| 动态表名参数/常量引用 | `_migrate_topic_heat` | [src/research_feed/storage.py:238](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:238) |
| SQL写 INSERT / SQL读 FROM/JOIN | `update_topic_heat` | [src/research_feed/storage.py:670](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:670) |
| SQL读 FROM/JOIN | `get_topic_heat_records` | [src/research_feed/storage.py:748](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:748) |
| SQL读 FROM/JOIN | `build_briefing` | [src/research_feed/storage.py:812](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:812) |
| 动态表名参数/常量引用 | `_should_enqueue_feishu_sync` | [src/research_feed/storage.py:1009](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1009) |
| SQL读 FROM/JOIN | `get_feishu_recency_candidates` | [src/research_feed/storage.py:1265](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1265) |

### ashare_map

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `_seed_default_ashare_map` | [src/research_feed/storage.py:295](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:295) |
| SQL读 FROM/JOIN | `ashare_names_for_topics` | [src/research_feed/storage.py:769](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:769) |
| SQL读 FROM/JOIN | `_mapped_stocks` | [src/research_feed/trend_stock_report.py:140](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/trend_stock_report.py:140) |

### daily_briefings

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `save_briefing` | [src/research_feed/storage.py:927](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:927) |

### source_runtime_state

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `get_source_runtime_state` | [src/research_feed/storage.py:142](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:142) |
| SQL写 INSERT | `mark_source_blocked` | [src/research_feed/storage.py:157](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:157) |
| SQL写 INSERT | `mark_source_healthy` | [src/research_feed/storage.py:211](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:211) |

### feishu_sync_queue

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL写 INSERT | `enqueue_feishu_sync` | [src/research_feed/storage.py:1031](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1031) |
| SQL读 FROM/JOIN | `get_pending_sync_items` | [src/research_feed/storage.py:1056](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1056) |
| SQL改 UPDATE | `mark_sync_success` | [src/research_feed/storage.py:1080](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1080) |
| SQL改 UPDATE / SQL读 FROM/JOIN | `mark_sync_failure` | [src/research_feed/storage.py:1098](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1098) |

### feishu_record_map

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `get_feishu_record_id` | [src/research_feed/storage.py:1126](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1126) |
| SQL写 INSERT | `save_feishu_record_id` | [src/research_feed/storage.py:1146](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1146) |
| SQL读 FROM/JOIN | `get_feishu_retention_candidates` | [src/research_feed/storage.py:1167](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1167) |
| SQL删 DELETE / SQL读 FROM/JOIN | `delete_feishu_record_mappings` | [src/research_feed/storage.py:1240](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1240) |
| SQL读 FROM/JOIN | `get_feishu_recency_candidates` | [src/research_feed/storage.py:1265](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/storage.py:1265) |

### x_watch_users

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `_x_user_counts` | [src/admin_api.py:77](/Users/mukun/work/workspace/stock/marketNewsFeed/src/admin_api.py:77) |
| SQL读 FROM/JOIN | `_x_users` | [src/admin_api.py:94](/Users/mukun/work/workspace/stock/marketNewsFeed/src/admin_api.py:94) |
| SQL写 INSERT / SQL改 UPDATE | `sync_list_members` | [src/x_watch/x_monitor.py:146](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:146) |
| SQL读 FROM/JOIN | `list_members_sync_due` | [src/x_watch/x_monitor.py:205](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:205) |
| SQL读 FROM/JOIN | `active_users` | [src/x_watch/x_monitor.py:239](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:239) |
| SQL改 UPDATE | `init_latest_post_id` | [src/x_watch/x_monitor.py:262](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:262) |
| SQL改 UPDATE | `update_latest_post_id` | [src/x_watch/x_monitor.py:319](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:319) |

### x_watch_posts

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `load_events` | [src/research_feed/report_center.py:87](/Users/mukun/work/workspace/stock/marketNewsFeed/src/research_feed/report_center.py:87) |
| 动态表名参数/常量引用 | `init_db` | [src/x_watch/x_monitor.py:93](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:93) |
| SQL写 INSERT / SQL读 FROM/JOIN | `store_post` | [src/x_watch/x_monitor.py:278](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:278) |
| SQL改 UPDATE | `save_analysis` | [src/x_watch/x_monitor.py:419](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:419) |
| SQL改 UPDATE | `update_push_status` | [src/x_watch/x_monitor.py:566](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:566) |
| SQL读 FROM/JOIN | `retry_failed_pushes` | [src/x_watch/x_monitor.py:636](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:636) |

### x_watch_api_usage

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| SQL读 FROM/JOIN | `_x_usage` | [src/admin_api.py:123](/Users/mukun/work/workspace/stock/marketNewsFeed/src/admin_api.py:123) |
| SQL读 FROM/JOIN | `_sync_x_list` | [src/admin_api.py:151](/Users/mukun/work/workspace/stock/marketNewsFeed/src/admin_api.py:151) |
| 动态表名参数/常量引用 | `init_db` | [src/x_watch/x_monitor.py:93](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:93) |
| SQL写 INSERT | `record_usage` | [src/x_watch/x_monitor.py:114](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:114) |
| SQL读 FROM/JOIN | `list_members_sync_due` | [src/x_watch/x_monitor.py:205](/Users/mukun/work/workspace/stock/marketNewsFeed/src/x_watch/x_monitor.py:205) |

## investment-research-dashboard

### dashboard_users

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM模型引用 | `_dashboard_user_record` | [backend/app/auth_api.py:62](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:62) |
| ORM模型引用 | `_auth_user_from_db` | [backend/app/auth_api.py:74](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:74) |
| ORM select / ORM模型引用 | `login` | [backend/app/auth_api.py:145](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:145) |
| ORM模型引用 | `change_password` | [backend/app/auth_api.py:180](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:180) |
| ORM select / ORM模型引用 | `list_users` | [backend/app/auth_api.py:204](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:204) |
| ORM构造对象（写入候选） / ORM模型引用 | `create_user` | [backend/app/auth_api.py:210](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:210) |
| ORM模型引用 | `update_user` | [backend/app/auth_api.py:234](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:234) |
| ORM insert / ORM模型引用 | `lifespan` | [backend/app/main.py:34](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/main.py:34) |

### captcha_challenges

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM delete / ORM构造对象（写入候选） / ORM模型引用 | `issue_captcha` | [backend/app/login_security.py:112](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/login_security.py:112) |
| ORM select / ORM模型引用 | `verify_captcha` | [backend/app/login_security.py:154](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/login_security.py:154) |
| ORM select / ORM模型引用 | `consume_captcha` | [backend/app/login_security.py:220](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/login_security.py:220) |

### login_attempts

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM模型引用 | `enforce_login_throttle` | [backend/app/login_security.py:192](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/login_security.py:192) |
| ORM delete / ORM构造对象（写入候选） / ORM模型引用 | `record_login_failure` | [backend/app/login_security.py:238](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/login_security.py:238) |
| ORM delete / ORM模型引用 | `clear_subject_failures` | [backend/app/login_security.py:246](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/login_security.py:246) |

### snapshots

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM select / ORM模型引用 | `system_version` | [backend/app/api.py:171](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:171) |
| ORM模型引用 | `data_status` | [backend/app/api.py:220](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:220) |
| ORM select / ORM模型引用 | `dashboard` | [backend/app/api.py:230](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:230) |
| ORM select / ORM模型引用 | `capital_flow` | [backend/app/api.py:274](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:274) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `seat_flow` | [backend/app/api.py:427](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:427) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `seat_flow_analysis` | [backend/app/api.py:509](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:509) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `limit_up_ladder` | [backend/app/api.py:588](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:588) |
| ORM select / ORM模型引用 | `archived` | [backend/app/api.py:600](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:600) |
| ORM模型引用 | `available_dates` | [backend/app/api.py:775](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:775) |
| ORM select / ORM模型引用 | `archived` | [backend/app/api.py:783](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:783) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `archive_and_return` | [backend/app/api.py:812](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:812) |
| ORM模型引用 | `_latest_us_snapshot` | [backend/app/api.py:1653](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1653) |
| ORM select / ORM模型引用 | `query` | [backend/app/api.py:1659](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1659) |
| ORM select / ORM模型引用 | `us_industry_history` | [backend/app/api.py:1732](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1732) |
| ORM select / ORM模型引用 | `_cached` | [backend/app/company_profiles.py:216](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/company_profiles.py:216) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `build_company_profile` | [backend/app/company_profiles.py:232](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/company_profiles.py:232) |
| ORM模型引用 | `_snapshot_reference` | [backend/app/decision_engine.py:37](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/decision_engine.py:37) |
| ORM模型引用 | `_stored_decision_input` | [backend/app/decision_engine.py:47](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/decision_engine.py:47) |
| ORM select / ORM模型引用 | `_latest_snapshot` | [backend/app/decision_engine.py:80](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/decision_engine.py:80) |
| ORM select / ORM模型引用 | `load_market_dashboard_inputs` | [backend/app/market_dashboard.py:21](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_dashboard.py:21) |
| ORM模型引用 | `present_stored_market_dashboard` | [backend/app/market_dashboard.py:102](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_dashboard.py:102) |
| ORM模型引用 | `compose_market_dashboard` | [backend/app/market_dashboard.py:116](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_dashboard.py:116) |
| ORM模型引用 | `available_snapshot_dates` | [backend/app/market_data_projection.py:74](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_data_projection.py:74) |
| ORM select / ORM模型引用 | `archived_snapshot` | [backend/app/market_data_projection.py:90](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_data_projection.py:90) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `sync_capital_flow_snapshot` | [backend/app/market_data_projection.py:108](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_data_projection.py:108) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `sync_short_selection_snapshot` | [backend/app/market_data_projection.py:146](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_data_projection.py:146) |
| ORM insert / ORM模型引用 | `sync_projection` | [backend/app/market_structure.py:177](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_structure.py:177) |
| ORM select / ORM模型引用 | `read_projection` | [backend/app/market_structure.py:208](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_structure.py:208) |
| ORM select / ORM模型引用 | `available_review_dates` | [backend/app/postmarket_review.py:28](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/postmarket_review.py:28) |
| ORM select / ORM模型引用 | `_snapshot` | [backend/app/postmarket_review.py:84](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/postmarket_review.py:84) |
| ORM模型引用 | `_derived_review` | [backend/app/postmarket_review.py:107](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/postmarket_review.py:107) |
| ORM select / ORM模型引用 | `_latest_real` | [backend/app/readiness.py:13](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/readiness.py:13) |
| ORM模型引用 | `_snapshot_result` | [backend/app/readiness.py:22](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/readiness.py:22) |
| ORM select / ORM模型引用 | `latest_snapshot` | [backend/app/seat_tracking.py:40](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking.py:40) |
| ORM构造对象（写入候选） / ORM模型引用 | `refresh_one` | [backend/app/seat_tracking.py:99](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking.py:99) |
| ORM模型引用 | `create_case` | [backend/app/seat_tracking_api.py:271](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:271) |
| ORM select / ORM模型引用 | `reviews` | [backend/app/seat_tracking_api.py:315](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:315) |
| ORM模型引用 | `analysis` | [backend/app/seat_tracking_api.py:370](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:370) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `outcomes` | [backend/app/seat_tracking_api.py:447](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:447) |
| ORM构造对象（写入候选） / ORM模型引用 | `_seed_us_market_demo` | [backend/app/seed.py:26](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seed.py:26) |
| ORM构造对象（写入候选） / ORM模型引用 | `seed_demo_data` | [backend/app/seed.py:71](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seed.py:71) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `_store_overnight` | [backend/app/us_market_sync.py:39](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/us_market_sync.py:39) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `_store_calendar` | [backend/app/us_market_sync.py:65](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/us_market_sync.py:65) |

### seat_subscriptions

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM select / ORM模型引用 | `refresh_subscribed` | [backend/app/seat_tracking.py:163](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking.py:163) |
| ORM模型引用 | `audit` | [backend/app/seat_tracking_api.py:90](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:90) |
| ORM select / ORM模型引用 | `subscriptions` | [backend/app/seat_tracking_api.py:142](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:142) |
| ORM insert / ORM select / ORM模型引用 | `subscribe` | [backend/app/seat_tracking_api.py:167](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:167) |
| ORM模型引用 | `update_subscription` | [backend/app/seat_tracking_api.py:199](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:199) |
| ORM select / ORM模型引用 | `reports` | [backend/app/seat_tracking_api.py:232](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:232) |

### seat_reviews

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM insert / ORM select / ORM模型引用 | `create_case` | [backend/app/seat_tracking_api.py:271](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:271) |
| ORM select / ORM模型引用 | `reviews` | [backend/app/seat_tracking_api.py:315](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:315) |
| ORM模型引用 | `update_review` | [backend/app/seat_tracking_api.py:353](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:353) |
| ORM insert / ORM select / ORM模型引用 | `analysis` | [backend/app/seat_tracking_api.py:370](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:370) |
| ORM模型引用 | `outcomes` | [backend/app/seat_tracking_api.py:447](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:447) |

### watchlist_items

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM select / ORM模型引用 | `swing_selection_candles` | [backend/app/api.py:883](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:883) |
| ORM select / ORM模型引用 | `watchlist` | [backend/app/api.py:979](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:979) |
| ORM模型引用 | `_watchlist_upstream_query` | [backend/app/api.py:991](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:991) |
| ORM select / ORM模型引用 | `search_watchlist_candidates` | [backend/app/api.py:1024](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1024) |
| ORM select / ORM模型引用 | `add_watchlist_item` | [backend/app/api.py:1063](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1063) |
| ORM模型引用 | `remove_watchlist_item` | [backend/app/api.py:1115](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1115) |
| ORM模型引用 | `restore_watchlist_item` | [backend/app/api.py:1147](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1147) |
| ORM select / ORM模型引用 | `watchlist_strategy_profiles` | [backend/app/api.py:1254](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1254) |
| ORM模型引用 | `update_watchlist` | [backend/app/api.py:1293](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1293) |
| ORM模型引用 | `_watchlist_score` | [backend/app/decision_engine.py:152](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/decision_engine.py:152) |
| ORM select / ORM模型引用 | `generate_latest_decisions` | [backend/app/decision_engine.py:219](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/decision_engine.py:219) |
| ORM构造对象（写入候选） / ORM模型引用 | `seed_demo_data` | [backend/app/seed.py:71](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seed.py:71) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `sync_watchlist` | [backend/app/watchlist_sync.py:109](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/watchlist_sync.py:109) |

### decisions

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM select / ORM模型引用 | `decisions` | [backend/app/api.py:1320](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1320) |
| ORM模型引用 | `decision_feedback` | [backend/app/api.py:1380](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1380) |
| ORM构造对象（写入候选） / ORM模型引用 | `_decision` | [backend/app/decision_engine.py:173](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/decision_engine.py:173) |
| ORM模型引用 | `generate_latest_decisions` | [backend/app/decision_engine.py:219](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/decision_engine.py:219) |
| ORM select / ORM模型引用 | `_derived_review` | [backend/app/postmarket_review.py:107](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/postmarket_review.py:107) |
| ORM构造对象（写入候选） / ORM模型引用 | `seed_demo_data` | [backend/app/seed.py:71](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seed.py:71) |

### market_events

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM select / ORM模型引用 | `events` | [backend/app/api.py:1403](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1403) |
| ORM模型引用 | `update_event` | [backend/app/api.py:1409](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1409) |
| ORM select / ORM模型引用 | `generate_latest_decisions` | [backend/app/decision_engine.py:219](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/decision_engine.py:219) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `sync_sector_events` | [backend/app/market_events.py:19](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_events.py:19) |
| ORM模型引用 | `_event_text` | [backend/app/postmarket_review.py:101](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/postmarket_review.py:101) |
| ORM select / ORM模型引用 | `_derived_review` | [backend/app/postmarket_review.py:107](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/postmarket_review.py:107) |
| ORM构造对象（写入候选） / ORM模型引用 | `seed_demo_data` | [backend/app/seed.py:71](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seed.py:71) |

### research_items

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM select / ORM模型引用 | `research` | [backend/app/api.py:1429](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1429) |
| ORM构造对象（写入候选） / ORM模型引用 | `create_research` | [backend/app/api.py:1555](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1555) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `sync_research` | [backend/app/research_sync.py:60](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/research_sync.py:60) |
| ORM构造对象（写入候选） / ORM模型引用 | `seed_demo_data` | [backend/app/seed.py:71](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seed.py:71) |

### reviews

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `update_review` | [backend/app/api.py:1598](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1598) |
| ORM select / ORM模型引用 | `available_review_dates` | [backend/app/postmarket_review.py:28](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/postmarket_review.py:28) |
| ORM模型引用 | `_stored_review` | [backend/app/postmarket_review.py:241](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/postmarket_review.py:241) |
| ORM select / ORM模型引用 | `build_postmarket_review` | [backend/app/postmarket_review.py:262](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/postmarket_review.py:262) |
| ORM构造对象（写入候选） / ORM模型引用 | `seed_demo_data` | [backend/app/seed.py:71](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seed.py:71) |

### decision_feedback

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM构造对象（写入候选） / ORM模型引用 | `decision_feedback` | [backend/app/api.py:1380](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1380) |

### audit_logs

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM构造对象（写入候选） / ORM模型引用 | `_sync_watchlist_after_mutation` | [backend/app/api.py:996](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:996) |
| ORM构造对象（写入候选） / ORM模型引用 | `update_watchlist` | [backend/app/api.py:1293](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1293) |
| ORM构造对象（写入候选） / ORM模型引用 | `generate_decisions` | [backend/app/api.py:1350](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1350) |
| ORM构造对象（写入候选） / ORM模型引用 | `decision_feedback` | [backend/app/api.py:1380](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1380) |
| ORM构造对象（写入候选） / ORM模型引用 | `update_event` | [backend/app/api.py:1409](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1409) |
| ORM构造对象（写入候选） / ORM模型引用 | `create_research` | [backend/app/api.py:1555](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1555) |
| ORM构造对象（写入候选） / ORM模型引用 | `update_review` | [backend/app/api.py:1598](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1598) |
| ORM select / ORM模型引用 | `audit` | [backend/app/api.py:1764](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1764) |
| ORM构造对象（写入候选） / ORM模型引用 | `record_research_sync_failure` | [backend/app/research_sync.py:45](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/research_sync.py:45) |
| ORM构造对象（写入候选） / ORM模型引用 | `sync_research` | [backend/app/research_sync.py:60](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/research_sync.py:60) |
| ORM构造对象（写入候选） / ORM模型引用 | `audit` | [backend/app/seat_tracking_api.py:90](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:90) |
| ORM构造对象（写入候选） / ORM模型引用 | `sync_us_market` | [backend/app/us_market_sync.py:92](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/us_market_sync.py:92) |
| ORM构造对象（写入候选） / ORM模型引用 | `record_us_market_sync_failure` | [backend/app/us_market_sync.py:167](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/us_market_sync.py:167) |
| ORM构造对象（写入候选） / ORM模型引用 | `record_watchlist_sync_failure` | [backend/app/watchlist_sync.py:86](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/watchlist_sync.py:86) |
| ORM构造对象（写入候选） / ORM模型引用 | `sync_watchlist` | [backend/app/watchlist_sync.py:109](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/watchlist_sync.py:109) |

### sync_states

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM select / ORM模型引用 | `system_version` | [backend/app/api.py:171](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:171) |
| ORM select / ORM模型引用 | `data_status` | [backend/app/api.py:220](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:220) |
| ORM select / ORM模型引用 | `sync_version` | [backend/app/api.py:1513](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1513) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `_record_projection_result` | [backend/app/market_data_projection.py:183](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_data_projection.py:183) |
| ORM select / ORM模型引用 | `read_projection` | [backend/app/market_structure.py:208](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_structure.py:208) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `refresh` | [backend/app/market_structure.py:392](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_structure.py:392) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `_sync_state` | [backend/app/research_sync.py:31](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/research_sync.py:31) |
| ORM select / ORM模型引用 | `state_for` | [backend/app/seat_tracking.py:56](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking.py:56) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `refresh_one` | [backend/app/seat_tracking.py:99](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking.py:99) |
| ORM构造对象（写入候选） / ORM模型引用 | `seed_demo_data` | [backend/app/seed.py:71](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seed.py:71) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `_sync_state` | [backend/app/us_market_sync.py:25](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/us_market_sync.py:25) |
| ORM select / ORM构造对象（写入候选） / ORM模型引用 | `_sync_state` | [backend/app/watchlist_sync.py:72](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/watchlist_sync.py:72) |

### sector_scores

| 操作证据 | 函数 | 源文件 |
| --- | --- | --- |
| ORM select / ORM模型引用 | `sectors` | [backend/app/api.py:329](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:329) |
| ORM select / ORM模型引用 | `generate_latest_decisions` | [backend/app/decision_engine.py:219](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/decision_engine.py:219) |
| ORM构造对象（写入候选） / ORM模型引用 | `seed_demo_data` | [backend/app/seed.py:71](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seed.py:71) |
