import json
import time
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
import os
import warnings
import numpy as np
import pandas as pd

# --- 1. 环境设置 ---
print("🚀 步骤 1: 开始设置运行环境...")
load_dotenv()
os.environ["TRULENS_OTEL_TRACING"] = "1"
warnings.filterwarnings("ignore")
print("✅ 环境设置完成。")

# --- 必要的库导入 ---
from langchain.schema import BaseMessage, HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END

# --- TruLens 库导入 ---
from trulens.apps.langgraph import TruGraph
from trulens.core.session import TruSession
from trulens.core.otel.instrument import instrument
from trulens.otel.semconv.trace import SpanAttributes
from trulens.core import Feedback
from trulens.providers.google import Google
from trulens.core.feedback.selector import Selector
from trulens.dashboard import run_dashboard

# --- 2. 定义 Agent 状态和工具 ---
print("\n🚀 步骤 2: 定义 Agent 状态和初始化工具...")
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]

tavily_tool = TavilySearchResults(max_results=2)
print("✅ Agent 状态和 Tavily 搜索工具已准备就绪。")


# --- 3. 定义 LangGraph 节点 (已加入 @instrument 装饰器) ---
print("\n🚀 步骤 3: 定义 LangGraph 的搜索节点...")
@instrument(
    span_type=SpanAttributes.SpanType.RETRIEVAL,
    attributes=lambda ret, exception, *args, **kwargs: {
        SpanAttributes.RETRIEVAL.QUERY_TEXT: args[0]['messages'][-1].content,
        SpanAttributes.RETRIEVAL.RETRIEVED_CONTEXTS: [str(ret["messages"][-1].content)]
    },
)
def search_node(state: AgentState):
    print("\n   - [节点执行中]: 正在执行 'search_node'...")
    try:
        query = state['messages'][-1].content
        print(f"   - [节点内部]: 接收到查询 -> '{query}'")
        search_result = tavily_tool.invoke(query)
        new_message = HumanMessage(content=str(search_result), name="tavily_searcher")
        print("   - [节点内部]: Tavily 工具已成功返回搜索结果。")
        return {"messages": [new_message]}
    except Exception as e:
        print(f"   - [节点错误]: 'search_node' 执行失败: {e}")
        return {"messages": [HumanMessage(content=f"Tool failed with error: {e}", name="error")]}
print("✅ 搜索节点定义完成。")


# --- 4. 构建 LangGraph 工作流 ---
print("\n🚀 步骤 4: 构建并编译 LangGraph 工作流...")
workflow = StateGraph(AgentState)
workflow.add_node("searcher", search_node)
workflow.set_entry_point("searcher")
workflow.add_edge("searcher", END)
graph = workflow.compile()
print("✅ LangGraph 应用已成功创建。")


# --- 5. 定义 Feedback 功能 ---
print("\n🚀 步骤 5: 定义 TruLens Feedback 功能...")
gemini_provider = Google()
f_context_relevance = (
    Feedback(
        gemini_provider.context_relevance_with_cot_reasons,
        name="Context Relevance"
    )
    # First .on() call maps the 'question' argument.
    .on(
        {"question": Selector(
            span_type=SpanAttributes.SpanType.RETRIEVAL,
            span_attribute=SpanAttributes.RETRIEVAL.QUERY_TEXT,
        )}
    )
    # Second, chained .on() call maps the 'context' argument.
    .on(
        {"context": Selector(
            span_type=SpanAttributes.SpanType.RETRIEVAL,
            span_attribute=SpanAttributes.RETRIEVAL.RETRIEVED_CONTEXTS,
        )}
    )
    .aggregate(np.mean)
)

# --- 6. 设置 TruLens ---
print("\n🚀 步骤 6: 设置 TruLens Session 和 Recorder...")
session = TruSession()
print("   - 正在重置数据库...")
session.reset_database()
print("   - 数据库已清空，准备记录新的 Trace。")

tru_recorder = TruGraph(
    graph,
    app_name="LangGraph应用-带Feedback",
    session=session,
    feedbacks=[f_context_relevance]
)
print("✅ TruGraph Recorder 已成功创建。")


# --- 7. 运行和记录 ---
query = "英伟达(NVIDIA)股票的最新消息是什么？"
print(f"\n🚀 步骤 7: 执行应用并使用 TruLens 进行记录...")
print(f"   - 用户问题: '{query}'")

record_id = None
with tru_recorder as recording:
    result = graph.invoke({"messages": [HumanMessage(content=query)]})
    if recording.records:
        record_id = recording.records[0].record_id
        print(f"   - 成功捕获到 Record ID: {record_id}")

print("   - 应用执行完毕，等待数据写入数据库...")
time.sleep(6) 
print("✅ 数据记录完成。")


# --- 8. 【最终修复版】使用 OTel 模式检查和展示记录 ---
print("\n🚀 步骤 8: [OTel模式] 从数据库获取 Events 并展示结果...")

