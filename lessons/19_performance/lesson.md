<!-- course-chapter: 19 -->

# 第 19 章：性能与诊断

性能优化的第一步不是改代码，而是把“慢”变成可重复的问题。本章使用标准库
`timeit`、`cProfile`、`pstats` 和 `tracemalloc`，分别回答小片段耗时、调用热点和 Python
内存分配峰值问题。

配套内容：

- 完整实现：`lessons/19_performance/example.py`
- 练习：`lessons/19_performance/exercise.py`
- 验收：`lessons/19_performance/test_lesson.py`
- 参考实现：`lessons/19_performance/example.py`

先运行：

```bash
uv run pytest lessons/19_performance/test_lesson.py -q
```

## 1. 先定义问题，再选择工具

“程序很慢”至少可能表示：

- 单个 CPU 密集函数耗时长；
- 算法复杂度随输入增长过快；
- 网络或磁盘 I/O 等待；
- 分配太多对象导致内存压力；
- 锁竞争、队列背压或并发度错误；
- 首次导入、缓存预热或数据库连接造成冷启动。

不同问题需要不同证据。先写清：真实工作负载是什么、输入规模多大、当前指标是多少、
目标是多少、允许牺牲多少内存或复杂度。没有这些信息，“更快”无法验收。

一个可靠流程是：

```text
复现 → 建立基线 → 定位热点 → 提出假设 → 只改一件事 → 同条件复测 → 记录取舍
```

如果改完没有可重复差异，就不应把复杂代码包装成“优化”。

## 2. 测量环境也属于实验条件

比较前尽量固定：Python 版本、依赖版本、输入数据、运行次数、机器负载和冷/热缓存状态。
一次 `perf_counter()` 差值很容易被调度、垃圾回收和后台进程干扰。

报告至少记录：

```text
场景：在 100_000 个整数中做最坏情况成员查询
Python：CPython 3.13.x
输入：目标不存在
重复：每轮 10_000 次，共 5 轮
结果：中位数与最小值
结论：只适用于重复查询；构造集合的成本另算
```

微基准最好在稳定电源、相同环境运行，并关注倍数和数量级，不要把纳秒级随机波动解释成
真实收益。

## 3. timeit 测量小而明确的代码

`timeit.Timer` 会重复调用目标并使用合适的高分辨率计时器：

```python
from timeit import Timer


def benchmark(function, *, number: int = 1000) -> float:
    if number <= 0:
        raise ValueError("number 必须大于零")
    return Timer(function).timeit(number=number)
```

返回值是执行 `number` 次的总秒数，不是单次平均值。需要平均值时自行除以 `number`，并在
报告中明确单位。

```python
elapsed = benchmark(lambda: 9_999 in values, number=10_000)
per_call = elapsed / 10_000
```

比较两个实现必须使用相同输入和次数。也要决定是否把准备成本包含在测量中：

```python
values = list(range(10_000))
value_set = set(values)  # 放在计时外：只比较重复查询。

list_time = benchmark(lambda: 9_999 in values)
set_time = benchmark(lambda: 9_999 in value_set)
```

若业务只查询一次，构造 set 的成本可能抵消收益。因此基准问题要对应真实使用方式。

## 4. 不要在自动测试里断言“必须更快”

下面的测试很脆弱：

```python
def test_set_is_faster():
    assert benchmark(set_lookup) < benchmark(list_lookup)
```

CI 机器负载、解释器版本和输入规模都可能改变结果。正确性测试应验证测量工具的契约：

- callable 是否恰好执行指定次数；
- 非正次数是否被拒绝；
- 返回值是否为非负时间；
- 参数和异常是否正确传递。

性能阈值属于专门的基准环境，需要统计方法、容忍度和历史基线，不应混进普通单元测试。

## 5. cProfile 找“时间花在哪里”

`timeit` 告诉你整体需要多久，`cProfile` 记录函数调用关系和耗时：

```python
import cProfile
import io
import pstats


def profile_text(function, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.runcall(function, *args, **kwargs)

    output = io.StringIO()
    stats = pstats.Stats(profiler, stream=output)
    stats.sort_stats("cumulative").print_stats()
    return output.getvalue()
```

常见列：

- `ncalls`：调用次数；
- `tottime`：函数自身耗时，不含子调用；
- `percall`：平均每次耗时；
- `cumtime`：函数及其子调用累计耗时；
- `filename:lineno(function)`：函数位置。

从 `cumulative` 排序适合先找一条慢调用链，从 `tottime` 排序适合找函数自身热点。高调用
次数也值得关注：单次很快的函数被调用百万次，同样可能占据大量时间。

Profiler 本身有开销，所以用它定位热点，再用贴近真实场景的基准确认优化效果。它不会
自动解释异步等待、外部服务或内核 I/O 的全部原因。

## 6. tracemalloc 测 Python 分配峰值

`tracemalloc` 跟踪 Python 内存分配。最小封装如下：

```python
tracemalloc.start()
try:
    result = function(*args, **kwargs)
    current, peak = tracemalloc.get_traced_memory()
finally:
    tracemalloc.stop()
```

`current` 是读取时仍在跟踪的内存，`peak` 是测量期间观察到的峰值。峰值通常比函数结束
后的当前值更能暴露临时大对象。

`stop()` 必须放在 `finally`：被测函数抛出异常时也要恢复全局跟踪状态。否则后续测试会
继承污染状态，得到难以解释的结果。

```python
result, memory = measure_peak_memory(
    lambda size: [value**2 for value in range(size)],
    100_000,
)
print(memory.peak_bytes)
```

`tracemalloc` 主要观察 Python 分配器管理的内存，不等于操作系统看到的全部进程 RSS；
第三方原生扩展的内存需要其他工具。

