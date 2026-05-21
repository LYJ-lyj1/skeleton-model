import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import base64
import os
from io import BytesIO
from PIL import Image  # 新增

#=============== 页面配置 ===========
st.set_page_config(
    page_title="人体数字模型前处理定位平台",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

#============= 导入自定义模块 ===========
try:
    from skeleton_model import SkeletonModel3D
    from data_processor import DataProcessor
except ImportError as e:
    st.error(f"⚠️ 模块导入错误: {e}")
    st.info("请确保 skeleton_model.py 和 data_processor.py 在同一目录下")

#== 初始化函数 =============
@st.cache_resource
def get_skeleton_model():
    return SkeletonModel3D()

@st.cache_resource
def get_data_processor():
    return DataProcessor()

# 创建实例
skeleton_model = get_skeleton_model()
data_processor = get_data_processor()

#=== 辅助函数 ============
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

def load_anatomy_image(joint_name):
    """从 anatomy_images 文件夹加载解剖图片并转换为base64格式"""
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
            os.path.join("static", filename),
        ]
        for filepath in paths_to_try:
            if os.path.exists(filepath):
                try:
                    with open(filepath, "rb") as f:
                        return base64.b64encode(f.read()).decode()
                except Exception as e:
                    st.warning(f"加载图片失败 {filepath}: {e}")
        return None
    st.warning(f"图片文件未找到: {filename}")
    return None

