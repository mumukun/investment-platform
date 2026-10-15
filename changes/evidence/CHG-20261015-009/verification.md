# CHG-20261015-009 验证

- Dashboard 基线：492c580；实现已本地提交：7fe2154a2177fad81a253db3699fe5b5464ed02f。
- `npm test -- src/views/WatchlistView.spec.ts src/App.spec.ts`：2 文件、18 项通过。
- `npm run build`：vue-tsc、Vite production build 通过。
- `git diff --check`：通过。
- 浏览器：真实 App.vue / WatchlistView.vue，临时纯本地 fixture 模拟 48 只股票，不连接真实 API 或数据库。默认每页 20 只。
- 1280 × 720：标准行实测 66.5px，document 横向不溢出；截图 desktop.jpg。
- 390 × 844：响应式三行结构，实测 150px，无 document 横向溢出；截图 mobile.jpg。
- 临时预览入口与服务均已清理；node_modules 与构建产物为本隔离工作树的忽略文件。
- 未执行生产验证、后端测试或跨仓测试：本次不修改后端/契约/算法；无部署授权。
