import ast,json,re
from pathlib import Path
base=Path('/Users/mukun/.codex/worktrees/market-structure-etf')
root=base/'investment-platform'; docs=root/'docs'
repos={'stock-analyzer':base/'stock-analyzer','marketNewsFeed':Path('/Users/mukun/work/workspace/stock/marketNewsFeed'),'investment-research-dashboard':base/'investment-research-dashboard'}
existing=(docs/'data-model-fields-2026-10-13.md').read_text()
parts=re.split(r'^## (.+)$',existing,flags=re.M)
tables={};owner={}
for i in range(1,len(parts),2):
 names=re.findall(r'^### (\w+)$',parts[i+1],re.M)
 tables[parts[i]]=names
 for name in names:owner[name]=parts[i]
assert len(owner)==58
orm={}
models=repos['investment-research-dashboard']/'backend/app/models.py'
for cls in ast.parse(models.read_text()).body:
 if isinstance(cls,ast.ClassDef):
  for n in cls.body:
   if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='__tablename__' for t in n.targets):orm[cls.name]=ast.literal_eval(n.value)
usage={t:[] for t in owner};apis=[];parse_errors=[]

def fn_nodes(node):
 for child in ast.iter_child_nodes(node):
  if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef,ast.Lambda)):continue
  yield child
  yield from fn_nodes(child)

def symbol(node):
 if isinstance(node,ast.Name):return node.id
 if isinstance(node,ast.Attribute):return symbol(node.value)+'.'+node.attr
 return ''

for repo,rpath in repos.items():
 folders=['stock_analyzer','scripts'] if repo=='stock-analyzer' else ['src'] if repo=='marketNewsFeed' else ['backend/app','scripts']
 for folder in folders:
  for path in sorted((rpath/folder).rglob('*.py')):
   try:tree=ast.parse(path.read_text())
   except (SyntaxError,UnicodeError) as e:parse_errors.append(str(path));continue
   for fn in ast.walk(tree):
    if not isinstance(fn,(ast.FunctionDef,ast.AsyncFunctionDef)):continue
    if fn.name.startswith(('test_','self_test')):continue
    found={}
    for n in fn_nodes(fn):
     if isinstance(n,ast.Constant) and isinstance(n.value,str):
      value=n.value
      for op,pattern in [('SQL写 INSERT',r'\bINSERT\s+INTO\s+(\w+)'),('SQL改 UPDATE',r'\bUPDATE\s+(\w+)\s+SET'),('SQL删 DELETE',r'\bDELETE\s+FROM\s+(\w+)'),('SQL读 FROM/JOIN',r'\b(?:FROM|JOIN)\s+(\w+)')]:
       for table in re.findall(pattern,value,re.I):
        if table in usage:found.setdefault(table,set()).add(op)
      if value in usage:found.setdefault(value,set()).add('动态表名参数/常量引用')
     if repo=='investment-research-dashboard' and isinstance(n,ast.Name) and n.id in orm:
      found.setdefault(orm[n.id],set()).add('ORM模型引用')
     if repo=='investment-research-dashboard' and isinstance(n,ast.Call):
      if isinstance(n.func,ast.Name) and n.func.id in orm:found.setdefault(orm[n.func.id],set()).add('ORM构造对象（写入候选）')
      if isinstance(n.func,ast.Name) and n.func.id in ('select','insert','update','delete'):
       for arg in n.args:
        if isinstance(arg,ast.Name) and arg.id in orm:found.setdefault(orm[arg.id],set()).add('ORM '+n.func.id)
    for table,ops in found.items():
     if owner[table]!=repo:continue
     usage[table].append({'file':str(path),'function':fn.name,'line':fn.lineno,'operations':sorted(ops)})
    for dec in fn.decorator_list:
     if not isinstance(dec,ast.Call) or not isinstance(dec.func,ast.Attribute) or dec.func.attr not in ('get','post','put','patch','delete'):continue
     if not dec.args or not isinstance(dec.args[0],ast.Constant):continue
     route=dec.args[0].value
     if not isinstance(route,str):continue
     if repo=='investment-research-dashboard':
      prefix='/api/v1'+('/auth' if path.name=='auth_api.py' else '/seat-tracking' if path.name=='seat_tracking_api.py' else '/market-structure' if path.name=='market_structure.py' else '')
      route=prefix+route
     calls=sorted({symbol(n.func) for n in fn_nodes(fn) if isinstance(n,ast.Call) and symbol(n.func)})
     relevant=[c for c in calls if any(x in c.lower() for x in ('fetch','sync','build','compose','load','projection','generate','record','archive','save','store','client.'))]
     apis.append({'repo':repo,'method':dec.func.attr.upper(),'path':route,'file':str(path),'function':fn.name,'line':fn.lineno,'parameters':ast.unparse(fn.args),'return_annotation':ast.unparse(fn.returns) if fn.returns else '未声明','data_call_symbols':relevant,'direct_table_references':sorted(found)})
