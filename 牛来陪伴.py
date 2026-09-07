import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

# 保存对话信息函数
def save_session():
    # 1 保存当前会话信息
    if st.session_state.current_session:
        # 构建新的会话对象
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

        # 如果 sessions 目录不存在，则创建
        if not os.path.exists("sessions"):
            os.makedirs("sessions")
         # 保存对话数据
        with open(f'sessions/{st.session_state.current_session}.json','w',encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

    
# 生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d %H-%M-%S")

# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    # 加载sessions目录下的所有文件
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True)
    return session_list            

# 加载指定的会话信息函数
def load_session(session_name):
    try:
        if os.path.exists(f'sessions/{session_name}.json'):
            with open(f'sessions/{session_name}.json','r',encoding='utf-8') as f:
                session_data = json.load(f)
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_data["current_session"]
                st.session_state.messages = session_data["messages"]
    except Exception:
        st.error("加载会话失败")

#  删除指定的会话信息函数
def delete_session(session_name):
    try:
        if os.path.exists(f'sessions/{session_name}.json'):
            os.remove(f'sessions/{session_name}.json')#删除文件
            # 如果删除时当前的对话，那需要出现一个新的对话页面
            if session_name == st.session_state.current_session:
                st.session_state.messages = []                    
                st.session_state.current_session = generate_session_name()
    except Exception:
            st.error("删除会话失败")
    

st.set_page_config(
    page_title="牛来陪伴",
    page_icon="🦸‍♂️",
    # 布局
    layout="wide",
    # 侧边栏
    initial_sidebar_state="expanded",
    menu_items={}
)

# 大标题
st.title("牛来陪伴")

# logo
st.logo("resources/豪情.jpg")

# 系统提示词
system_prompt = """
        你叫%s,现在是用户的好伙伴,请完全带入用户伙伴角色。
        规则:
            1.每次只会一条消息
            2.禁止任何场景或状态描述性文字
            3.匹配用户的语言
            4.回复简短，像微信聊天
            5.禁止任何恶意或不实信息
            6.禁止任何广告或推销
            7.用符合牛的性格的方式对话
        牛的性格:
           %s   
        你必须严格遵守上述规则来回复用户

    """

#初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 昵称
if 'nick_name' not in st.session_state:
    st.session_state.nick_name = '牛震'

# 性格
if 'nature' not in st.session_state:
    st.session_state.nature = '你是一个很骄傲的人'

# 会话标识
if 'current_session' not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 显示聊天记录
st.text(f'会话名称:{st.session_state.current_session}')
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.chat_message(
            "assistant",
            avatar="./resources/niulai.jpg"
        ).write(message["content"])
    else:
        st.chat_message("user").write(message["content"])


# 创建与AI大模型交互的客户端对象
client = OpenAI(
    api_key=st.secrets["platform_api"]["api_key"],
    base_url=st.secrets["platform_api"]["base_url"]
)


# 左侧的侧边栏-with 是streamlit上下文管理器
with st.sidebar:
    st.subheader("AI控制面板")

    # 新建会话按钮
    if st.button("新建会话",width='stretch',icon="💬"):
        # 1 保存当前会话信息
        save_session()
        # 2 构建新的会话
        if st.session_state.messages:#如果聊天记录不为空，则清空聊天记录并重新生成会话标识
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()    
            st.rerun()#刷新页面
    # 会话历史
    st.text('会话历史')
    session_list = load_sessions()
    for session in session_list:
        col1,col2 =st.columns([4,1])
        with col1:
            # 加载会话信息  
            if st.button(session,width ='stretch',icon="😶‍🌫️",key=f'load_{session}',type='primary' if session == st.session_state.current_session else 'secondary'):
                load_session(session)
                st.rerun()#刷新页面 
        with col2:
            # 删除会话信息
            if st.button(session,width ='stretch',icon="❌️",key=f'delete_{session}'):
                delete_session(session)
                st.rerun()#刷新页面

    # 分割线
    st.divider()

    # 牛来信息  
    st.subheader("牛来信息")
    # 昵称输入框
    nick_name = st.text_input('昵称',placeholder='请输入牛的名称', value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    # 性格输入框
    nature = st.text_area('性格',placeholder='请输入牛的性格', value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature
    # 会话标识
    if 'current_session' not in st.session_state:
        now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        st.session_state.current_session = now

# 消息输入框
prompt =st.chat_input("请输入你的消息")
if prompt:#字符串会自动转化为布尔值，非空则为True
    st.chat_message("user").write(prompt)
    print('--------------->调用AI大模型，提示词：',prompt)

    # 将用户输入的消息添加到聊天记录中
    st.session_state.messages.append({"role": "user", "content": prompt})


    # AI大模型输出
    # 调用AI大模型进行对话
    print("======== 准备调用 Qwen ========")
    response = client.chat.completions.create(
        model=st.secrets["platform_api"]["model"],
        messages=[
            {"role": "system", "content": system_prompt %(st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.messages
        ],
        stream=True,
    )
    print("======== 已经拿到 response ========")
    # 输出大模型返回的结果(流式输出)
    response_message = st.empty()  # 创建一个空的文本框

    # print('--------------->AI大模型返回的结果：',response.choices[0].message.content)
    # st.chat_message("assistant",avatar="./resources/niulai.jpg").write(response.choices[0].message.content)

    # 处理流式输出
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant",avatar="./resources/niulai.jpg").write(full_response)
    print("最终回复：", full_response)
    # 将AI大模型的输出添加到聊天记录中
    st.session_state.messages.append({"role": "assistant", "content": full_response})


    # 保存对话信息
    save_session()
