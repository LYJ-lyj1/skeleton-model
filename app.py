import streamlit as st
import base64
import os
from io import StringIO
import csv

# =============== 页面配置 ===========
st.set_page_config(
    page_title="人体数字模型定位平台",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========== 辅助函数 ===========
def reset_all_inputs():
    """重置所有输入字段"""
    st.session_state.spine_values = [0.0] * 25
    st.session_state.joint_data = {
        'left_shoulder': [0.0, 0.0, 0.0],
        'left_elbow': 0.0,
        'left_hip': [0.0, 0.0, 0.0],
        'left_knee': 0.0,
        'right_shoulder': [0.0, 0.0, 0.0],
        'right_elbow': 0.0,
        'right_hip': [0.0, 0.0, 0.0],
        'right_knee': 0.0
    }
    st.rerun()

def load_real_model_image(view_key):
    """从real_human_model_images文件夹加载3D建模图"""
    # 视图映射到图片编号
    view_to_image = {
        'iso_pos': 1,   # 正等轴测视图
        'iso_neg': 2,   # 反等轴测视图
        'front': 3,     # 前视图
        'side': 4,      # 侧视图
        'top': 5        # 俯视图
    }
    
    image_index = view_to_image.get(view_key, 1)
    filename = f"Human_Pose_{image_index:03d}.png"
    
    paths_to_try = [
        os.path.join("real_human_model_images", filename),
        filename,
    ]
    
    for filepath in paths_to_try:
        if os.path.exists(filepath):
            try:
                with open(filepath, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception as e:
                st.warning(f"加载图片失败: {e}")
    
    return None

def load_anatomy_image(joint_name):
    """加载解剖图"""
    # 解剖图映射
    image_map = {
        "left_shoulder": "shoulder_left.png",
        "right_shoulder": "shoulder_right.png",
        "left_elbow": "elbow_left.png",
        "right_elbow": "elbow_right.png",
        "left_hip": "hip_left.png",
        "right_hip": "hip_right.png",
        "left_knee": "knee_left.png",
        "right_knee": "knee_right.png",
    }
    
    filename = image_map.get(joint_name)
    if filename:
        paths_to_try = [
            os.path.join("anatomy_images", filename),
            filename,
        ]
        
        for filepath in paths_to_try:
            if os.path.exists(filepath):
                try:
                    with open(filepath, "rb") as f:
                        return base64.b64encode(f.read()).decode()
                except Exception as e:
                    st.warning(f"加载图片失败: {filepath}: {e}")
                    return None
    
    return None

def get_joint_description(joint_name):
    """获取关节的解剖学描述"""
    descriptions = {
        "left_shoulder": """
        左肩解剖:
        ▪ 类型: 球窝关节

        ▪ 组成部分: 肱骨头 + 肩胛骨的关节盂

        ▪ 运动: 屈曲/伸展, 外展/内收, 旋转

        ▪ 特点: 人体最灵活的关节

        """,
        "right_shoulder": """
        右肩解剖:
        ▪ 类型: 球窝关节

        ▪ 组成部分: 肱骨头 + 肩胛骨的关节盂

        ▪ 运动: 屈曲/伸展, 外展/内收, 旋转

        """,
        "left_elbow": """
        左肘解剖:
        ▪ 类型: 铰链关节

        ▪ 组成部分: 远端肱骨 + 尺骨鹰嘴 + 桡骨头

        ▪ 运动: 主要是屈曲/伸展

        """,
        "right_elbow": """
        右肘解剖:
        ▪ 类型: 铰链关节

        ▪ 组成部分: 远端肱骨 + 尺骨鹰嘴 + 桡骨头

        ▪ 运动: 主要是屈曲/伸展

        """,
        "left_hip": """
        左髋解剖:
        ▪ 类型: 球窝关节

        ▪ 组成部分: 股骨头 + 髋臼

        ▪ 运动: 多方向运动

        ▪ 特点: 承重关节, 稳定性高

        """,
        "right_hip": """
        右髋解剖:
        ▪ 类型: 球窝关节

        ▪ 组成部分: 股骨头 + 髋臼

        ▪ 运动: 多方向运动

        """,
        "left_knee": """
        左膝解剖:
        ▪ 类型: 复合关节

        ▪ 组成部分: 股骨, 胫骨, 髌骨

        ▪ 运动: 主要是屈曲/伸展

        """,
        "right_knee": """
        右膝解剖:
        ▪ 类型: 复合关节

        ▪ 组成部分: 股骨, 胫骨, 髌骨

        ▪ 运动: 主要是屈曲/伸展

        """
    }
    return descriptions.get(joint_name, "关节解剖图")

# 脊柱节段标签
spine_labels = [f"C{i+1}" for i in range(7)] + [f"T{i+1}" for i in range(12)] + [f"L{i+1}" for i in range(5)] + ["S1"]

# 初始化会话状态
if 'spine_values' not in st.session_state:
    st.session_state.spine_values = [0.0] * 25
if 'joint_data' not in st.session_state:
    st.session_state.joint_data = {
        'left_shoulder': [0.0, 0.0, 0.0],
        'left_elbow': 0.0,
        'left_hip': [0.0, 0.0, 0.0],
        'left_knee': 0.0,
        'right_shoulder': [0.0, 0.0, 0.0],
        'right_elbow': 0.0,
        'right_hip': [0.0, 0.0, 0.0],
        'right_knee': 0.0
    }
if 'current_view' not in st.session_state:
    st.session_state.current_view = "iso_pos"

# =============== 顶部标题 (中英文双语) ============
st.markdown("""
    <h1 style='text-align: center; color: #2c3e50; margin-bottom: 10px;'>
        人体数字模型前处理定位平台
    </h1>
    <h3 style='text-align: center; color: #7f8c8d; margin-bottom: 30px;'>
        Human Body Model Positioning Toolbox
    </h3>
""", unsafe_allow_html=True)
st.markdown("---")

# =============== 主显示区 ============
st.markdown("## 🖼️ 模型预览")

# 预设视角按钮 - 5个按钮对应5个视图
st.markdown("### 预设视角")
view_cols = st.columns(5)
views = ["正等轴测", "透视图", "侧视图", "俯视图", "正视图"]
view_keys = ["iso_pos", "iso_neg", "front", "side", "top"]

# 创建5个视图按钮
for i, (view_name, view_key) in enumerate(zip(views, view_keys)):
    with view_cols[i]:
        is_active = st.session_state.current_view == view_key
        btn_type = "primary" if is_active else "secondary"
        
        if st.button(view_name, key=f"view_{view_key}", use_container_width=True, type=btn_type):
            st.session_state.current_view = view_key
            st.rerun()

st.markdown("---")

# 显示当前视图
st.markdown(f"### 当前视图: {views[view_keys.index(st.session_state.current_view)]}")

# 加载并显示当前视图的3D模型图片
img_b64 = load_real_model_image(st.session_state.current_view)

if img_b64:
    # 居中显示大图
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(f"data:image/png;base64,{img_b64}", 
                 caption=f"专业3D人体模型 - {views[view_keys.index(st.session_state.current_view)]}",
                 use_container_width=True)
else:
    st.error("⚠️ 未找到3D模型图片")
    st.info("""
    请确保：
    1. 创建 'real_human_model_images' 文件夹
    2. 将师兄提供的5张图片放入文件夹
    3. 图片命名为: 
       - Human_Pose_001.png (正等轴测视图)
       - Human_Pose_002.png (反等轴测视图)
       - Human_Pose_003.png (前视图)
       - Human_Pose_004.png (侧视图)
       - Human_Pose_005.png (俯视图)
    """)

# =============== 侧边栏: 数据输入 ===============
with st.sidebar:
    st.header("📥 数据输入面板")
    
    # 脊柱角度输入
    st.subheader("脊柱角度")
    st.caption("C1-C7: 颈椎 | T1-T12: 胸椎 | L1-L5: 腰椎 | S1: 骶骨")
    
    spine_cols = st.columns(5)
    for i in range(25):
        with spine_cols[i % 5]:
            st.session_state.spine_values[i] = st.number_input(
                label=spine_labels[i],
                min_value=-180.0,
                max_value=180.0,
                value=st.session_state.spine_values[i],
                step=1.0,
                key=f"spine_{i}"
            )
    
    st.markdown("---")
    
    # 关节角度输入
    st.subheader("关节角度")
    
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.markdown("左侧关节")
        
        # 左肩
        shoulder_title_cols = st.columns([3, 1])
        with shoulder_title_cols[0]:
            st.markdown("左肩")
        with shoulder_title_cols[1]:
            with st.popover("❓", help="点击查看左肩解剖图"):
                st.markdown("左肩解剖")
                img_b64 = load_anatomy_image("left_shoulder")
                if img_b64:
                    st.image(f"data:image/png;base64,{img_b64}", 
                            caption="左肩解剖图", 
                            use_container_width=True)
                else:
                    st.info("请将左肩解剖图放入anatomy_images文件夹")
                st.markdown(get_joint_description("left_shoulder"))
        
        l_shoulder_cols = st.columns(3)
        for j in range(3):
            with l_shoulder_cols[j]:
                angle_names = ["屈/伸", "外展/内收", "旋转"]
                st.session_state.joint_data['left_shoulder'][j] = st.number_input(
                    label=angle_names[j],
                    min_value=-180.0,
                    max_value=180.0,
                    value=st.session_state.joint_data['left_shoulder'][j],
                    step=1.0,
                    key=f"left_shoulder_{j}",
                    label_visibility="collapsed"
                )
        
        # 左肘
        elbow_title_cols = st.columns([3, 1])
        with elbow_title_cols[0]:
            st.markdown("左肘")
        with elbow_title_cols[1]:
            with st.popover("❓", help="点击查看左肘解剖图"):
                st.markdown("左肘解剖")
                img_b64 = load_anatomy_image("left_elbow")
                if img_b64:
                    st.image(f"data:image/png;base64,{img_b64}", 
                            caption="左肘解剖图", 
                            use_container_width=True)
                else:
                    st.info("请将左肘解剖图放入anatomy_images文件夹")
                st.markdown(get_joint_description("left_elbow"))
        
        st.session_state.joint_data['left_elbow'] = st.number_input(
            label="屈曲角度",
            min_value=-180.0,
            max_value=180.0,
            value=st.session_state.joint_data['left_elbow'],
            step=1.0,
            key="left_elbow",
            label_visibility="collapsed"
        )
        
        # 左髋
        hip_title_cols = st.columns([3, 1])
        with hip_title_cols[0]:
            st.markdown("左髋")
        with hip_title_cols[1]:
            with st.popover("❓", help="点击查看左髋解剖图"):
                st.markdown("左髋解剖")
                img_b64 = load_anatomy_image("left_hip")
                if img_b64:
                    st.image(f"data:image/png;base64,{img_b64}", 
                            caption="左髋解剖图", 
                            use_container_width=True)
                else:
                    st.info("请将左髋解剖图放入anatomy_images文件夹")
                st.markdown(get_joint_description("left_hip"))
        
        l_hip_cols = st.columns(3)
        for j in range(3):
            with l_hip_cols[j]:
                angle_names = ["屈/伸", "外展/内收", "旋转"]
                st.session_state.joint_data['left_hip'][j] = st.number_input(
                    label=angle_names[j],
                    min_value=-180.0,
                    max_value=180.0,
                    value=st.session_state.joint_data['left_hip'][j],
                    step=1.0,
                    key=f"left_hip_{j}",
                    label_visibility="collapsed"
                )
        
        # 左膝
        knee_title_cols = st.columns([3, 1])
        with knee_title_cols[0]:
            st.markdown("左膝")
        with knee_title_cols[1]:
            with st.popover("❓", help="点击查看左膝解剖图"):
                st.markdown("左膝解剖")
                img_b64 = load_anatomy_image("left_knee")
                if img_b64:
                    st.image(f"data:image/png;base64,{img_b64}", 
                            caption="左膝解剖图", 
                            use_container_width=True)
                else:
                    st.info("请将左膝解剖图放入anatomy_images文件夹")
                st.markdown(get_joint_description("left_knee"))
        
        st.session_state.joint_data['left_knee'] = st.number_input(
            label="屈曲角度",
            min_value=-180.0,
            max_value=180.0,
            value=st.session_state.joint_data['left_knee'],
            step=1.0,
            key="left_knee",
            label_visibility="collapsed"
        )
    
    with right_col:
        st.markdown("右侧关节")
        
        # 右肩
        shoulder_title_cols = st.columns([3, 1])
        with shoulder_title_cols[0]:
            st.markdown("右肩")
        with shoulder_title_cols[1]:
            with st.popover("❓", help="点击查看右肩解剖图"):
                st.markdown("右肩解剖")
                img_b64 = load_anatomy_image("right_shoulder")
                if img_b64:
                    st.image(f"data:image/png;base64,{img_b64}", 
                            caption="右肩解剖图", 
                            use_container_width=True)
                else:
                    st.info("请将右肩解剖图放入anatomy_images文件夹")
                st.markdown(get_joint_description("right_shoulder"))
        
        r_shoulder_cols = st.columns(3)
        for j in range(3):
            with r_shoulder_cols[j]:
                angle_names = ["屈/伸", "外展/内收", "旋转"]
                st.session_state.joint_data['right_shoulder'][j] = st.number_input(
                    label=angle_names[j],
                    min_value=-180.0,
                    max_value=180.0,
                    value=st.session_state.joint_data['right_shoulder'][j],
                    step=1.0,
                    key=f"right_shoulder_{j}",
                    label_visibility="collapsed"
                )
        
        # 右肘
        elbow_title_cols = st.columns([3, 1])
        with elbow_title_cols[0]:
            st.markdown("右肘")
        with elbow_title_cols[1]:
            with st.popover("❓", help="点击查看右肘解剖图"):
                st.markdown("右肘解剖")
                img_b64 = load_anatomy_image("right_elbow")
                if img_b64:
                    st.image(f"data:image/png;base64,{img_b64}", 
                            caption="右肘解剖图", 
                            use_container_width=True)
                else:
                    st.info("请将右肘解剖图放入anatomy_images文件夹")
                st.markdown(get_joint_description("right_elbow"))
        
        st.session_state.joint_data['right_elbow'] = st.number_input(
            label="屈曲角度",
            min_value=-180.0,
            max_value=180.0,
            value=st.session_state.joint_data['right_elbow'],
            step=1.0,
            key="right_elbow",
            label_visibility="collapsed"
        )
        
        # 右髋
        hip_title_cols = st.columns([3, 1])
        with hip_title_cols[0]:
            st.markdown("右髋")
        with hip_title_cols[1]:
            with st.popover("❓", help="点击查看右髋解剖图"):
                st.markdown("右髋解剖")
                img_b64 = load_anatomy_image("right_hip")
                if img_b64:
                    st.image(f"data:image/png;base64,{img_b64}", 
                            caption="右髋解剖图", 
                            use_container_width=True)
                else:
                    st.info("请将右髋解剖图放入anatomy_images文件夹")
                st.markdown(get_joint_description("right_hip"))
        
        r_hip_cols = st.columns(3)
        for j in range(3):
            with r_hip_cols[j]:
                angle_names = ["屈/伸", "外展/内收", "旋转"]
                st.session_state.joint_data['right_hip'][j] = st.number_input(
                    label=angle_names[j],
                    min_value=-180.0,
                    max_value=180.0,
                    value=st.session_state.joint_data['right_hip'][j],
                    step=1.0,
                    key=f"right_hip_{j}",
                    label_visibility="collapsed"
                )
        
        # 右膝
        knee_title_cols = st.columns([3, 1])
        with knee_title_cols[0]:
            st.markdown("右膝")
        with knee_title_cols[1]:
            with st.popover("❓", help="点击查看右膝解剖图"):
                st.markdown("右膝解剖")
                img_b64 = load_anatomy_image("right_knee")
                if img_b64:
                    st.image(f"data:image/png;base64,{img_b64}", 
                            caption="右膝解剖图", 
                            use_container_width=True)
                else:
                    st.info("请将右膝解剖图放入anatomy_images文件夹")
                st.markdown(get_joint_description("right_knee"))
        
        st.session_state.joint_data['right_knee'] = st.number_input(
            label="屈曲角度",
            min_value=-180.0,
            max_value=180.0,
            value=st.session_state.joint_data['right_knee'],
            step=1.0,
            key="right_knee",
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    # 操作控制
    st.subheader("操作控制")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        preview_btn = st.button("🔍 预览", use_container_width=True, type="primary")
    with btn_col2:
        save_btn = st.button("💾 保存", use_container_width=True)
    with btn_col3:
        reset_btn = st.button("🔄 重置", use_container_width=True)
    
    if st.button("📂 加载示例数据", use_container_width=True):
        example_spine = [5 * i for i in range(25)]
        example_joints = {
            'left_shoulder': [30, 20, 10],
            'left_elbow': 45,
            'left_hip': [15, 5, 0],
            'left_knee': 30,
            'right_shoulder': [-30, 20, -10],
            'right_elbow': -45,
            'right_hip': [-15, 5, 0],
            'right_knee': -30
        }
        st.session_state.spine_values = example_spine
        st.session_state.joint_data = example_joints
        st.success("示例数据已加载！")
        st.rerun()

# =============== 使用指南 (位于底部) ===============
st.markdown("---")

st.markdown("## 📋 使用指南")

guide_col1, guide_col2, guide_col3 = st.columns(3)

with guide_col1:
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #4e73df; height: 100%;">
        <h5 style="color: #4e73df; margin-top: 0;">1. 输入数据</h5>
        <p>在左侧边栏输入25个脊柱角度和8个关节角度。</p>
    </div>
    """, unsafe_allow_html=True)

with guide_col2:
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1cc88a;">
        <h5 style="color: #1cc88a; margin-top: 0;">2. 预览模型</h5>
        <p>点击视图按钮切换5个不同视角查看3D模型。</p>
    </div>
    """, unsafe_allow_html=True)

with guide_col3:
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #f6c23e;">
        <h5 style="color: #f6c23e; margin-top: 0;">3. 保存与导出</h5>
        <p>点击保存按钮可将当前角度数据下载为CSV文件。</p>
    </div>
    """, unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.caption("© 2026 人体数字模型前处理定位平台 | 生物力学研究工具")

# =============== 保存功能 ===============
if save_btn:
    st.success("✅ 数据保存成功！")
    
    # 创建CSV数据
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['脊柱节段', '角度(°)'])
    for i, angle in enumerate(st.session_state.spine_values):
        writer.writerow([spine_labels[i], angle])
    
    writer.writerow([])
    writer.writerow(['关节', '角度1', '角度2', '角度3'])
    for joint_name, angles in st.session_state.joint_data.items():
        if isinstance(angles, list):
            writer.writerow([joint_name, angles[0], angles[1], angles[2]])
        else:
            writer.writerow([joint_name, angles, "", ""])
    
    csv_data = output.getvalue()
    
    st.download_button(
        label="📥 下载CSV文件",
        data=csv_data,
        file_name="关节角度数据.csv",
        mime="text/csv"
    )

# =============== 重置功能 ===============
if reset_btn:
    reset_all_inputs()
    st.success("🔄 所有输入已重置")
    st.rerun()