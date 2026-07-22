"""
销冠智语 AI 智能体 — 谈单助手集成模块
嵌入方式：在 app.py 中 import 后调用 render_ai_panel()
"""
import streamlit as st
import requests
import json


SALESWHISPER_API = "http://localhost:9000"  # ⚠️ 部署到服务器后改为 http://你的服务器IP:9000

# 广州各区的学校列表
DISTRICT_SCHOOLS = {
    "越秀": ["省实", "执信", "二中", "广大附中", "铁一", "七中", "十六中", "培正"],
    "天河": ["天河中学", "113中", "天河外国语", "汇景实验", "广州中学"],
    "海珠": ["五中", "南武", "九十七中", "海珠实验"],
    "荔湾": ["真光", "一中", "四中", "西关外国语"],
    "白云": ["培英", "白云广雅", "白云华附", "白云省实"],
    "番禺": ["仲元", "番禺中学", "番禺实验"],
    "黄埔": ["玉岩", "八十六中", "科学城中学"],
    "花都": ["秀全", "邝维煜纪念中学"],
    "增城": ["增城中学", "增城一中"],
    "从化": ["从化中学", "从化六中"],
    "南沙": ["南沙一中", "南沙广附"],
}


def render_ai_panel():
    """渲染 AI 智能诊断面板"""
    with st.expander("🧠 AI 智能学情诊断", expanded=False):
        st.markdown("""
        <div style="background:linear-gradient(135deg,#4F46E5,#7C3AED);padding:16px 20px;border-radius:12px;margin-bottom:16px;">
            <span style="color:white;font-weight:700;font-size:1rem;">🤖 AI 课程顾问</span>
            <span style="color:rgba(255,255,255,0.8);font-size:0.8rem;margin-left:8px;">输入学生情况，AI 自动分析失分原因 + 升学建议</span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            grade = st.selectbox("年级", ["初一", "初二", "初三"], key="ai_grade")
        with col2:
            subject = st.selectbox("科目", ["数学", "英语", "语文", "物理", "化学"], key="ai_subject")
        with col3:
            score = st.text_input("分数", placeholder="如: 72", key="ai_score")

        col4, col5 = st.columns(2)
        with col4:
            district = st.selectbox("所在区域（可选）", ["-"] + list(DISTRICT_SCHOOLS.keys()), key="ai_district")
        with col5:
            target_school = st.selectbox("目标学校（可选）", ["-"] + (DISTRICT_SCHOOLS.get(district, []) if district != "-" else []), key="ai_school")

        concern = st.text_area("家长具体问题（可选）", placeholder="如: 孩子数学一直在70分左右上不去，担心初二下学期函数和几何更跟不上...", key="ai_concern")

        if st.button("🔍 AI 智能分析", use_container_width=True, type="primary", key="ai_analyze_btn"):
            if not score:
                st.warning("请先输入分数")
                return

            with st.spinner("AI 正在分析中..."):
                try:
                    resp = requests.post(
                        f"{SALESWHISPER_API}/api/ai/analyze",
                        json={
                            "grade": grade,
                            "subject": subject,
                            "score": score,
                            "district": district if district != "-" else "",
                            "target_school": target_school if target_school != "-" else "",
                            "concern": concern
                        },
                        timeout=30
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        display_analysis(data)
                    else:
                        st.error(f"AI 服务暂不可用 ({resp.status_code})。请确认后端已启动。")
                except requests.exceptions.ConnectionError:
                    st.error(f"无法连接到 AI 服务 ({SALESWHISPER_API})。请确认后端正在运行。")
                except Exception as e:
                    st.error(f"分析失败: {e}")


def display_analysis(data: dict):
    """展示 AI 分析结果"""
    analysis = data.get("analysis", "")
    thinking = data.get("thinking", [])
    recommendations = data.get("recommendations", [])
    diagnosis = data.get("diagnosis", {})
    keywords = data.get("search_keywords", [])

    # 用 st.markdown 渲染分析报告
    st.markdown("---")
    st.markdown("### 📊 AI 诊断结果")

    # 诊断概览卡片
    level = diagnosis.get("level", "未知")
    rate = diagnosis.get("rate", 0)
    level_colors = {"优秀": "#10B981", "良好": "#3B82F6", "中等": "#F59E0B", "薄弱": "#EF4444", "严重薄弱": "#DC2626"}
    color = level_colors.get(level, "#6B7280")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("水平定位", level, delta=f"得分率 {rate:.0f}%")
    with col_b:
        st.metric("推理步骤", f"{len(thinking)} 步")
    with col_c:
        st.metric("建议数量", f"{len(recommendations)} 条")

    # 推理过程（可折叠）
    with st.expander("🔍 查看 AI 推理过程", expanded=False):
        for i, step in enumerate(thinking, 1):
            icon = ["📍", "🔬", "📜", "🎯", "💡"][min(i - 1, 4)]
            st.markdown(f"{icon} {step}")

    # 完整分析报告
    st.markdown(analysis)

    # 建议操作
    if recommendations:
        st.markdown("---")
        st.markdown("### 💡 下一步建议")
        for rec in recommendations:
            st.markdown(f"- {rec}")

    # 相关话术搜索
    if keywords:
        st.markdown("---")
        st.markdown("### 🔗 相关话术")
        st.caption("点击可搜索话术库: " + ", ".join(keywords[:5]))


def render_policy_card():
    """渲染中考政策卡片"""
    with st.expander("🏫 2027广州中考新政速览", expanded=False):
        try:
            resp = requests.get(f"{SALESWHISPER_API}/api/ai/policy", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                st.markdown(f"**{data.get('title', '')}**")
                st.caption(data.get('effective', ''))

                subjects = data.get("subjects", {})
                if subjects:
                    cols = st.columns(4)
                    for i, (name, info) in enumerate(subjects.items()):
                        with cols[i % 4]:
                            change = info.get("变化", "")
                            emoji = "📈" if change.startswith("+") else "📉" if change.startswith("-") else "➡️"
                            st.metric(
                                label=f"{emoji} {name}",
                                value=f"{info.get('分值', '?')}分",
                                delta=change if change != "不变" else None
                            )

                unchanged = data.get("key_unchanged", [])
                if unchanged:
                    with st.expander("不变的政策", expanded=False):
                        for item in unchanged:
                            st.markdown(f"- {item}")
        except Exception:
            st.caption("政策数据暂不可用")
