# 数据API—函数—调用符号索引（细化版）

核对日期2026-10-13。FastAPI装饰器路由从源码提取，包含业务、认证及运维端点；不等于每条端点都已生产启用或每个动态分支都有独立契约。

marketNewsFeed使用HTTP Handler分派而非FastAPI装饰器，research GET及通知链路见业务手册，不用0条装饰器路由表示无API。参数来自Python签名：Depends注入不是浏览器参数；认证、请求schema及响应嵌套字段须继续阅读对应模型。运行在/API版本前缀下的router已组合实际挂载前缀。

“调用符号”是直接源码调用，不是已证明的全链路；通过构建器/客户端/依赖注入间接使用的表不会自动列为直接表引用。

## stock-analyzer（34个装饰器端点）

### GET /api/health

处理函数：[health](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:395)。返回注解：`dict[str, Any]`。

```python
health()
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/stocks/search

处理函数：[search](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:406)。返回注解：`dict[str, Any]`。

```python
search(payload: SearchRequest)
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/stocks/add

处理函数：[add](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:413)。返回注解：`dict[str, Any]`。

```python
add(payload: AddStockRequest, background_tasks: BackgroundTasks)
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/stocks

处理函数：[list_stocks](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:433)。返回注解：`dict[str, Any]`。

```python
list_stocks(attention: Attention | None=None, include_paused: bool=False, limit: int=Query(default=200, ge=1, le=500))
```

数据相关直接调用：`_record_to_stock`、`watchlist_store.list_items`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/watchlist

处理函数：[investment_dashboard_watchlist](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:449)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_watchlist(include_paused: bool=True, refresh_quotes: bool=False, limit: int=Query(default=500, ge=1, le=500))
```

数据相关直接调用：`build_dashboard_watchlist_record`、`load_security_classifications`、`watchlist_store.list_items`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/company-profile/{code}

处理函数：[investment_dashboard_company_profile](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:498)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_company_profile(code: str)
```

数据相关直接调用：`fetch_industry`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/nextday-watch

处理函数：[investment_dashboard_nextday_watch](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:521)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_nextday_watch()
```

数据相关直接调用：`build_dashboard_nextday_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/short-selection/candles

处理函数：[investment_dashboard_short_selection_candles](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:574)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_short_selection_candles(code: str=Query(min_length=6, max_length=6, pattern='^\\d{6}$'), end_date: str | None=Query(default=None), days: int=Query(default=60, ge=20, le=120))
```

数据相关直接调用：`_selection_candles_payload`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/stocks/{code}/candles

处理函数：[investment_dashboard_stock_candles](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:584)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_stock_candles(code: str, end_date: str | None=Query(default=None), days: int=Query(default=60, ge=20, le=120))
```

数据相关直接调用：`_selection_candles_payload`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/seat-directory

处理函数：[investment_dashboard_seat_directory](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:597)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_seat_directory(query: str=Query(min_length=1, max_length=80), observation_date: date | None=None, limit: int=Query(default=20, ge=1, le=50))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/seat-case

处理函数：[investment_dashboard_seat_case](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:611)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_seat_case(code: str=Query(pattern='^\\d{6}$'), event_date: date=Query(), as_of: date | None=None)
```

数据相关直接调用：`build_case_outcome`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/seat-tracking

处理函数：[investment_dashboard_seat_tracking](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:623)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_seat_tracking(query: str=Query(min_length=1, max_length=80), observation_date: date | None=None, window: int=Query(default=20, ge=5, le=120), start_date: date | None=None)
```

数据相关直接调用：`build_tracking_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/seat-flow

处理函数：[investment_dashboard_seat_flow](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:644)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_seat_flow(query: str=Query(min_length=1, max_length=80), observation_date: date | None=None, days: int=Query(default=90, ge=7, le=180))
```

数据相关直接调用：`build_seat_flow_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/stocks/{code}/bars

