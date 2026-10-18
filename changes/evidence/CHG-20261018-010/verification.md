# CHG-20261018-010 验证记录

仅本地实现与Commit；未Push/PR/Merge/Tag/部署。marketNewsFeed不涉及。测试使用本Change自建127.0.0.1隔离PostgreSQL17数据库，未访问生产或其他项目数据。

## 来源与边界

- 官方板块页面：https://data.eastmoney.com/bkzj/BK1495.html
- 官方脚本：https://data.eastmoney.com/newstatic/js/bkzj/detail.js
- 脚本文件SHA256：75e1f192820a4902f317d8e7ffb3b07733793d658831ba8674f951c8ee1307b1
- 公开脚本确认：fs=b:BK代码；3/5/10日主力净额f267/f164/f174；涨幅f127/f109/f160；f6当日成交额；f124个股源时间。金额原单位元，输出亿元。不是逐日重算账本，不代表指数贡献。
- 本机对push2delay.eastmoney.com及push2.eastmoney.com行情只读探针被远端关闭连接（RemoteDisconnected/ConnectionError）。没有成功行情捕获，未将合成值标为真实抓取证据；目标环境真实连通/数值核对尚未执行。
- Provider源夹具明确Synthetic；Consumer夹具由Provider.collect处理该合成夹具导出。isMock=false仅用于校验真实数据契约标识，夹具message明确合成。浏览器入口覆写为MOCK且显示固定MOCK提示，非生产页面。

## Repository / Contract Tests

- Provider Python3.13：`python -m pytest tests/test_sector_fund_members.py tests/test_sector_fund_research.py tests/test_sector_fund_store.py tests/test_capital_flow.py -q`：39 PASS，含自建隔离PG队列/幂等/失败保留/历史读取；ASGI Bearer鉴权、GET只读、POST后台；101只完整分页、数量变化、重复/缺字段/日期/有限数字。
- Provider `python scripts/check_config.py`与受影响模块compileall：PASS。新增成员测试进入既有CI pytest命令；CI未触发，显式PG用例在无本地测试URL时skip。
- Consumer：`pytest backend/tests/test_sector_fund_members.py backend/tests/test_sector_fund_research.py -q`：39 PASS；含原始字段、鉴权/超时/契约失败、PG健康快照保留/覆盖倒退/历史截止隔离、会话保护/刷新独立失败。没有迁移，无需migration检查。
- Consumer `ruff check backend`、`uv lock --check --offline`：PASS。
- `npm test`：38文件188 PASS。覆盖窗口切换、真实零/缺失、搜索/排序/分页、股票详情观察日、失败保留/重试、后台轮询、关闭清理、晚到响应隔离。`npm run build`（Vue TS/Vite）：PASS。

## 浏览器验收

实际App、SectorFundResearchPanel、图表及新增成员组件；所有接口由临时本地验收入口返回明确MOCK合成数据，25只观察名单，非真实个股行情。不新增截图自动化测试套件。

- 默认1280×720：流入/流出双列，暖灰表面、紫色焦点、红绿金融数值。搜索002535能在完整25只中定位第25只，不局限当前页。desktop-mock.png。
- 390×844：document.scrollWidth=390，抽屉宽374.40/scrollWidth374，排行单列334.40，表格内部334宽/695滚动宽；正文无横向溢出。mobile-390-mock.png。
- 320×740：document.scrollWidth=320，抽屉宽307.20/scrollWidth307，排行单列267.20，表格内部267宽/695滚动宽。mobile-320-mock.png。
- 观测了窗口过渡结束后的尺寸；没有把CSS过渡中间值误判为溢出。浏览器已恢复视口并关闭本任务临时页。

## 保留项

本地隔离工作树保留；008/009及原checkout用户文件未纳入本次提交。真实行情可用性、生产浏览器及正式发布未验证/未执行。后续准备发布应先按Change依赖核对Provider→Dashboard，不能凭MOCK验收宣称真实行情已就绪。

最终Consumer测试有1条Starlette/httpx测试工具弃用提示，无业务检查失败。测试容器重启曾改变随机端口，旧端口连接失败后按实际端口重新执行，两侧39项均通过。临时Vite和本Change测试容器已停止；原文件与停止容器保留。