def load_real_model_image(image_index=1):
    """从 real_human_model_images 文件夹加载3D建模图 (Human_Pose_001.png 到 005.png)"""
    if 1 <= image_index <= 5:
        filename = f"Human_Pose_{image_index:03d}.png"  # 格式化: 001, 002, ...
    else:
        filename = "Human_Pose_001.png"  # 默认
    
    # 检查多个可能的路径
    paths_to_try = [
        os.path.join("real_human_model_images", filename),  # 主要路径
        filename,  # 根目录
    ]
    
    for filepath in paths_to_try:
        if os.path.exists(filepath):
            try:
                with open(filepath, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception as e:
                st.warning(f"加载3D建模图失败 {filepath}: {e}")
    
    # 如果找不到图片
    st.warning(f"未找到3D建模图: {filename}")
    return None

def get_joint_description(joint_name):
    """获取关节的解剖学描述"""
    descriptions = {
        "left_shoulder": """
**左肩关节解剖:**
- 类型: 球窝关节
- 构成: 肱骨头 + 肩胛骨关节盂
- 运动: 屈/伸, 外展/内收, 旋转
- 特点: 人体最灵活的关节
**关键结构:**
1. 肱骨(上臂骨)
2. 肩胛骨(肩胛骨)
3. 锁骨(锁骨)
4. 关节囊
5. 肩袖肌群
""",
        "right_shoulder": """
**右肩关节解剖:**
- 类型: 球窝关节
- 构成: 肱骨头 + 肩胛骨关节盂
- 运动: 屈/伸, 外展/内收, 旋转
- 特点: 人体最灵活的关节
""",
        "left_elbow": """
**左肘关节解剖:**
- 类型: 铰链关节
- 构成: 肱骨远端 + 尺骨鹰嘴 + 桡骨头
- 运动: 主要为屈/伸
- 特点: 高稳定性, 活动范围有限
""",
        "right_elbow": """
**右肘关节解剖:**
- 类型: 铰链关节
- 构成: 肱骨远端 + 尺骨鹰嘴 + 桡骨头
- 运动: 主要为屈/伸
""",
        "left_hip": """
**左髋关节解剖:**
- 类型: 球窝关节
- 构成: 股骨头 + 髋臼
- 运动: 多方向运动
- 特点: 承重关节, 高稳定性
""",
        "right_hip": """
**右髋关节解剖:**
- 类型: 球窝关节
- 构成: 股骨头 + 髋臼
- 运动: 多方向运动
""",
        "left_knee": """
**左膝关节解剖:**
- 类型: 复杂关节
- 构成: 股骨, 胫骨, 髌骨
- 运动: 主要为屈/伸
- 特点: 人体最大且最复杂的关节
""",
        "right_knee": """
**右膝关节解剖:**
- 类型: 复杂关节
- 构成: 股骨, 胫骨, 髌骨
- 运动: 主要为屈/伸
""",
    }
    return descriptions.get(joint_name, "关节解剖示意图")

#============== 会话状态初始化 =================
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
if 'multi_view' not in st.session_state:
    st.session_state.multi_view = False
if 'current_real_model_image' not in st.session_state:  # 新增：当前显示的3D模型图片索引
    st.session_state.current_real_model_image = 1
if 'show_real_model' not in st.session_state:  # 控制是否显示3D模型
    st.session_state.show_real_model = True

#============== 页面标题 ============
st.title("人体数字模型前处理定位平台 / Human Body Model Positioning Toolbox")
st.markdown("---")

#============= 侧边栏: 数据输入 ===============
st.sidebar.header("数据输入面板")

# 1. 脊柱角度输入
st.sidebar.subheader("脊柱角度(25个椎骨)")
st.sidebar.caption("C1-C7: 颈椎 | T1-T12: 胸椎 | L1-L5: 腰椎 | S1: 骶骨")

# 创建脊柱标签
spine_labels = [f"C{i+1}" for i in range(7)] + [f"T{i+1}" for i in range(12)] + [f"L{i+1}" for i in range(5)] + ["S1"]

# 在5列中显示25个脊柱输入框
spine_cols = st.sidebar.columns(5)
spine_values = []
for i in range(25):
    with spine_cols[i % 5]:
        value = st.number_input(
            label=spine_labels[i],
            min_value=-180.0,
            max_value=180.0,
            value=st.session_state.spine_values[i],
            step=1.0,
            key=f"spine_input_{i}"
        )
        spine_values.append(value)
        st.session_state.spine_values[i] = value

st.sidebar.markdown("---")

# 2. 关节角度输入
st.sidebar.subheader("关节角度")

# 创建左右列布局
left_col, right_col = st.sidebar.columns(2)

#============= 左侧关节 =============
with left_col:
    st.markdown("**左侧关节**")
    
    # 左肩
    shoulder_row1, shoulder_row2 = st.columns([3, 1])
    with shoulder_row1:
        st.markdown("##### 左肩")
    with shoulder_row2:
        with st.popover("?", help="点击查看左肩解剖图"):
            st.markdown("**左肩关节解剖**")
            img_b64 = load_anatomy_image("left_shoulder")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}",
                         caption="左肩关节解剖",
                         width=300)
            else:
                st.info("左肩关节解剖图占位符")
            st.markdown(get_joint_description("left_shoulder"))
    
    # 左肩3个角度
    l_shoulder_cols = st.columns(3)
    l_shoulder_values = []
    for j in range(3):
        with l_shoulder_cols[j]:
            angle_names = ["屈/伸", "外展/内收", "旋转"]
            value = st.number_input(
                label=angle_names[j],
                min_value=-180.0,
                max_value=180.0,
                value=st.session_state.joint_data['left_shoulder'][j],
                step=1.0,
                key=f"left_shoulder_{j}"
            )
            l_shoulder_values.append(value)
    st.session_state.joint_data['left_shoulder'] = l_shoulder_values

    # 左肘
    elbow_row1, elbow_row2 = st.columns([3, 1])
    with elbow_row1:
        st.markdown("##### 左肘")
    with elbow_row2:
        with st.popover("?", help="点击查看左肘解剖图"):
            st.markdown("**左肘关节解剖**")
            img_b64 = load_anatomy_image("left_elbow")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}",
                         caption="左肘关节解剖",
                         width=300)
            else:
                st.info("左肘关节解剖图占位符")
            st.markdown(get_joint_description("left_elbow"))
    
    l_elbow_value = st.number_input(
        label="屈曲角度",
        min_value=-180.0,
        max_value=180.0,
        value=st.session_state.joint_data['left_elbow'],
        step=1.0,
        key="left_elbow"
    )
    st.session_state.joint_data['left_elbow'] = l_elbow_value

    # 左髋
    hip_row1, hip_row2 = st.columns([3, 1])
    with hip_row1:
        st.markdown("##### 左髋")
    with hip_row2:
        with st.popover("?", help="点击查看左髋解剖图"):
            st.markdown("**左髋关节解剖**")
            img_b64 = load_anatomy_image("left_hip")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}",
                         caption="左髋关节解剖",
                         width=300)
            else:
                st.info("左髋关节解剖图占位符")
            st.markdown(get_joint_description("left_hip"))
    
    l_hip_cols = st.columns(3)
    l_hip_values = []
    for j in range(3):
        with l_hip_cols[j]:
            angle_names = ["屈/伸", "外展/内收", "旋转"]
            value = st.number_input(
                label=angle_names[j],
                min_value=-180.0,
                max_value=180.0,
                value=st.session_state.joint_data['left_hip'][j],
                step=1.0,
                key=f"left_hip_{j}"
            )
            l_hip_values.append(value)
    st.session_state.joint_data['left_hip'] = l_hip_values

    # 左膝
    knee_row1, knee_row2 = st.columns([3, 1])
    with knee_row1:
        st.markdown("##### 左膝")
    with knee_row2:
        with st.popover("?", help="点击查看左膝解剖图"):
            st.markdown("**左膝关节解剖**")
            img_b64 = load_anatomy_image("left_knee")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}",
                         caption="左膝关节解剖",
                         width=300)
            else:
                st.info("左膝关节解剖图占位符")
            st.markdown(get_joint_description("left_knee"))
    
    l_knee_value = st.number_input(
        label="屈曲角度",
        min_value=-180.0,
        max_value=180.0,
        value=st.session_state.joint_data['left_knee'],
        step=1.0,
        key="left_knee"
    )
    st.session_state.joint_data['left_knee'] = l_knee_value