处理函数：[investment_dashboard_stock_bars](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:664)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_stock_bars(code: str, period: Literal['day', 'week', 'month']='day', observation_date: date | None=None, before: date | None=None, limit: int=Query(default=60, ge=20, le=120))
```

数据相关直接调用：`build_stock_bars_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/limit-up-ladder

处理函数：[investment_dashboard_limit_up_ladder](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:694)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_limit_up_ladder(observation_date: date | None=None, days: int=Query(default=5, ge=1, le=20))
```

数据相关直接调用：`build_limit_up_ladder_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/short-selection

处理函数：[investment_dashboard_short_selection](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:748)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_short_selection()
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/watchlist/strategy-profiles

处理函数：[investment_dashboard_watchlist_strategy_profiles](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:773)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_watchlist_strategy_profiles()
```

数据相关直接调用：`watchlist_store.latest_strategy_snapshot`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/market-regime

处理函数：[investment_dashboard_market_regime](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:785)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_market_regime()
```

数据相关直接调用：`build_market_regime_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/short-selection/history

处理函数：[investment_dashboard_short_selection_history](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:805)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_short_selection_history(limit: int=Query(default=100, ge=1, le=500))
```

数据相关直接调用：`.fetchone`

直接表/ORM引用：`events`、`short_signal_event`

### GET /api/integrations/investment-dashboard/swing-selection

处理函数：[investment_dashboard_swing_selection](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:844)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_swing_selection(trade_date: date | None=Query(default=None), pattern: str | None=Query(default=None), state: str | None=Query(default=None), grade: str | None=Query(default=None), industry: str | None=Query(default=None), min_score: float | None=Query(default=None, ge=0, le=100), strategy_path: str | None=Query(default=None), path_role: Literal['primary', 'any']=Query(default='primary'), lifecycle_stage: str | None=Query(default=None), confirmation_state: str | None=Query(default=None), participation_decision: str | None=Query(default=None), contract_version: str=Query(default=CONTRACT_SELECTION), limit: int=Query(default=20000, ge=1, le=20000), cursor: int=Query(default=0, ge=0))
```

数据相关直接调用：`build_swing_selection_envelope`、`build_swing_selection_v3_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/swing-selection/candles

处理函数：[investment_dashboard_swing_selection_candles](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:924)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_swing_selection_candles(code: str=Query(min_length=6, max_length=6, pattern='^\\d{6}$'), end_date: str | None=Query(default=None), days: int=Query(default=60, ge=20, le=120))
```

数据相关直接调用：`_selection_candles_payload`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/swing-selection/history

处理函数：[investment_dashboard_swing_selection_history](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:936)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_swing_selection_history(date_from: str | None=Query(default=None), date_to: str | None=Query(default=None), code: str | None=Query(default=None), pattern: str | None=Query(default=None), settled_only: bool=Query(default=False), rules_version: str | None=Query(default=None), limit: int=Query(default=500, ge=1, le=2000))
```

数据相关直接调用：`build_swing_history_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/swing-selection/stats

处理函数：[investment_dashboard_swing_selection_stats](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:966)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_swing_selection_stats()
```

数据相关直接调用：`build_swing_stats_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/capital-flow

处理函数：[investment_dashboard_capital_flow](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:986)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_capital_flow()
```

数据相关直接调用：`build_capital_flow_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/sector-workbench

处理函数：[investment_dashboard_sector_workbench](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:998)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_sector_workbench(category: Literal['行业', '概念']=Query(default='行业'), days: int=Query(default=60, ge=20, le=180), sector: str | None=Query(default=None, max_length=80))
```

数据相关直接调用：`build_sector_workbench_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/us-market/overnight

处理函数：[investment_dashboard_us_market_overnight](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:1021)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_us_market_overnight(trade_date: str | None=Query(default=None, pattern='^\\d{4}-\\d{2}-\\d{2}$'))
```

