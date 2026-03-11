# 论文阅读自动处理器

一款自动将研究论文上传至 [千问阅读](https://www.qianwen.com/read) 并通过 GPT-4o-mini 对其是否为多 domain 的 rubric benchmark 进行自动判断的工具。

## 功能

- **自动上传**: 自动将 `./paper` 中的 PDF 论文上传到千问阅读。
- **自动摘要提取**: 自动在网页界面抓取其“AI 导读”的摘要。
- **AI 自动判断**: 使用 GPT-4o-mini 对摘要进行分析判断。
- **结果导出**: 将所有判断和理由保存到 `answer.xlsx`。
- **过程截图**: 在 `auto_read/chat_screenshots` 目录下保存每个文件的网页截图，以便人工核对。

## 安装

1. 安装 [uv](https://github.com/astral-sh/uv)。
2. 安装依赖:
   ```bash
   cd auto_read
   uv sync
   uv run playwright install chromium
   ```

## 配置

1. **Cookies**: 在网页端登录千问阅读，使用“Cookie-Editor”插件导出 JSON 格式的 cookies，保存为 `auto_read/cookies.json`。
2. **Tokens**: 在项目根目录下创建 `tokens.yaml` 文件，填入你的 OpenAI API Key 和 base_url。

## 使用方法

将需要处理的 PDF 文件放入 `./paper` 目录，然后运行:
```bash
cd auto_read
uv run auto_read.py
```

## 项目结构

```text
.
├── paper/               # 存放 PDF 论文
├── auto_read/
│   ├── auto_read.py     # 主运行程序
│   ├── cookies.json     # 用户 cookies (由 .gitignore 忽略)
│   └── chat_screenshots/# 存放生成的核对截图
├── tokens.yaml          # API tokens (由 .gitignore 忽略)
└── answer.xlsx          # 最终导出的表格 (由 .gitignore 忽略)
```

## 协议

遵循 MIT 开源协议。
