import os
import warnings
from dotenv import load_dotenv
from trulens.core import Feedback
from trulens.core.feedback.selector import Selector
from trulens.providers.google import Google

# --- 1. 环境设置与初始化 ---
# 从 .env 文件加载环境变量 (比如 GOOGLE_API_KEY)
load_dotenv(override=True)
warnings.filterwarnings("ignore")
os.environ["TRULENS_OTEL_TRACING"] = "1"

print("初始化 Gemini Provider...")
# 初始化 Provider，用于调用 Google 的 LLM 进行评估
# 请确保您的环境中已设置 GOOGLE_API_KEY
try:
    gemini_provider = Google(model_name="gemini-1.5-pro-latest")
except Exception as e:
    print(f"初始化 Provider 失败: {e}")
    print("请确保您的 .env 文件中已正确设置 GOOGLE_API_KEY。")
    exit()

# --- 2. 定义中文业务案例 ---

# 案例 A: 一个有待改进的计划 (目标是得到一个中间分数, 而非 0 分)
# 这个计划有一些方向，但缺乏具体、可执行的细节，是现实中常见的“不够好”的计划。
plan_mediocre_chinese = """
用户目标: 本周我们应该优先跟进哪些销售线索？请为每个高优先级线索制定出具体的行动计划。

计划 (有待改进版):
1. 从CRM中筛选出近期的重要销售线索。
2. 找出其中交易额最高的几个大客户。
3. 整理这些客户的过往沟通记录和当前所处的销售阶段。
4. 将信息汇总成一份报告，准备在周会上进行讨论。
"""

# 案例 B: 一个优秀的计划
# 这个计划逻辑严谨，步骤清晰，标准明确，完美回应了用户的目标。
plan_excellent_chinese = """
用户目标: 本周我们应该优先跟进哪些销售线索？请为每个高优先级线索制定出具体的行动计划。

计划 (优秀版):
1. 从CRM中筛选出所有状态为“开放”的商机，且满足以下任一条件：
   - “下一步行动日期”在未来14天内。
   - “下一步行动日期”为空或已过期。
2. 在上述商机中，进一步筛选出交易额大于10万元人民币或线索评级为“高”的线索。
3. 将筛选后的线索，按照“签约阶段紧迫程度”（如接近签约日期、有失单风险）和“潜在收入”进行降序排序，得到高优先级列表。
4. 对列表中的每一个高优先级线索：
   a. 提取最新的互动记录、关键决策人信息以及当前面临的阻碍。
   b. 识别任何逾期或缺失的关键行动项。
   c. 基于以上信息，提出具体、高价值的下一步行动建议（例如：安排产品演示、发送修改后的报价单、请求销售经理介入等）。
5. 将所有建议整合成本周的优先行动清单，并明确负责人和截止日期。
6. 以表格形式呈现最终结果，包含列：客户名称、预计合同额、销售阶段、紧迫性评分、下一步行动、负责人、截止日期。
"""

# --- 3. 定义 Feedback 函数 ---

# 定义一个名为 "计划质量评估" 的 Feedback 函数。
# 它使用 gemini_provider 的 plan_quality_with_cot_reasons 方法进行评估。
# .on({"trace": Selector(trace_level=True)}) 表示这个函数需要获取完整的 Trace 作为输入。
f_plan_quality_cn = Feedback(
    gemini_provider.plan_quality_with_cot_reasons,
    name="计划质量评估",
).on({
    "trace": Selector(trace_level=True),
})

# --- 4. 辅助函数：美化输出结果 ---

def display_evaluation_results(plan_name: str, plan_content: str, score: float, reason: dict):
    """一个用于清晰展示评估结果的辅助函数。"""
    print("\n" + "="*50)
    print(f"评估案例: {plan_name}")
    print(f"计划内容:\n{plan_content}")
    print("-" * 50)
    
    # 将得分从 0-1 区间转换为更直观的 0-100 分制
    score_100 = score * 100
    print(f"📈 计划质量得分: {score_100:.1f} / 100.0")
    
    # 解析并格式化评估理由
    reason_text = reason.get('reason', '没有提供评估理由。')
    print("\n📝 Gemini 评估员的详细理由:")
    
    # 理由文本通常包含固定的关键词，我们可以用它们来分割和格式化
    if "Supporting Evidence:" in reason_text:
        parts = reason_text.split("Supporting Evidence:", 1)
        criteria_part = parts[0].replace("Criteria:", "").strip()
        evidence_part = parts[1].strip()
        print(f"\n【评估标准回顾】\n{criteria_part}\n")
        print(f"【具体证据与分析】\n{evidence_part}")
    else:
        print(reason_text)
        
    print("="*50 + "\n")


# --- 5. 执行评估并展示结果 ---

def main():
    """主执行函数"""
    print("\n开始评估两个不同质量的计划...")

    # 评估第一个：有待改进的计划
    print("--- 正在评估一个有待改进的计划... ---")
    score1, reason1 = f_plan_quality_cn(plan_mediocre_chinese)
    display_evaluation_results("有待改进的计划", plan_mediocre_chinese, score1, reason1)

    # 评估第二个：优秀的计划
    print("--- 正在评估一个优秀的计划... ---")
    score2, reason2 = f_plan_quality_cn(plan_excellent_chinese)
    display_evaluation_results("优秀的计划", plan_excellent_chinese, score2, reason2)

if __name__ == "__main__":
    main()