# CHG-20261016-006 本地验证

基线 Dashboard `eed62d429c01ca32dacb5318c1f2ef3bc1d281cb`，治理 `f06b628d934d5ccf8c52567e352f58cebaae921e`。本轮均为独立工作树未提交成果，不代表生产已上线。

- `npm test -- --run`：36文件 / 169测试通过，无未处理错误，见vitest.txt。
- `npm run build`：vue-tsc和Vite成功，见build.txt；应用版本仍0.24.0，未创建新Release。
- 本地1280px浏览器：实际Swing/Short/Watchlist/LimitUpLadder/TechConceptExplorer与唯一应用级StockDetailDrawer挂载；使用现有测试样例，页面明确MOCK，fetch禁止真实服务访问。截图分别为swing-right、short-right、watchlist-right、limit-up-right、tech-right。共享行情页签见shared-chart。
- 波段非自选候选显示原参与决策、优先级分解、原条件与全部路径；短线保留量化与风险；涨停保留封板事实。每次只出现一个rtl个股抽屉，桌面右边缘1280、宽860。
- 科技成员键盘方向键切换到行情页；Escape关闭，等待抽屉隐藏后焦点返回原股票名称。
- 320px：科技/自选共用面板及波段模块证据均宽320，无抽屉横向溢出；修复波段页头日期/按钮不换行引起背景363px溢出后，文档宽320。见mobile-320 / swing-mobile-320。
- 最终浏览器控制台warn/error为空。辅助文字实测12px，#62675e与#fffdf9对比5.71:1、与#f3f0e9对比5.1:1；仅针对本轮内容抽样，不声称整站无障碍认证。
- AI决策/次日源、日期与证券身份过滤、迟到响应、补充上下文异常、研究保存及候选发现由Vitest覆盖。公司页签沿用原按需服务，未执行真实AI生成；未连接生产、写入真实研究或执行后端/数据库/Provider测试（未改其代码）。

临时本地预览、标签页、视口设置及依赖软链在验收后清理；保留修改工作树供后续审查。资金排序/成分股仅记录CHG-20261016-007 PLANNED。