if record_id is None:
    print("\n   - [警告]: 未能捕获到 Record ID。无法查询具体的运行结果。")
else:
    app_name = tru_recorder.app_name
    app_version = tru_recorder.app_version
    print(f"   - 正在为 App '{app_name}' (版本: {app_version}) 查询 Events...")

    # 延长等待时间，确保反馈异步完成（可调整为循环）
    print("   - 等待反馈计算完成（异步）...")
    time.sleep(30)  # 或更长，如果 API 慢

    all_events_df = session.get_events(
        app_name=app_name,
        app_version=app_version,
        record_ids=[record_id]
    )

    if all_events_df.empty:
        print("\n   - [错误]: 未能从数据库中获取到任何 Events。请检查前面的步骤是否有误。")
    else:
        print(f"   - [调试信息] Events DataFrame 的列名: {all_events_df.columns.to_list()}")
        
        # 初始化变量
        user_input = '输入信息未找到。'
        app_output_str = '输出信息未找到。'
        feedback_results = []
        
        # 遍历 DataFrame，提取关键信息
        for _, row in all_events_df.iterrows():
            record_data = row.get('record', {})  # span 基本 info，如 name
            attributes = row.get('record_attributes', {})  # 属性 dict
            
            # 调试：打印每个 span 的 name 和 attributes keys（可选移除）
            span_name = record_data.get('name', '未知')
            print(f"   - [调试] Span name: {span_name}, Attributes keys: {list(attributes.keys())}")
            
            # 提取 Input/Output（span_type == 'record_root'）
            if attributes.get('ai.observability.span_type') == 'record_root':
                user_input = attributes.get('ai.observability.record_root.input', '输入信息未找到。')
                app_output_str = attributes.get('ai.observability.record_root.output', '输出信息未找到。')
            
            # 提取 Feedback（span_type == 'eval_root'，检查 metric_name == 'Context Relevance'）
            if attributes.get('ai.observability.span_type') == 'eval_root' and attributes.get('ai.observability.eval_root.metric_name') == 'Context Relevance':
                result_value = attributes.get('ai.observability.eval_root.score')  # score 值
                # Reason: 优先 explanation，fallback metadata.reason
                result_reason = attributes.get('ai.observability.eval.explanation', attributes.get('ai.observability.eval.metadata.reason', '未找到推理'))
                if result_value is not None:
                    feedback_results.append({
                        "name": attributes.get('ai.observability.eval_root.metric_name'),
                        "value": result_value,
                        "reason": result_reason
                    })

        # 显示结果
        print("\n" + "="*50)
        print("📊 TruLens 追踪诊断结果 (OTel 模式)")
        print("="*50)
        print(f"👤 **用户输入 (Input):**")
        try:
            input_data = json.loads(user_input)
            print(f"   {input_data['messages'][0]['content']}")
        except:
            print(f"   {user_input}")
        print("\n" + "-"*50 + "\n")
        print(f"🤖 **应用输出 (Output):**")
        try:
            output_data = json.loads(app_output_str)
            last_message_content = output_data.get('messages', [{}])[-1].get('content', app_output_str)
            print(json.dumps(json.loads(last_message_content), indent=4, ensure_ascii=False))
        except:
            print(f"   {app_output_str}")
        print("\n" + "-"*50 + "\n")
        print("⭐ **Feedback 评估结果:**")
        if not feedback_results:
            print("   - [提示] 在 Events 中未找到 'Context Relevance' 的 Feedback 结果。")
            print("   - 可能原因：Feedback 计算失败（检查 .env 中的 GOOGLE_API_KEY、网络、API 配额）、或异步未完成。")
            print("   - 建议：1. 用 dashboard 检查 trace 是否有 feedback attributes。2. 切换 provider 如 OpenAI（需 OPENAI_API_KEY）。3. 禁用 OTel 模式测试（os.environ['TRULENS_OTEL_TRACING'] = '0'），用 session.get_records_and_feedback() 查询。")
        else:
            for feedback in feedback_results:
                feedback_name = feedback['name']
                feedback_value = feedback['value']
                feedback_reason = feedback['reason']
                emoji = "✅" if feedback_value >= 0.7 else ("🤔" if feedback_value >= 0.5 else "❌")
                print(f"   - {emoji} {feedback_name}: {feedback_value:.2f}")
                print(f"     - 推理 (Reason): {feedback_reason}")
        print("="*50)

# --- 9. 启动 TruLens Dashboard ---
print("\n🚀 步骤 9: 启动 TruLens Dashboard 以进行可视化分析...")
print("   - Dashboard 是查看 OTel 模式下详细信息的最佳方式。")
print("   - 在终端按 Ctrl+C 来停止 Dashboard。")

try:
    run_dashboard()
except Exception as e:
    print(f"\n   - [错误]: 启动 Dashboard 失败: {e}")