# Dynamic storage helper calls cannot be resolved by SQL literal matching; kept as explicit evidence category.
rows=['# 数据表—函数读写索引（细化版）','','核对日期2026-10-13。覆盖全部58张当前模型表。以下为静态源码证据，不执行采集、SQL或业务代码。','',
'判读规则：SQL INSERT/UPDATE/DELETE/FROM/JOIN是函数中出现的文字证据；ORM select/insert及模型引用只描述源码用法，不把任意引用冒充写操作。动态表名参数保留为待沿helper确认的引用。DELETE语句也含FROM，所以可能同时列为SQL读；这不是第二次真实查询。初始化DDL、测试及self_test不是业务数据血缘。函数中嵌套函数的证据另列，不声称运行调用次数或完整调用闭包。','',
'本文结合[细粒度业务数据手册](/Users/mukun/.codex/worktrees/market-structure-etf/investment-platform/docs/data-architecture-detail-2026-10-13.md)阅读；字段定义见[完整字段附录](/Users/mukun/.codex/worktrees/market-structure-etf/investment-platform/docs/data-model-fields-2026-10-13.md)。','']
for repo,names in tables.items():
 rows+=['## '+repo,'']
 for table in names:
  rows+=['### '+table,'','| 操作证据 | 函数 | 源文件 |','| --- | --- | --- |']
  refs=sorted(usage[table],key=lambda x:(x['file'],x['line']))
  for r in refs:
   relative=str(Path(r['file']).relative_to(repos[repo]))
   rows.append('| '+ ' / '.join(r['operations'])+' | `'+r['function']+'` | ['+relative+':'+str(r['line'])+']('+r['file']+':'+str(r['line'])+') |')
  if not refs:rows.append('| 未找到直接文字引用；不得推断已启用 | — | 模型定义存在，动态路径需进一步核对 |')
  rows+=['']
(docs/'data-table-function-index-2026-10-13.md').write_text('\n'.join(rows))
rows=['# 数据API—函数—调用符号索引（细化版）','','核对日期2026-10-13。FastAPI装饰器路由从源码提取，包含业务、认证及运维端点；不等于每条端点都已生产启用或每个动态分支都有独立契约。','',
'marketNewsFeed使用HTTP Handler分派而非FastAPI装饰器，research GET及通知链路见业务手册，不用0条装饰器路由表示无API。参数来自Python签名：Depends注入不是浏览器参数；认证、请求schema及响应嵌套字段须继续阅读对应模型。运行在/API版本前缀下的router已组合实际挂载前缀。','',
'“调用符号”是直接源码调用，不是已证明的全链路；通过构建器/客户端/依赖注入间接使用的表不会自动列为直接表引用。','']
for repo in repos:
 subset=[a for a in apis if a['repo']==repo]
 if not subset:continue
 rows+=['## '+repo+'（'+str(len(subset))+'个装饰器端点）','']
 for a in subset:
  rows+=['### '+a['method']+' '+a['path'],'',f"处理函数：[{a['function']}]({a['file']}:{a['line']})。返回注解：`{a['return_annotation']}`。",'', '```python',a['function']+'('+a['parameters']+')','```','', '数据相关直接调用：'+('、'.join('`'+c+'`' for c in a['data_call_symbols']) or '未发现命中符号；沿源函数查看。'),'','直接表/ORM引用：'+('、'.join('`'+t+'`' for t in a['direct_table_references']) or '未发现直接引用；可能通过依赖/构建器访问。'),'']
(docs/'data-api-function-index-2026-10-13.md').write_text('\n'.join(rows))
manifest={'schema_version':1,'scope':'read-only source AST; not runtime trace or production schema','tables':usage,'api_routes':apis,'parse_errors':parse_errors}
(root/'changes/evidence/CHG-20261013-002/data-lineage-source-index.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
assert not parse_errors,parse_errors
print(json.dumps({'tables':len(usage),'tables_with_refs':sum(bool(v) for v in usage.values()),'table_function_refs':sum(map(len,usage.values())),'api_routes':len(apis),'by_repo':{repo:sum(a['repo']==repo for a in apis) for repo in repos},'missing_refs':[t for t,v in usage.items() if not v]},ensure_ascii=False))
