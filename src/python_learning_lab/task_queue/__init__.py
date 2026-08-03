"""第 20 章综合项目的边界模型和组装入口。

完整任务要求位于 ``exercises/capstone/README.md``。这里仅提供稳定的公开输入输出
模型，领域规则复用 ``python_learning_lab.engineering`` 中的实现。
"""

from .models import CreateTaskInput, TaskOutput

__all__ = ["CreateTaskInput", "TaskOutput"]