数据相关直接调用：`build_overnight_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/us-market/calendar

处理函数：[investment_dashboard_us_market_calendar](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:1049)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_us_market_calendar(date_from: Annotated[date, Query(alias='from')], date_to: Annotated[date, Query(alias='to')])
```

数据相关直接调用：`build_calendar_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/us-market/history

处理函数：[investment_dashboard_us_market_history](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:1075)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_us_market_history(limit: int=Query(default=30, ge=1, le=180))
```

数据相关直接调用：`build_history_envelope`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/monitor

处理函数：[investment_dashboard_monitor](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:1102)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_monitor(alert_limit: int=Query(default=50, ge=1, le=100))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/stocks/{query}

处理函数：[get_stock](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:1135)。返回注解：`dict[str, Any]`。

```python
get_stock(query: str, live: bool=False)
```

数据相关直接调用：`_fetch_live_quote`、`_record_to_stock`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/stocks/{query}/update

处理函数：[update_stock](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:1151)。返回注解：`dict[str, Any]`。

```python
update_stock(query: str, payload: StockUpdateRequest, background_tasks: BackgroundTasks)
```

数据相关直接调用：`_record_to_stock`、`_update_record`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/stocks/{query}/remove

处理函数：[remove_stock](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:1178)。返回注解：`dict[str, Any]`。

```python
remove_stock(query: str, background_tasks: BackgroundTasks, payload: RemoveStockRequest | None=None)
```

数据相关直接调用：`_record_to_stock`、`_update_record`、`record.get`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/alerts/recent

处理函数：[recent_alerts](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:1199)。返回注解：`dict[str, Any]`。

```python
recent_alerts(limit: int=Query(default=20, ge=1, le=100))
```

数据相关直接调用：`watchlist_store.list_alert_events`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/integrations/investment-dashboard/market-structure

处理函数：[investment_dashboard_market_structure](/Users/mukun/.codex/worktrees/market-structure-etf/stock-analyzer/stock_analyzer/api.py:1205)。返回注解：`dict[str, Any]`。