#============= 右侧关节 ==============
with right_col:
    st.markdown("**右侧关节**")
    
    # 右肩
    shoulder_row1, shoulder_row2 = st.columns([3, 1])
    with shoulder_row1:
        st.markdown("##### 右肩")
    with shoulder_row2:
        with st.popover("?", help="点击查看右肩解剖图"):
            st.markdown("**右肩关节解剖**")
            img_b64 = load_anatomy_image("right_shoulder")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}",
                         caption="右肩关节解剖",
                         width=300)
            else:
                st.info("右肩关节解剖图占位符")
            st.markdown(get_joint_description("right_shoulder"))
    
    # 右肩3个角度
    r_shoulder_cols = st.columns(3)
    r_shoulder_values = []
    for j in range(3):
        with r_shoulder_cols[j]:
            angle_names = ["屈/伸", "外展/内收", "旋转"]
            value = st.number_input(
                label=angle_names[j],
                min_value=-180.0,
                max_value=180.0,
                value=st.session_state.joint_data['right_shoulder'][j],
                step=1.0,
                key=f"right_shoulder_{j}"
            )
            r_shoulder_values.append(value)
    st.session_state.joint_data['right_shoulder'] = r_shoulder_values

    # 右肘
    elbow_row1, elbow_row2 = st.columns([3, 1])
    with elbow_row1:
        st.markdown("##### 右肘")
    with elbow_row2:
        with st.popover("?", help="点击查看右肘解剖图"):
            st.markdown("**右肘关节解剖**")
            img_b64 = load_anatomy_image("right_elbow")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}",
                         caption="右肘关节解剖",
                         width=300)
            else:
                st.info("右肘关节解剖图占位符")
            st.markdown(get_joint_description("right_elbow"))
    
    r_elbow_value = st.number_input(
        label="屈曲角度",
        min_value=-180.0,
        max_value=180.0,
        value=st.session_state.joint_data['right_elbow'],
        step=1.0,
        key="right_elbow"
    )
    st.session_state.joint_data['right_elbow'] = r_elbow_value

    # 右髋
    hip_row1, hip_row2 = st.columns([3, 1])
    with hip_row1:
        st.markdown("##### 右髋")
    with hip_row2:
        with st.popover("?", help="点击查看右髋解剖图"):
            st.markdown("**右髋关节解剖**")
            img_b64 = load_anatomy_image("right_hip")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}",
                         caption="右髋关节解剖",
                         width=300)
            else:
                st.info("右髋关节解剖图占位符")
            st.markdown(get_joint_description("right_hip"))
    
    r_hip_cols = st.columns(3)
    r_hip_values = []
    for j in range(3):
        with r_hip_cols[j]:
            angle_names = ["屈/伸", "外展/内收", "旋转"]
            value = st.number_input(
                label=angle_names[j],
                min_value=-180.0,
                max_value=180.0,
                value=st.session_state.joint_data['right_hip'][j],
                step=1.0,
                key=f"right_hip_{j}"
            )
            r_hip_values.append(value)
    st.session_state.joint_data['right_hip'] = r_hip_values

    # 右膝
    knee_row1, knee_row2 = st.columns([3, 1])
    with knee_row1:
        st.markdown("##### 右膝")
    with knee_row2:
        with st.popover("?", help="点击查看右膝解剖图"):
            st.markdown("**右膝关节解剖**")
            img_b64 = load_anatomy_image("right_knee")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}",
                         caption="右膝关节解剖",
                         width=300)
            else:
                st.info("右膝关节解剖图占位符")
            st.markdown(get_joint_description("right_knee"))
    
    r_knee_value = st.number_input(
        label="屈曲角度",
        min_value=-180.0,
        max_value=180.0,
        value=st.session_state.joint_data['right_knee'],
        step=1.0,
        key="right_knee"
    )
    st.session_state.joint_data['right_knee'] = r_knee_value

