
# TruLens-eval with Google Gemini Examples

This repository provides practical examples of using `trulens-eval` to evaluate the quality and relevance of AI-generated content, with a specific focus on using Google's Gemini models as the evaluation provider.

## 🌟 Overview

These examples demonstrate how to integrate `trulens-eval` into your AI applications to gain deeper insights into their performance. You will learn how to:

-   **Trace & Evaluate a LangGraph Agent**: Automatically record a multi-step agent's execution and evaluate the relevance of its retrieved context.
-   **Use Custom Feedback Functions**: Assess the quality of a generated plan against specific criteria using a standalone feedback function.

## 🚀 Examples Included

1.  **`context_relevance.py`**:
    -   Builds a simple agent using `LangGraph` that searches for information with the `Tavily` tool.
    -   Uses `TruGraph` to trace the application's execution.
    -   Evaluates the relevance of the search results (context) to the user's query using the `Context Relevance` feedback function from `trulens-eval`.
    -   Launches the TruLens dashboard to visualize the trace and evaluation results.

2.  **`plan_quality.py`**:
    -   Directly evaluates two predefined text plans (one mediocre, one excellent) without running a full AI application.
    -   Demonstrates the usage of the `plan_quality_with_cot_reasons` feedback function to get a nuanced quality score and detailed reasoning from Gemini.

## 🛠️ Setup and Installation

Follow these steps to get the examples running on your local machine.

**1. Clone the Repository**

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

**2. Create a Virtual Environment (Recommended)**

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

**3. Install Dependencies**

All required packages are listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables**

You need to provide API keys for Google and Tavily.

-   Copy the example file `.env.example` to a new file named `.env`.
    ```bash
    cp .env.example .env
    ```
-   Open the `.env` file and add your personal API keys.
    -   `GOOGLE_API_KEY`: Required for `trulens-eval`'s feedback provider. Get it from [Google AI Studio](https://aistudio.google.com/app/apikey).
    -   `TAVILY_API_KEY`: Required for the search tool in `context_relevance.py`. Get it from [Tavily AI](https://app.tavily.com/).

## ▶️ How to Run

**Example 1: Evaluate Context Relevance in an Agent**

This script will run the LangGraph agent, record the trace, perform the evaluation, print the results to the console, and start the TruLens dashboard.

```bash
python context_relevance.py
```

-   **Expected Output**: The console will show the agent's output and a summary of the feedback results.
-   **Dashboard**: A local dashboard will be available at `http://localhost:8501` for detailed inspection of traces and evaluations.

**Example 2: Evaluate Plan Quality**

This script will directly evaluate the two hardcoded plans and print their scores and the reasoning behind them.

```bash
python plan_quality.py
```

-   **Expected Output**: You will see a detailed breakdown in the console for both the "mediocre" and "excellent" plans, including a quality score (0-100) and the evaluation logic from Gemini.

---
---

# TruLens-eval 结合 Google Gemini 示例

[English](./README.md) | 简体中文

本代码库提供了一系列实用示例，演示如何使用 `trulens-eval` 评估 AI 生成内容的质量与相关性，并重点展示了如何集成 Google Gemini 模型作为评估服务提供方（Provider）。

## 🌟 概览

这些示例将帮助您理解如何将 `trulens-eval` 集成到您的 AI 应用中，从而深入洞察其性能。您将学习到：

-   **追踪与评估 LangGraph Agent**: 自动记录一个多步 Agent 的完整执行过程，并评估其检索到的上下文（Context）的相关性。
-   **使用自定义 Feedback 功能**: 使用独立的 Feedback 函数，根据特定标准评估一个“计划”文本的质量。

## 🚀 示例说明

1.  **`context_relevance.py`**:
    -   使用 `LangGraph` 构建一个简单的 Agent，该 Agent 通过 `Tavily` 工具进行信息检索。
    -   使用 `TruGraph` 包装器来追踪应用的执行流程。
    -   利用 `trulens-eval` 的 `Context Relevance`（上下文相关性）Feedback 函数，评估搜索结果（上下文）与用户查询的匹配程度。
    -   运行结束后，启动 TruLens Dashboard 以便对追踪和评估结果进行可视化分析。

2.  **`plan_quality.py`**:
    -   不运行完整的 AI 应用，而是直接评估两个预定义的计划文本（一个中等质量，一个高质量）。
    -   演示如何使用 `plan_quality_with_cot_reasons` Feedback 函数，从 Gemini 获得精确的质量分数和详细的评估理由。

## 🛠️ 环境设置与安装

请遵循以下步骤在您的本地环境中运行这些示例。

**1. 克隆代码库**

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

**2. 创建虚拟环境 (推荐)**

```bash
python -m venv venv
source venv/bin/activate  # Windows 系统请使用 `venv\Scripts\activate`
```

**3. 安装依赖**

所有必需的 Python 包都已在 `requirements.txt` 文件中列出。

```bash
pip install -r requirements.txt
```

**4. 配置环境变量**

您需要提供 Google 和 Tavily 的 API 密钥。

-   首先，将环境变量示例文件 `.env.example` 复制为新文件 `.env`。
    ```bash
    cp .env.example .env
    ```
-   然后，编辑 `.env` 文件，填入您的个人 API 密钥。
    -   `GOOGLE_API_KEY`: `trulens-eval` 的 Feedback Provider 需要此密钥。您可以从 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取。
    -   `TAVILY_API_KEY`: `context_relevance.py` 示例中的搜索工具需要此密钥。您可以从 [Tavily AI](https://app.tavily.com/) 获取。

## ▶️ 如何运行

**示例 1: 评估 Agent 的上下文相关性**

此脚本将运行 LangGraph Agent，记录其追踪数据，执行评估，将结果打印到控制台，并启动 TruLens Dashboard。

```bash
python context_relevance.py
```

-   **预期输出**: 控制台将显示 Agent 的最终输出以及 Feedback 评估结果的摘要。
-   **Dashboard**: 脚本会自动启动一个本地网站，通常在 `http://localhost:8501`，您可以在其中查看详细的调用链和评估数据。

**示例 2: 评估计划质量**

此脚本将直接评估代码中预设的两个计划，并打印出它们各自的得分与评估理由。

```bash
python plan_quality.py
```

-   **预期输出**: 您将在控制台中看到对“有待改进的计划”和“优秀的计划”的详细分析，包括一个 0-100 分制的质量评分以及来自 Gemini 的评估逻辑。