```python
investment_dashboard_market_structure(as_of: date | None=None, lookback: int=Query(default=120, ge=5, le=120), mode: Literal['known', 'rebuilt']='rebuilt')
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

## investment-research-dashboard（76个装饰器端点）

### GET /api/v1/health

处理函数：[health](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:152)。返回注解：`dict[str, str]`。

```python
health(db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/readiness

处理函数：[readiness](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:158)。返回注解：`未声明`。

```python
readiness(db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/system/version

处理函数：[system_version](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:171)。返回注解：`dict`。

```python
system_version(db: Session=Depends(get_db))
```

数据相关直接调用：`build_metadata`、`capital_version_snapshot.payload.get`、`item.payload.get`

直接表/ORM引用：`snapshots`、`sync_states`

### GET /api/v1/data-status

处理函数：[data_status](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:220)。返回注解：`dict`。

```python
data_status(db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`snapshots`、`sync_states`

### GET /api/v1/dashboard/{session}

处理函数：[dashboard](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:230)。返回注解：`dict`。

```python
dashboard(session: str, db: Session=Depends(get_db))
```

数据相关直接调用：`compose_market_dashboard`、`load_market_dashboard_inputs`、`present_stored_market_dashboard`

直接表/ORM引用：`snapshots`

### GET /api/v1/capital-flow

处理函数：[capital_flow](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:274)。返回注解：`dict`。

```python
capital_flow(trade_date: date | None=None, db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`archived_snapshot`、`payload.get`、`sync_capital_flow_snapshot`

直接表/ORM引用：`snapshots`

### GET /api/v1/sectors

处理函数：[sectors](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:329)。返回注解：`list[dict]`。

```python
sectors(category: str | None=None, db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`sector_scores`

### GET /api/v1/sector-workbench

处理函数：[sector_workbench](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:337)。返回注解：`dict`。

```python
sector_workbench(category: str='行业', days: int=Query(default=60, ge=20, le=180), sector: str | None=Query(default=None, max_length=80), stock_client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`stock_client.fetch_sector_workbench`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/v1/company-profiles/{code}

处理函数：[company_profile](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:358)。返回注解：`dict`。

```python
company_profile(code: str, payload: CompanyProfileRequest, refresh: bool=False, db: Session=Depends(get_db), stock_client: StockAnalyzerClient=Depends(get_stock_analyzer_client), ai_client: DeepSeekClient=Depends(get_deepseek_client))
```

数据相关直接调用：`build_company_profile`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/short-selection

处理函数：[short_selection](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:381)。返回注解：`dict`。

```python
short_selection(trade_date: date | None=None, db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`archived_snapshot`、`sync_short_selection_snapshot`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/seat-flow

处理函数：[seat_flow](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:427)。返回注解：`未声明`。

```python
seat_flow(query: str=Query(default='紫阳东路', min_length=1, max_length=80), observation_date: date | None=None, days: int=Query(default=90, ge=7, le=180), client: StockAnalyzerClient=Depends(get_stock_analyzer_client), db: Session=Depends(get_db))
```

数据相关直接调用：`client.fetch_seat_flow`、`snapshot.payload.get`

直接表/ORM引用：`snapshots`

### POST /api/v1/seat-flow/analysis

处理函数：[seat_flow_analysis](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:509)。返回注解：`dict`。

```python
seat_flow_analysis(request: SeatFlowAIRequest, db: Session=Depends(get_db), ai_client: SeatFlowAIClient=Depends(get_seat_flow_ai_client))
```

数据相关直接调用：`ai_client.generate`、`ai_client.model.encode`、`result_payload`、`snapshot.payload.get`

直接表/ORM引用：`snapshots`

### GET /api/v1/limit-up-ladder

处理函数：[limit_up_ladder](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:588)。返回注解：`dict`。

```python
limit_up_ladder(observation_date: date | None=None, days: int=Query(default=5, ge=1, le=20), db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`archived`、`client.fetch_limit_up_ladder`、`payload.get`

直接表/ORM引用：`snapshots`

### GET /api/v1/stocks/{code}/candles

处理函数：[stock_candles](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:674)。返回注解：`dict`。

```python
stock_candles(code: str, trade_date: date | None=None, days: int=Query(default=60, ge=20, le=120), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`client.fetch_stock_candles`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/stocks/{code}/bars

处理函数：[stock_bars](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:699)。返回注解：`dict`。

```python
stock_bars(code: str, period: Literal['day', 'week', 'month']='day', observation_date: date | None=None, before: date | None=None, limit: int=Query(default=60, ge=20, le=120), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`client.fetch_stock_bars`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/short-selection/{code}/candles

处理函数：[short_selection_candles](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:727)。返回注解：`dict`。

```python
short_selection_candles(code: str, trade_date: date | None=None, days: int=Query(default=60, ge=20, le=120), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`client.fetch_short_selection_candles`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/swing-selection

处理函数：[swing_selection](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:752)。返回注解：`dict`。

```python
swing_selection(trade_date: date | None=None, strategy_path: str | None=None, path_role: str='primary', lifecycle_stage: str | None=None, confirmation_state: str | None=None, participation_decision: str | None=None, industry: str | None=None, limit: int=20000, cursor: int=0, db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`archive_and_return`、`archived`、`client.fetch_swing_selection`、`payload.get`、`swing_selection_payload`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/swing-selection/{code}/candles

处理函数：[swing_selection_candles](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:883)。返回注解：`dict`。

```python
swing_selection_candles(code: str, trade_date: date | None=None, days: int=Query(default=60, ge=20, le=120), db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`client.fetch_swing_candles`、`selection_candles_payload`

直接表/ORM引用：`watchlist_items`

### GET /api/v1/swing-selection/stats

处理函数：[swing_selection_stats](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:928)。返回注解：`dict`。

```python
swing_selection_stats(client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`client.fetch_swing_stats`、`swing_stats_payload`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/swing-selection/history

处理函数：[swing_selection_history](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:946)。返回注解：`dict`。

```python
swing_selection_history(date_from: str | None=Query(default=None), date_to: str | None=Query(default=None), code: str | None=Query(default=None), pattern: str | None=Query(default=None), settled_only: bool=Query(default=False), rules_version: str | None=Query(default=None), limit: int=Query(default=500, ge=1, le=2000), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`client.fetch_swing_history`、`swing_history_payload`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/watchlist

处理函数：[watchlist](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:979)。返回注解：`list[dict]`。

```python
watchlist(board: str | None=None, db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`watchlist_items`

### POST /api/v1/watchlist/search

处理函数：[search_watchlist_candidates](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1024)。返回注解：`dict`。

```python
search_watchlist_candidates(payload: WatchlistSearchIn, db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`client.search_stocks`

直接表/ORM引用：`watchlist_items`

### POST /api/v1/watchlist

处理函数：[add_watchlist_item](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1063)。返回注解：`dict`。

```python
add_watchlist_item(payload: WatchlistAddIn, db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`_sync_watchlist_after_mutation`、`client.add_stock`、`client.restore_stock`、`payload.reason.strip`

直接表/ORM引用：`watchlist_items`

### DELETE /api/v1/watchlist/{item_id}

处理函数：[remove_watchlist_item](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1115)。返回注解：`dict`。

```python
remove_watchlist_item(item_id: UUID, payload: WatchlistRemoveIn | None=None, db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`_sync_watchlist_after_mutation`、`client.remove_stock`、`payload.reason.strip`

直接表/ORM引用：`watchlist_items`

### POST /api/v1/watchlist/{item_id}/restore

处理函数：[restore_watchlist_item](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1147)。返回注解：`dict`。

```python
restore_watchlist_item(item_id: UUID, payload: WatchlistRestoreIn, db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`_sync_watchlist_after_mutation`、`client.restore_stock`

直接表/ORM引用：`watchlist_items`

### POST /api/v1/watchlist/sync

处理函数：[sync_watchlist_from_upstream](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1183)。返回注解：`dict`。

```python
sync_watchlist_from_upstream(db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`record_watchlist_sync_failure`、`sync_watchlist`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/watchlist/monitor

处理函数：[watchlist_monitor](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1207)。返回注解：`dict`。

```python
watchlist_monitor(alert_limit: int=Query(default=50, ge=1, le=100), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`client.fetch_monitor`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/watchlist/nextday-strategy

处理函数：[watchlist_nextday_strategy](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1220)。返回注解：`dict`。

```python
watchlist_nextday_strategy(client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`client.fetch_nextday_strategy`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/watchlist/rule-profiles

处理函数：[watchlist_rule_profiles](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1232)。返回注解：`dict`。

```python
watchlist_rule_profiles(trade_date: str | None=None)
```

数据相关直接调用：`rule_profile_payload`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/watchlist/strategy-profiles

处理函数：[watchlist_strategy_profiles](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1254)。返回注解：`dict`。

```python
watchlist_strategy_profiles(trade_date: str | None=None, db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`client.fetch_watchlist_strategy_profiles`、`strategy_profile_payload`

直接表/ORM引用：`watchlist_items`

### PATCH /api/v1/watchlist/{item_id}

处理函数：[update_watchlist](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1293)。返回注解：`dict`。

```python
update_watchlist(item_id: UUID, payload: WatchlistUpdate, db: Session=Depends(get_db))
```

数据相关直接调用：`payload.model_dump`

直接表/ORM引用：`audit_logs`、`watchlist_items`

### GET /api/v1/decisions

处理函数：[decisions](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1320)。返回注解：`list[dict]`。

```python
decisions(latest_only: bool=True, strategy_type: str | None=Query(default=None, pattern='^(intraday|next_day)$'), db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`decisions`

### POST /api/v1/decisions/generate

处理函数：[generate_decisions](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1350)。返回注解：`list[dict]`。

```python
generate_decisions(strategy_type: str=Query(default='intraday', pattern='^(intraday|next_day)$'), db: Session=Depends(get_db))
```

数据相关直接调用：`generate_latest_decisions`

直接表/ORM引用：`audit_logs`

### POST /api/v1/decisions/{decision_id}/feedback

处理函数：[decision_feedback](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1380)。返回注解：`dict`。

```python
decision_feedback(decision_id: UUID, payload: DecisionFeedbackIn, db: Session=Depends(get_db))
```

数据相关直接调用：`payload.model_dump`

直接表/ORM引用：`audit_logs`、`decision_feedback`、`decisions`

### GET /api/v1/events

处理函数：[events](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1403)。返回注解：`list[dict]`。

```python
events(db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`market_events`

### PATCH /api/v1/events/{event_id}

处理函数：[update_event](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1409)。返回注解：`dict`。

```python
update_event(event_id: UUID, payload: EventStatusUpdate, db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`audit_logs`、`market_events`

### GET /api/v1/research

处理函数：[research](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1429)。返回注解：`list[dict]`。

```python
research(min_level: int=Query(default=2, ge=1, le=5), limit: int=Query(default=500, ge=1, le=500), db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`research_items`

### POST /api/v1/research/sync

处理函数：[sync_research_from_upstream](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1448)。返回注解：`dict`。

```python
sync_research_from_upstream(min_level: int=Query(default=2, ge=1, le=5), db: Session=Depends(get_db), client: MarketNewsFeedClient=Depends(get_market_news_feed_client))
```

数据相关直接调用：`record_research_sync_failure`、`sync_research`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/v1/research/webhook

处理函数：[research_webhook](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1474)。返回注解：`dict`。

```python
research_webhook(x_webhook_secret: str=Header(default=''), db: Session=Depends(get_db), client: MarketNewsFeedClient=Depends(get_market_news_feed_client))
```

数据相关直接调用：`_research_sync_lock.acquire`、`_research_sync_lock.release`、`record_research_sync_failure`、`sync_research`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/research/stream

处理函数：[research_stream](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1510)。返回注解：`StreamingResponse`。

```python
research_stream(request: Request)
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/v1/research

处理函数：[create_research](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1555)。返回注解：`dict`。

```python
create_research(payload: ResearchCreate, db: Session=Depends(get_db))
```

数据相关直接调用：`payload.model_dump`

直接表/ORM引用：`audit_logs`、`research_items`

### GET /api/v1/reviews/latest

处理函数：[latest_review](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1575)。返回注解：`dict`。

```python
latest_review(db: Session=Depends(get_db))
```

数据相关直接调用：`build_postmarket_review`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/reviews/{observation_date}

处理函数：[review](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1586)。返回注解：`dict`。

```python
review(observation_date: date, db: Session=Depends(get_db))
```

数据相关直接调用：`build_postmarket_review`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### PATCH /api/v1/reviews/{trading_date}

处理函数：[update_review](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1598)。返回注解：`dict`。

```python
update_review(trading_date: date, payload: ReviewUpdate, db: Session=Depends(get_db))
```

数据相关直接调用：`build_postmarket_review`、`payload.model_dump`

直接表/ORM引用：`audit_logs`、`reviews`

### GET /api/v1/us-industries

处理函数：[us_industries](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1687)。返回注解：`dict`。

```python
us_industries(observation_date: date | None=Query(default=None, alias='date'), db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/us-industries/overnight

处理函数：[us_industries](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1687)。返回注解：`dict`。

```python
us_industries(observation_date: date | None=Query(default=None, alias='date'), db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/us-industries/calendar

处理函数：[us_industry_calendar](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1706)。返回注解：`dict`。

```python
us_industry_calendar(date_from: date | None=Query(default=None, alias='from'), date_to: date | None=Query(default=None, alias='to'), db: Session=Depends(get_db))
```

数据相关直接调用：`payload.get`

直接表/ORM引用：`events`

### GET /api/v1/us-industries/history

处理函数：[us_industry_history](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1732)。返回注解：`dict`。

```python
us_industry_history(limit: int=Query(default=30, ge=1, le=180), db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`snapshots`

### POST /api/v1/us-industries/sync

处理函数：[sync_us_industries](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1752)。返回注解：`dict`。

```python
sync_us_industries(db: Session=Depends(get_db), client: StockAnalyzerClient=Depends(get_stock_analyzer_client))
```

数据相关直接调用：`record_us_market_sync_failure`、`sync_us_market`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/audit

处理函数：[audit](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/api.py:1764)。返回注解：`list[dict]`。

```python
audit(limit: int=Query(default=50, ge=1, le=200), db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`audit_logs`

### GET /api/v1/auth/config

处理函数：[auth_config](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:95)。返回注解：`dict`。

```python
auth_config()
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/auth/me

处理函数：[auth_me](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:106)。返回注解：`dict`。

```python
auth_me(request: Request)
```

数据相关直接调用：`_user_payload`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/auth/captcha

处理函数：[captcha](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:122)。返回注解：`dict`。

```python
captcha(request: Request, width: int=Query(default=320, ge=260, le=420), height: int=Query(default=150, ge=130, le=180), db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/v1/auth/captcha/verify

处理函数：[captcha_verify](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:135)。返回注解：`dict`。

```python
captcha_verify(payload: CaptchaVerifyIn, request: Request, db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/v1/auth/login

处理函数：[login](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:145)。返回注解：`dict`。

```python
login(payload: LoginIn, request: Request, response: Response, db: Session=Depends(get_db))
```

数据相关直接调用：`_user_payload`、`payload.username.strip`、`record_login_failure`

直接表/ORM引用：`dashboard_users`

### POST /api/v1/auth/change-password

处理函数：[change_password](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:180)。返回注解：`Response`。

```python
change_password(payload: ChangePasswordIn, request: Request, db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`dashboard_users`

### GET /api/v1/auth/users

处理函数：[list_users](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:204)。返回注解：`list[dict]`。

```python
list_users(_: AuthUser=Depends(require_admin), db: Session=Depends(get_db))
```

数据相关直接调用：`_dashboard_user_record`

直接表/ORM引用：`dashboard_users`

### POST /api/v1/auth/users

处理函数：[create_user](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:210)。返回注解：`dict`。

```python
create_user(payload: UserCreateIn, _: AuthUser=Depends(require_admin), db: Session=Depends(get_db))
```

数据相关直接调用：`_dashboard_user_record`、`payload.display_name.strip`、`payload.username.strip`

直接表/ORM引用：`dashboard_users`

### PATCH /api/v1/auth/users/{user_id}

处理函数：[update_user](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:234)。返回注解：`dict`。

```python
update_user(user_id: UUID, payload: UserUpdateIn, _: AuthUser=Depends(require_admin), db: Session=Depends(get_db))
```

数据相关直接调用：`_dashboard_user_record`、`payload.display_name.strip`

直接表/ORM引用：`dashboard_users`

### GET /api/v1/auth/feishu/login

处理函数：[feishu_login](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:270)。返回注解：`RedirectResponse`。

```python
feishu_login(request: Request, next: str='/dashboard')
```

数据相关直接调用：`build_feishu_authorize_url`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/auth/feishu/callback

处理函数：[feishu_callback](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:286)。返回注解：`RedirectResponse`。

```python
feishu_callback(request: Request, code: str | None=None, state: str | None=None)
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/v1/auth/logout

处理函数：[logout](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/auth_api.py:316)。返回注解：`Response`。

```python
logout()
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/

处理函数：[root](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/main.py:162)。返回注解：`dict[str, str]`。

```python
root()
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/market-structure/overview

处理函数：[overview](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_structure.py:298)。返回注解：`dict`。

```python
overview(data: dict=Depends(read))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/market-structure/{section:path}

处理函数：[section](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/market_structure.py:303)。返回注解：`dict`。

```python
section(section: str, window: int=Query(default=5, ge=1, le=20), data: dict=Depends(read))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### GET /api/v1/seat-tracking/subscriptions

处理函数：[subscriptions](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:142)。返回注解：`未声明`。

```python
subscriptions(request: Request, db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`seat_subscriptions`

### GET /api/v1/seat-tracking/directory

处理函数：[directory](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:159)。返回注解：`未声明`。

```python
directory(query: str=Query(min_length=1, max_length=80), client=Depends(get_client))
```

数据相关直接调用：`fetch_directory`

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/v1/seat-tracking/subscriptions

处理函数：[subscribe](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:167)。返回注解：`未声明`。

```python
subscribe(body: SubscriptionIn, db: Session=Depends(get_db), client=Depends(get_client))
```

数据相关直接调用：`fetch_directory`

直接表/ORM引用：`seat_subscriptions`

### PATCH /api/v1/seat-tracking/subscriptions/{subscription_id}

处理函数：[update_subscription](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:199)。返回注解：`未声明`。

```python
update_subscription(subscription_id: UUID, body: SubscriptionUpdate, db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`seat_subscriptions`

### GET /api/v1/seat-tracking/reports

处理函数：[reports](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:232)。返回注解：`未声明`。

```python
reports(observation_date: date | None=None, window: int=Query(default=20, ge=5, le=120), start_date: date | None=None, db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`seat_subscriptions`

### POST /api/v1/seat-tracking/refresh

处理函数：[refresh](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:256)。返回注解：`未声明`。

```python
refresh(body: RefreshIn)
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：未发现直接引用；可能通过依赖/构建器访问。

### POST /api/v1/seat-tracking/cases

处理函数：[create_case](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:271)。返回注解：`未声明`。

```python
create_case(body: CaseIn, db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`seat_reviews`、`snapshots`

### GET /api/v1/seat-tracking/reviews

处理函数：[reviews](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:315)。返回注解：`未声明`。

```python
reviews(kind: Literal['case', 'analysis'] | None=None, code: str | None=None, observation_date: date | None=None, favorite: bool=False, stock: str | None=Query(default=None, pattern='^\\d{6}$'), offset: int=Query(default=0, ge=0, le=5000), db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`seat_reviews`、`snapshots`

### PATCH /api/v1/seat-tracking/reviews/{review_id}

处理函数：[update_review](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:353)。返回注解：`未声明`。

```python
update_review(review_id: UUID, body: ReviewUpdate, db: Session=Depends(get_db))
```

数据相关直接调用：未发现命中符号；沿源函数查看。

直接表/ORM引用：`seat_reviews`

### POST /api/v1/seat-tracking/analysis

处理函数：[analysis](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:370)。返回注解：`未声明`。

```python
analysis(body: AnalysisIn, db: Session=Depends(get_db), ai=Depends(get_ai))
```

数据相关直接调用：`generate`

直接表/ORM引用：`seat_reviews`、`snapshots`

### POST /api/v1/seat-tracking/reviews/{review_id}/outcomes

处理函数：[outcomes](/Users/mukun/.codex/worktrees/market-structure-etf/investment-research-dashboard/backend/app/seat_tracking_api.py:447)。返回注解：`未声明`。

```python
outcomes(review_id: UUID, body: OutcomesIn, db: Session=Depends(get_db), client=Depends(get_client))
```

数据相关直接调用：`fetch_case`、`fetch_tracking`

直接表/ORM引用：`seat_reviews`、`snapshots`