#================= 控制面板 ===================
st.sidebar.markdown("---")
st.sidebar.subheader("控制面板")

# Multi-view切换按钮
multi_view = st.sidebar.checkbox(
    "多视图模式 (Multi-view)", 
    value=st.session_state.multi_view,
    help="同时显示正面、侧面、俯视和3D视图"
)
st.session_state.multi_view = multi_view

# 3D模型显示控制
show_real_model = st.sidebar.checkbox(
    "显示3D人体模型图", 
    value=st.session_state.show_real_model,
    help="显示师兄提供的专业3D人体模型图片"
)
st.session_state.show_real_model = show_real_model

# 3D模型选择下拉菜单
if st.session_state.show_real_model:
    model_options = {
        1: "3D模型 001 (Human_Pose_001.png)",
        2: "3D模型 002 (Human_Pose_002.png)",
        3: "3D模型 003 (Human_Pose_003.png)",
        4: "3D模型 004 (Human_Pose_004.png)",
        5: "3D模型 005 (Human_Pose_005.png)",
    }
    
    selected_model = st.sidebar.selectbox(
        "选择3D模型视图",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=st.session_state.current_real_model_image-1
    )
    st.session_state.current_real_model_image = selected_model

# 控制按钮
btn_col1, btn_col2, btn_col3 = st.sidebar.columns(3)
with btn_col1:
    preview_btn = st.button("🔍 预览", use_container_width=True, type="primary")
with btn_col2:
    save_btn = st.button("💾 保存", use_container_width=True)
with btn_col3:
    reset_btn = st.button("🔄 重置", use_container_width=True)

# 加载示例数据按钮
if st.sidebar.button("📂 加载示例数据", use_container_width=True):
    # 创建示例数据
    example_spine = [5 * i for i in range(25)]  # 0,5,10,...,120
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
    st.sidebar.success("示例数据已加载！点击'预览'查看效果。")
    st.session_state.example_loaded = True
    st.session_state.example_spine = example_spine
    st.session_state.example_joints = example_joints

#============ 主显示区 ============
st.markdown("## Model Preview")

# 准备关节数据
joint_data = st.session_state.joint_data
if hasattr(st.session_state, 'example_loaded') and st.session_state.example_loaded:
    spine_values = st.session_state.example_spine
    joint_data = st.session_state.example_joints
else:
    spine_values = st.session_state.spine_values

# 创建可视化占位符
viz_placeholder = st.empty()
status_placeholder = st.empty()
summary_placeholder = st.empty()

# 预览功能
if preview_btn:
    with st.spinner("🔄 正在生成模型..."):
        # 验证数据
        spine_valid, spine_msg = data_processor.validate_spine_data(spine_values)
        if not spine_valid:
            st.error(f"❌ 脊柱数据错误: {spine_msg}")
        else:
            # 验证关节数据
            all_valid = True
            error_messages = []
            for joint_name, values in joint_data.items():
                valid, msg = data_processor.validate_joint_data(values, joint_name)
                if not valid:
                    error_messages.append(f"{joint_name}: {msg}")
                    all_valid = False
            
            if not all_valid:
                for error in error_messages:
                    st.error(f"❌ {error}")
            else:
                # 计算骨架位置
                joints = skeleton_model.calculate_from_angles(spine_values, joint_data)
                
                # 生成骨架可视化
                if st.session_state.multi_view:
                    fig = skeleton_model.plot_multi_view()
                else:
                    fig, ax = skeleton_model.plot_3d_skeleton()
                
                # 在占位符中显示
                with viz_placeholder.container():
                    if st.session_state.show_real_model:
                        # 显示两列布局：左侧3D模型，右侧骨架图
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 3D人体模型")
                            img_b64 = load_real_model_image(st.session_state.current_real_model_image)
                            if img_b64:
                                st.image(f"data:image/png;base64,{img_b64}",
                                         caption=f"专业3D人体模型 - 视图 {st.session_state.current_real_model_image}",
                                         use_column_width=True)
                            else:
                                st.warning(f"未找到3D模型图片: Human_Pose_{st.session_state.current_real_model_image:03d}.png")
                                st.info("请确保图片文件在 'real_human_model_images' 文件夹中")
                        
                        with col2:
                            st.markdown("### 骨骼框架预览")
                            st.pyplot(fig)
                            st.caption("基于当前角度生成的骨骼框架")
                    else:
                        # 只显示骨架图
                        st.pyplot(fig)
                        st.caption("基于当前角度生成的3D骨架模型")
                
                # 保存数据
                data_processor.save_data(spine_values, joint_data)
                
                # 显示成功消息
                status_placeholder.success("✅ 模型生成成功！")
                
                # 显示数据摘要
                with summary_placeholder.container():
                    st.subheader("📊 数据摘要")
                    st.info(data_processor.get_summary())
                
                # 可展开的数据视图
                with st.expander("查看详细数据"):
                    col1_data, col2_data = st.columns(2)
                    with col1_data:
                        st.write("**脊柱数据:**")
                        for i, (label, angle) in enumerate(zip(spine_labels, spine_values)):
                            st.write(f"{label}: {angle}°")
                    with col2_data:
                        st.write("**关节数据:**")
                        for joint_name, angles in joint_data.items():
                            if isinstance(angles, list):
                                st.write(f"{joint_name}: {angles[0]}°, {angles[1]}°, {angles[2]}°")
                            else:
                                st.write(f"{joint_name}: {angles}°")