## 7. 算法复杂度常比微优化重要

对 list 做成员查询通常是 O(n)，对 set/dict 平均是 O(1)。当输入扩大十倍时，前者最坏
工作量也可能扩大约十倍；后者通常不会线性增长。

```python
values = list(range(100_000))
value_set = set(values)

missing_in_list = 100_001 in values
missing_in_set = 100_001 in value_set
```

但 set 需要额外内存和构建时间，也会失去重复元素和基于位置的语义。数据结构选择应由
访问模式决定：一次顺序遍历用 list 很自然，大量成员查询才可能值得建立 set。

优化前先检查是否存在重复扫描、嵌套循环、不必要排序或重复解析。把 O(n²) 降到 O(n)
通常远比替换一个局部语法更重要。

## 8. 生成器节省峰值内存，不保证更快

列表立即计算并保存全部元素：

```python
squares = [value * value for value in range(1_000_000)]
```

生成器按需产生：

```python
squares = (value * value for value in range(1_000_000))
```

生成器通常降低峰值内存，适合流式管道和只消费一次的数据；但每次 `next()` 都有恢复执行
成本，而且生成器会被消费，不能像列表一样重复遍历和随机访问。

因此正确说法不是“生成器更快”，而是“生成器改变了计算时机和空间占用”。应分别测量
总耗时、峰值内存，并确认调用方是否需要多次遍历。

## 9. 缓存用空间换重复计算

`functools.lru_cache` 对相同可哈希参数复用结果：

```python
from functools import lru_cache


@lru_cache(maxsize=256)
def parse_schema(text: str) -> Schema:
    return expensive_parse(text)
```

通过 `cache_info()` 观察 `hits`、`misses`、`maxsize` 和 `currsize`。如果参数几乎从不重复，
缓存只有查表和内存成本；如果结果依赖文件、时间或外部状态，缓存还可能返回过期数据。

需要明确：

- key 是否稳定且可哈希；
- 命中率是否足够；
- `maxsize` 是否限制增长；
- 何时调用 `cache_clear()`；
- 多线程或多进程下缓存是否符合预期；
- 被缓存结果是否可被调用方修改。

缓存不是装饰器一加就结束，它引入了生命周期和一致性问题。

## 10. CPU、I/O 与并发边界

性能诊断要结合第 14 章：

- CPU 密集工作在事件循环中执行会阻塞其他协程；
- 同步磁盘或 HTTP 等待不能因为函数写成 `async def` 就自动异步；
- `asyncio.to_thread()` 适合把阻塞 I/O 移出循环，但不保证纯 Python CPU 并行；
- 多进程能绕开单进程解释器限制，但增加序列化和进程成本；
- 增加并发可能压垮下游，而不是降低单请求延迟。

先用 profile 区分计算与等待，再选择算法、批处理、缓存、线程、进程或异步 I/O。不要用
并发掩盖一个本可消除的重复计算。

## 11. 从数据得出有限结论

一份有用的优化记录可以这样写：

```text
问题：10 万行输入的去重步骤占总时间 72%。
证据：cProfile 的 cumulative 排序显示 list membership 为主要热点。
假设：使用 set 维护已见 key，可将重复查询从 O(n) 降为平均 O(1)。
实验：相同数据、相同 Python、5 轮，每轮完整执行。
结果：中位耗时 1.82s → 0.14s；峰值内存 18MB → 27MB。
决定：批处理内存预算为 64MB，接受 9MB 增量。
限制：key 高度唯一；更大输入需继续验证。
```

结论要限定在实际实验条件内。不要把一个 100 元素微基准推广成所有负载，也不要只报告
最快的一次运行。

## 12. 本章练习顺序

在 `lessons/19_performance/exercise.py` 中依次完成：

1. `benchmark()`：验证 `number > 0`，用 `Timer(function).timeit(number=number)`。
2. `profile_text()`：转发位置和关键字参数，按累计时间输出报告。
3. `measure_peak_memory()`：保留函数返回值，报告 current/peak，并在异常时停止跟踪。

运行单章验收：

```bash
uv run pytest lessons/19_performance/test_lesson.py -q
```

运行演示：

```bash
uv run python lessons/19_performance/example.py
```

验收测试刻意不比较两个实现谁更快，而是验证工具契约、参数转发、报告结构和清理行为。

## 13. 常见误区

- 看到复杂代码就先优化，没有业务基线；
- 只运行一次并报告最快结果；
- 比较时输入、次数或准备成本不同；
- 在普通 CI 单元测试中断言精确耗时；
- 只看 `tottime`，忽略慢调用链的 `cumtime`；
- 测内存时异常路径没有 `tracemalloc.stop()`；
- 认为生成器一定更快、缓存一定有益；
- 为无法感知的微小收益牺牲可读性和正确性。

## 14. 完成标准与复习题

完成本章时，你应能：

- 为真实工作负载建立可重复的时间和内存基线；
- 说明 `timeit`、`cProfile` 和 `tracemalloc` 各回答什么问题；
- 读懂 `ncalls`、`tottime` 与 `cumtime`；
- 在 list/set、list/generator、计算/缓存之间说明时间与空间取舍；
- 写出不会依赖机器速度的测量工具单元测试；
- 用数据记录优化前后结果及适用范围。

请回答：

1. `Timer.timeit(number=1000)` 返回的是单次时间还是总时间？
2. 为什么构造 set 的成本是否放进计时会改变结论？
3. `current_bytes` 和 `peak_bytes` 分别表示什么？
4. 一个函数 `cumtime` 很高但 `tottime` 很低，通常意味着什么？
5. 哪些情况下 `lru_cache` 可能让系统更慢或占用更多内存？
