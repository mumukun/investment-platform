# CHG-20261016-008 本地布局验收

Dashboard基线eed62d429c01ca32dacb5318c1f2ef3bc1d281cb，独立feat/CHG-20261016-008-tech-board-layout分支。本轮未提交/推送/合并/发布；没有新Tag或Release。CHG-20261016-006的右侧抽屉仍在另一个工作树，未覆盖该成果。

- 命令：npm test -- --run src/components/TechConceptExplorer.spec.ts src/utils/techBoard.spec.ts。2文件5测试通过，见vitest.txt。没有为可逆样式新增结构镜像测试；既有选择、搜索、详情入口、无虚构来源及请求竞争测试保留。
- npm run build（vue-tsc + Vite）成功，见build.txt；git diff --check通过。仅改展示/文档，未运行后端或Provider测试。
- 本地浏览器挂载实际TechBoardView、TechConceptExplorer、PageHeader与图表；外壳只复用已有app-*样式作演示。MOCK标记明显，成员从仓库公开参考名单截取，数量/价格/走势为布局fixture，不代表生产或完整真实名单；fetch禁止任何真实服务请求。
- 1280px：桌面documentWidth=1280；chrome导航、surface概览/名单、surface-soft指标/表头、chrome交替行均在DOM核实。主图见desktop-top、desktop-detail；空搜索empty-search，待核验pending-direction，名单失败member-error，指数展开index-reference，个人关注personal-watch。
- 搜索生益仅1行；无匹配提示可见；硅光待核验不出现表格；名单失败保留概览和名单区域、独立琥珀提示及重试按钮；分页25→5，关注true后恢复false。没有真实关注或研究写入。
- 键盘Tab从CPO项进入光芯片项，outline为#6c5ed0 solid 2px；选择背景#ebe7ff。没有修改股票详情调用或排序计算。
- 320px：documentWidth=320，目录为两列并内部滚动；成员面板client298/表格scroll720，横向滚动限定在表格内。概览与成员区见mobile-320、mobile-detail-320；指数展开和个人关注仍doc320，见personal-watch-mobile。
- 最终控制台无warn/error。辅助字12px，表格13px；文字抽样对比：#62675e/#fffdf9 5.71:1、#62675e/#f3f0e9 5.10:1、#6554c0/#ebe7ff 4.86:1、#95601c/#fbf2e5 4.77:1、#366caf/#edf3fb 4.80:1、交替行涨跌5.05/4.97:1。不声称整站无障碍通过。

验收后关闭本地预览、标签页、视口覆盖并移除临时fixture/依赖软链，保留未提交工作树。下一步如需上线，应与006分别审查和提交，再按正式发布治理集成；007仍为用户指定的后续资金待办，不属于本次实现。
