# 全部线上 HTTP 耗时观察

每行是一条真实请求；同一路由不同时间/参数的结果不构成受控 A/B 测试。秒数不是 P95。字节为内网未压缩响应，公网为实际线缆字节。

## Dashboard 容器内第一轮

| 服务 | GET 路径与参数 | 秒 | HTTP | 字节 |
| --- | --- | ---: | ---: | ---: |
| dashboard | `/api/v1/health` | 0.008 | 200 | 39 |
| dashboard | `/api/v1/readiness` | 0.012 | 200 | 746 |
| dashboard | `/api/v1/system/version` | 0.048 | 200 | 3756 |
| dashboard | `/api/v1/data-status` | 0.011 | 200 | 7682 |
| dashboard | `/api/v1/swing-selection` | 6.115 | 200 | 3992947 |
| dashboard | `/api/v1/swing-selection?trade_date=2026-10-20` | 4.503 | 200 | 3934695 |
| dashboard | `/api/v1/swing-selection/stats` | 4.746 | 200 | 5798 |
| dashboard | `/api/v1/swing-selection/history` | 0.400 | 200 | 429292 |
| dashboard | `/api/v1/short-selection` | 6.324 | 200 | 20381 |
| dashboard | `/api/v1/short-selection/tracking` | 0.230 | 200 | 1070 |
| dashboard | `/api/v1/short-selection/stats` | 0.270 | 200 | 2610 |
| dashboard | `/api/v1/stocks/300188/bars` | 37.308 | 200 | 10555 |
| dashboard | `/api/v1/stocks/300188/candles` | 4.904 | 200 | 8780 |
| dashboard | `/api/v1/capital-flow?source=sina` | 0.973 | 200 | 13136 |
| dashboard | `/api/v1/capital-flow/research?source=sina` | 1.182 | 200 | 74561 |
| dashboard | `/api/v1/capital-flow/research/member-industries` | 1.963 | 200 | 2230 |
| dashboard | `/api/v1/sector-workbench` | 60.065 | 502 | 42 |
| dashboard | `/api/v1/limit-up-ladder` | 17.958 | 200 | 148736 |
| dashboard | `/api/v1/watchlist` | 0.037 | 200 | 259066 |
| dashboard | `/api/v1/watchlist/monitor` | 0.961 | 200 | 144679 |
| dashboard | `/api/v1/watchlist/nextday-strategy` | 1.251 | 200 | 10365 |
| dashboard | `/api/v1/watchlist/strategy-profiles` | 0.080 | 200 | 181604 |
| dashboard | `/api/v1/dashboard/premarket` | 2.473 | 200 | 7753 |
| dashboard | `/api/v1/dashboard/intraday` | 0.501 | 200 | 4222 |
| dashboard | `/api/v1/dashboard/postmarket` | 0.427 | 200 | 4222 |
| dashboard | `/api/v1/market-structure/overview` | 8.788 | 200 | 5920100 |
| dashboard | `/api/v1/global-board` | 0.327 | 200 | 2305781 |
| dashboard | `/api/v1/tech-board` | 3.028 | 200 | 1761695 |
| dashboard | `/api/v1/tech-board/boards/cni-980115/members` | 1.756 | 200 | 131908 |
| dashboard | `/api/v1/tech-board/boards/cni-980115/history` | 3.923 | 200 | 26542 |
| dashboard | `/api/v1/tech-board/concepts/sina-chgn_701159/members` | 0.913 | 200 | 419694 |
| dashboard | `/api/v1/research` | 9.435 | 200 | 1401977 |
| dashboard | `/api/v1/reviews/availability` | 0.576 | 200 | 4286 |
| dashboard | `/api/v1/reviews/latest` | 1.756 | 200 | 1328 |
| dashboard | `/api/v1/us-industries/overnight` | 0.016 | 200 | 51126 |
| dashboard | `/api/v1/us-industries/calendar` | 0.011 | 200 | 3407 |
| dashboard | `/api/v1/us-industries/history` | 4.227 | 200 | 1536328 |

