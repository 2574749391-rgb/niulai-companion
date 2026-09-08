import streamlit as st
import os
import json
from datetime import datetime
from openai import OpenAI


# =========================================================
# 1. 基础函数
# =========================================================

# 生成会话名称
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d %H-%M-%S")


# 保存当前会话
def save_session():
    if not st.session_state.current_session:
        return

    session_data = {
        "nick_name": st.session_state.nick_name,
        "nature": st.session_state.nature,
        "current_session": st.session_state.current_session,
        "messages": st.session_state.messages
    }

    # sessions 文件夹不存在就自动创建
    if not os.path.exists("sessions"):
        os.makedirs("sessions")

    file_path = f"sessions/{st.session_state.current_session}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            session_data,
            f,
            ensure_ascii=False,
            indent=2
        )


# 加载所有历史会话
def load_sessions():
    session_list = []

    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")

        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])

    # 时间新的排在前面
    session_list.sort(reverse=True)

    return session_list


# 加载指定会话
def load_session(session_name):
    try:
        file_path = f"sessions/{session_name}.json"

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            st.session_state.nick_name = session_data.get(
                "nick_name",
                "牛震"
            )

            st.session_state.nature = session_data.get(
                "nature",
                "你是一个很骄傲的人"
            )

            st.session_state.current_session = session_data.get(
                "current_session",
                session_name
            )

            st.session_state.messages = session_data.get(
                "messages",
                []
            )

    except Exception as e:
        st.error(f"加载会话失败：{e}")


# 删除指定会话
def delete_session(session_name):
    try:
        file_path = f"sessions/{session_name}.json"

        if os.path.exists(file_path):
            os.remove(file_path)

        # 如果删除的是当前会话
        if session_name == st.session_state.current_session:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()

    except Exception as e:
        st.error(f"删除会话失败：{e}")


# =========================================================
# 2. Streamlit 页面设置
# =========================================================

st.set_page_config(
    page_title="牛来陪伴",
    page_icon="🦸‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)


# =========================================================
# 3. 初始化 Session State
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "nick_name" not in st.session_state:
    st.session_state.nick_name = "牛震"

if "nature" not in st.session_state:
    st.session_state.nature = "你是一个很骄傲的人"

if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()


# =========================================================
# 4. 页面标题和 Logo
# =========================================================

st.title("牛来陪伴")

try:
    st.logo("resources/豪情.jpg")
except Exception:
    pass


# =========================================================
# 5. 系统提示词
# =========================================================

system_prompt = """
你叫%s，现在是用户的好伙伴，请完全代入用户伙伴角色。

规则：
1. 每次只回复一条消息。
2. 禁止任何场景或状态描述性文字。
3. 匹配用户使用的语言。
4. 回复简短，像微信聊天。
5. 禁止任何恶意或不实信息。
6. 禁止任何广告或推销。
7. 用符合牛性格的方式进行对话。

牛的性格：
%s

你必须严格遵守上述规则回复用户。
"""


# =========================================================
# 6. 创建 AI 客户端
# =========================================================

try:
    client = OpenAI(
        api_key=st.secrets["platform_api"]["api_key"],
        base_url=st.secrets["platform_api"]["base_url"],
        timeout=60.0
    )

except Exception as e:
    st.error(f"API 配置读取失败：{e}")
    st.stop()


# =========================================================
# 7. 左侧控制面板
# =========================================================

with st.sidebar:

    st.subheader("AI控制面板")

    # -------------------------
    # 新建会话
    # -------------------------

    if st.button(
        "新建会话",
        width="stretch",
        icon="💬"
    ):

        # 先保存旧会话
        if st.session_state.messages:
            save_session()

        # 创建新会话
        st.session_state.messages = []
        st.session_state.current_session = generate_session_name()

        st.rerun()


    # -------------------------
    # 历史会话
    # -------------------------

    st.text("会话历史")

    session_list = load_sessions()

    for session in session_list:

        col1, col2 = st.columns([4, 1])

        with col1:

            button_type = (
                "primary"
                if session == st.session_state.current_session
                else "secondary"
            )

            if st.button(
                session,
                width="stretch",
                icon="🤖",
                key=f"load_{session}",
                type=button_type
            ):
                # 先保存当前会话
                if st.session_state.messages:
                    save_session()

                # 加载目标会话
                load_session(session)

                st.rerun()

        with col2:

            if st.button(
                "✕",
                width="stretch",
                key=f"delete_{session}"
            ):
                delete_session(session)
                st.rerun()


    # -------------------------
    # 分割线
    # -------------------------

    st.divider()


    # -------------------------
    # 牛的信息
    # -------------------------

    st.subheader("牛来信息")

    nick_name = st.text_input(
        "昵称",
        placeholder="请输入牛的名称",
        value=st.session_state.nick_name
    )

    if nick_name:
        st.session_state.nick_name = nick_name


    nature = st.text_area(
        "性格",
        placeholder="请输入牛的性格",
        value=st.session_state.nature
    )

    if nature:
        st.session_state.nature = nature


# =========================================================
# 8. 显示当前会话名称
# =========================================================

st.text(
    f"会话名称:{st.session_state.current_session}"
)


# =========================================================
# 9. 显示聊天记录
# =========================================================

for message in st.session_state.messages:

    if message["role"] == "assistant":

        st.chat_message(
            "assistant",
            avatar="resources/niulai.jpg"
        ).write(message["content"])

    elif message["role"] == "user":

        st.chat_message(
            "user"
        ).write(message["content"])


# =========================================================
# 10. 用户输入
# =========================================================

prompt = st.chat_input(
    "请输入你的消息"
)


# =========================================================
# 11. 调用 AI
# =========================================================

if prompt:

    # -------------------------
    # 显示用户消息
    # -------------------------

    st.chat_message(
        "user"
    ).write(prompt)


    # -------------------------
    # 保存用户消息
    # -------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    # -------------------------
    # 最近 6 条上下文
    # -------------------------

    recent_messages = st.session_state.messages[-6:]


    # -------------------------
    # AI 回复
    # -------------------------

    with st.chat_message(
        "assistant",
        avatar="resources/niulai.jpg"
    ):

        with st.spinner(
            f"🤔 {st.session_state.nick_name}正在思考..."
        ):

            try:

                response = client.chat.completions.create(

                    model=st.secrets["platform_api"]["model"],

                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt % (
                                st.session_state.nick_name,
                                st.session_state.nature
                            )
                        },
                        *recent_messages
                    ],

                    stream=False
                )


                # 获取模型回复
                full_response = response.choices[0].message.content


                # 防止接口返回 None
                if full_response:

                    st.write(full_response)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": full_response
                        }
                    )

                else:

                    st.error(
                        "❌ API 调用成功，但模型返回了空内容。"
                    )


            except Exception as e:

                st.error(
                    f"❌ AI 接口调用失败，原因：{e}"
                )


    # -------------------------
    # 保存最新聊天记录
    # -------------------------

    save_session()