else:
    # 初始状态显示提示
    with viz_placeholder.container():
        if st.session_state.show_real_model:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 3D人体模型")
                img_b64 = load_real_model_image(st.session_state.current_real_model_image)
                if img_b64:
                    st.image(f"data:image/png;base64,{img_b64}",
                             caption=f"专业3D人体模型 - 视图 {st.session_state.current_real_model_image}",
                             use_column_width=True)
                else:
                    st.warning(f"未找到3D模型图片: Human_Pose_{st.session_state.current_real_model_image:03d}.png")
                    st.info("""
                    **如何正确显示3D模型:**
                    1. 确保图片文件在 'real_human_model_images' 文件夹中
                    2. 确保图片命名为: Human_Pose_001.png 到 Human_Pose_005.png
                    3. 图片文件应为PNG格式
                    """)
            
            with col2:
                st.markdown("### 骨骼框架预览")
                st.info("👆 点击左侧的 **预览** 按钮生成3D骨架模型")
                st.caption("此处将显示基于输入角度生成的骨骼框架")
        else:
            st.info("👆 点击左侧的 **预览** 按钮生成3D骨架模型")

# 保存功能
if save_btn:
    spine_valid, spine_msg = data_processor.validate_spine_data(spine_values)
    if spine_valid:
        all_valid = True
        for joint_name, values in joint_data.items():
            valid, msg = data_processor.validate_joint_data(values, joint_name)
            if not valid:
                all_valid = False
                break
        
        if all_valid:
            if data_processor.save_data(spine_values, joint_data):
                st.success("✅ 数据保存成功！")
                
                # 提供下载
                import csv
                from io import StringIO
                
                output = StringIO()
                writer = csv.writer(output)
                
                # 写入脊柱数据
                writer.writerow(['脊柱节段', '角度(°)'])
                for i, angle in enumerate(spine_values):
                    writer.writerow([spine_labels[i], angle])
                
                writer.writerow([])
                writer.writerow(['关节', '角度1', '角度2', '角度3'])
                for joint_name, angles in joint_data.items():
                    if isinstance(angles, list):
                        writer.writerow([joint_name, angles[0], angles[1], angles[2]])
                    else:
                        writer.writerow([joint_name, angles, "", ""])
                
                csv_data = output.getvalue()
                
                st.download_button(
                    label="下载为CSV",
                    data=csv_data,
                    file_name="关节角度数据.csv",
                    mime="text/csv"
                )
            else:
                st.error("❌ 数据保存失败")
    else:
        st.error(f"❌ {spine_msg}")

# 重置功能
if reset_btn:
    reset_all_inputs()
    st.success("🔄 所有输入字段已重置为0")
    st.rerun()

#========== 页面底部 =============
st.markdown("---")
st.markdown("### 📋 使用指南")
col1_guide, col2_guide, col3_guide = st.columns(3)
with col1_guide:
    st.markdown("""
    **1. 输入数据**
    - 在侧边栏输入25个脊柱角度
    - 输入8个关节角度
    - 点击?查看解剖图
    """)
with col2_guide:
    st.markdown("""
    **2. 生成模型**
    - 点击**预览**生成3D骨架
    - 可选择显示3D人体模型
    - 数据摘要显示在下方
    """)
with col3_guide:
    st.markdown("""
    **3. 保存与导出**
    - 点击**保存**存储数据
    - 下载为CSV文件
    - 点击**重置**清除数据
    """)

# 页脚
st.markdown("---")
st.caption("© 2026 人体数字模型前处理定位平台 | 版本 2.0 | 生物力学研究工具")