## Dashboard 容器内补测

| 服务 | GET 路径与参数 | 秒 | HTTP | 字节 |
| --- | --- | ---: | ---: | ---: |
| dashboard | `/api/v1/health` | 0.008 | 200 | 39 |
| dashboard | `/api/v1/sectors` | 0.191 | 200 | 2 |
| dashboard | `/api/v1/events` | 2.339 | 200 | 552755 |
| dashboard | `/api/v1/decisions` | 0.321 | 200 | 2 |
| dashboard | `/api/v1/audit` | 1.073 | 200 | 20220 |
| dashboard | `/api/v1/seat-tracking/subscriptions` | 1.420 | 200 | 1302 |
| dashboard | `/api/v1/seat-tracking/reports` | 0.133 | 200 | 711 |
| dashboard | `/api/v1/seat-tracking/reviews` | 0.163 | 200 | 1418 |
| dashboard | `/api/v1/research?limit=50` | 0.153 | 200 | 131728 |
| dashboard | `/api/v1/us-industries/history?limit=5` | 0.034 | 200 | 256337 |
| dashboard | `/api/v1/market-structure/overview?lookback=5` | 0.284 | 200 | 584848 |
| dashboard | `/api/v1/swing-selection` | 10.773 | 200 | 3992883 |
| dashboard | `/api/v1/swing-selection/stats` | 0.564 | 200 | 5798 |
| dashboard | `/api/v1/swing-selection?limit=50` | 8.808 | 200 | 597861 |
| dashboard | `/api/v1/health` | 0.006 | 200 | 39 |

## 上游服务直连

| 服务 | GET 路径与参数 | 秒 | HTTP | 字节 |
| --- | --- | ---: | ---: | ---: |
| stock | `/api/integrations/investment-dashboard/watchlist?refresh_quotes=false&limit=1` | 2.203 | 200 | 2748 |
| stock | `/api/integrations/investment-dashboard/swing-selection?contract_version=investment-dashboard-swing-selection-v3&limit=50` | 6.034 | 200 | 597548 |
| stock | `/api/integrations/investment-dashboard/swing-selection/stats?contract_version=investment-dashboard-swing-stats-v3` | 6.961 | 200 | 5798 |
| stock | `/api/integrations/investment-dashboard/short-selection` | 14.424 | 200 | 114461 |
| stock | `/api/integrations/investment-dashboard/monitor` | 0.202 | 200 | 144929 |
| stock | `/api/integrations/investment-dashboard/market-structure` | 8.118 | 200 | 5548325 |
| stock | `/api/integrations/investment-dashboard/global-board` | 3.339 | 200 | 2305635 |
| stock | `/api/integrations/investment-dashboard/tech-board` | 20.958 | 200 | 4677050 |
| news | `/api/health` | 0.003 | 200 | 145 |
| news | `/api/integrations/investment-dashboard/research?limit=100` | 14.603 | 200 | 180006 |
| news | `/api/x-watch/users?limit=20` | 8.684 | 200 | 2112 |
| news | `/api/x-watch/usage` | 4.681 | 200 | 4607 |

## 公网 HTTPS，声明 Accept-Encoding: gzip

| 服务 | GET 路径与参数 | 秒 | HTTP | 字节 |
| --- | --- | ---: | ---: | ---: |
| dashboard | `/api/v1/health` | 0.206 | 200 | 39 |
| dashboard | `/api/v1/swing-selection` | 6.952 | 200 | 255669 |
| dashboard | `/api/v1/swing-selection?trade_date=2026-10-20` | 3.126 | 200 | 247092 |
| dashboard | `/api/v1/swing-selection?limit=50` | 2.311 | 200 | 60851 |
| dashboard | `/api/v1/short-selection` | 3.790 | 200 | 3511 |
| dashboard | `/api/v1/stocks/300188/bars` | 4.867 | 200 | 2698 |

共70次；无管理写接口、采集/同步/AI或X收费调用。
