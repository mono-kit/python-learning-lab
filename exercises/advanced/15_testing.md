# 第 15 章练习：建立测试矩阵

不要修改业务实现。为 `advanced/concurrency.py` 和 `engineering/service.py` 新增测试：

1. 用参数化覆盖成功、普通异常和超时。
2. 用计数器验证并发上限，不用真实网络。
3. 取消外层执行器，验证 worker 的 `finally` 已执行。
4. 用 fixture 分别提供内存仓库与 SQLite 仓库，让同一组服务契约测试运行两次。
5. 用 `caplog` 验证事件名和 `task_id`，不要断言完整时间戳。
6. 用 `FrozenClock` 测时间相关逻辑，不 patch 整个 `datetime` 模块。

写完后解释每个 fixture 管理的是数据、资源还是行为；如果一个 fixture 三者都做，
尝试拆分。
