# Code Eval

Code Eval是一个用于行内代码补全的Python工具。它可以从C++等代码库中提取测试集并验证测试结果。

## 安装

首先，确保你已经安装了Poetry。然后，克隆此仓库并在项目根目录下运行：

```bash
poetry install
```

这将会安装所有必要的依赖。

## 使用

### 准备数据集

运行以下命令来准备数据集：

```bash
poetry run python code_eval/main.py prepare --src <源代码目录> --output <输出文件路径>
```

### 评估测试

运行以下命令来评估测试：

```bash
poetry run python code_eval/main.py evaluate --dataset <数据集文件路径>
```

## 开发

此项目使用Poetry进行依赖管理。如果你需要添加或更新依赖，请使用：

```bash
poetry add <依赖名>
```

## 贡献

欢迎通过Pull Requests或Issues来贡献你的代码或提出建议。