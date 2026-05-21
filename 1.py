import streamlit as st
import base64
import os
import pandas as pd
from io import StringIO
import csv

#=============== 页面配置 ===========
st.set_page_config(
    page_title="人体数字模型定位平台",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 移除所有与skeleton_model和Matplotlib相关的导入
# 只保留必要的功能

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

def load_real_model_image(image_index=1):
    """从 real_human_model_images 文件夹加载3D建模图"""
    if 1 <= image_index <= 5:
        filename = f"Human_Pose_{image_index:03d}.png"
    else:
        filename = "Human_Pose_001.png"
    
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
if 'current_real_model_image' not in st.session_state:
    st.session_state.current_real_model_image = 1

#============== 页面标题 ============
st.title("人体数字模型前处理定位平台（HBM positioning）")
st.markdown("---")

#============= 侧边栏: 数据输入 ===============
st.sidebar.header("数据输入面板")

# 1. 脊柱角度输入
st.sidebar.subheader("脊柱角度(25个椎骨)")
spine_labels = [f"C{i+1}" for i in range(7)] + [f"T{i+1}" for i in range(12)] + [f"L{i+1}" for i in range(5)] + ["S1"]

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
left_col, right_col = st.sidebar.columns(2)

# 左侧关节
with left_col:
    st.markdown("**左侧关节**")
    
    # 左肩
    st.markdown("##### 左肩")
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
    st.markdown("##### 左肘")
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
    st.markdown("##### 左髋")
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
    st.markdown("##### 左膝")
    l_knee_value = st.number_input(
        label="屈曲角度",
        min_value=-180.0,
        max_value=180.0,
        value=st.session_state.joint_data['left_knee'],
        step=1.0,
        key="left_knee"
    )
    st.session_state.joint_data['left_knee'] = l_knee_value

# 右侧关节
with right_col:
    st.markdown("**右侧关节**")
    
    # 右肩
    st.markdown("##### 右肩")
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
    st.markdown("##### 右肘")
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
    st.markdown("##### 右髋")
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
    st.markdown("##### 右膝")
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
st.sidebar.subheader("3D模型控制")

# 3D模型选择
st.sidebar.markdown("选择模型姿态:")
col1, col2, col3, col4, col5 = st.sidebar.columns(5)
with col1:
    if st.button("1", use_container_width=True):
        st.session_state.current_real_model_image = 1
with col2:
    if st.button("2", use_container_width=True):
        st.session_state.current_real_model_image = 2
with col3:
    if st.button("3", use_container_width=True):
        st.session_state.current_real_model_image = 3
with col4:
    if st.button("4", use_container_width=True):
        st.session_state.current_real_model_image = 4
with col5:
    if st.button("5", use_container_width=True):
        st.session_state.current_real_model_image = 5

st.sidebar.caption(f"当前选择: Human_Pose_{st.session_state.current_real_model_image:03d}")

# 控制按钮
st.sidebar.markdown("---")
st.sidebar.subheader("操作控制")

btn_col1, btn_col2, btn_col3 = st.sidebar.columns(3)
with btn_col1:
    preview_btn = st.button("🔍 预览", use_container_width=True, type="primary")
with btn_col2:
    save_btn = st.button("💾 保存", use_container_width=True)
with btn_col3:
    reset_btn = st.button("🔄 重置", use_container_width=True)

# 加载示例数据
if st.sidebar.button("📂 加载示例数据", use_container_width=True):
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
    st.sidebar.success("示例数据已加载！")
    st.session_state.example_loaded = True
    st.session_state.example_spine = example_spine
    st.session_state.example_joints = example_joints

#============ 主显示区 ============
st.markdown("## 🎯 3D人体模型预览")

# 准备数据
joint_data = st.session_state.joint_data
if hasattr(st.session_state, 'example_loaded') and st.session_state.example_loaded:
    spine_values = st.session_state.example_spine
    joint_data = st.session_state.example_joints
else:
    spine_values = st.session_state.spine_values

# 预览功能
if preview_btn or True:  # 默认显示
    with st.spinner("正在加载3D模型..."):
        st.markdown(f"### 当前姿态: Human_Pose_{st.session_state.current_real_model_image:03d}")
        
        img_b64 = load_real_model_image(st.session_state.current_real_model_image)
        if img_b64:
            # 居中显示大图
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.image(f"data:image/png;base64,{img_b64}",
                         caption=f"专业3D人体模型 - 姿态 {st.session_state.current_real_model_image}",
                         use_container_width=True)
            
            # 显示5个小图供选择
            st.markdown("---")
            st.markdown("### 所有可用姿态")
            cols = st.columns(5)
            for i, col in enumerate(cols, 1):
                with col:
                    small_img = load_real_model_image(i)
                    if small_img:
                        st.image(f"data:image/png;base64,{small_img}",
                                 caption=f"姿态 {i}",
                                 use_container_width=True)
                        if st.button(f"选择姿态 {i}", key=f"select_{i}", use_container_width=True):
                            st.session_state.current_real_model_image = i
                            st.rerun()
        else:
            st.error("⚠️ 未找到3D模型图片")
            st.info("""
            请确保：
            1. 创建 'real_human_model_images' 文件夹
            2. 将师兄提供的图片放入文件夹
            3. 图片命名为: Human_Pose_001.png 到 Human_Pose_005.png
            """)
        
        # 显示数据摘要
        st.markdown("---")
        st.subheader("📊 当前角度设置")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**脊柱角度:**")
            for i, (label, angle) in enumerate(zip(spine_labels, spine_values)):
                st.write(f"{label}: {angle}°")
        
        with col2:
            st.markdown("**关节角度:**")
            for joint_name, angles in joint_data.items():
                if isinstance(angles, list):
                    st.write(f"{joint_name}: {angles[0]}°, {angles[1]}°, {angles[2]}°")
                else:
                    st.write(f"{joint_name}: {angles}°")

# 保存功能
if save_btn:
    st.success("✅ 数据保存成功！")
    
    # 创建CSV数据
    output = StringIO()
    writer = csv.writer(output)
    
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
        label="📥 下载CSV数据",
        data=csv_data,
        file_name="关节角度数据.csv",
        mime="text/csv"
    )

# 重置功能
if reset_btn:
    reset_all_inputs()
    st.success("🔄 所有输入已重置")
    st.rerun()

#========== 页面底部 =============
st.markdown("---")
st.markdown("### 📋 使用指南")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **1. 输入数据**
    - 侧边栏输入角度
    - 脊柱25个节段
    - 8个主要关节
    """)
with col2:
    st.markdown("""
    **2. 预览模型**
    - 点击**预览**显示
    - 选择不同姿态
    - 查看数据摘要
    """)
with col3:
    st.markdown("""
    **3. 保存与导出**
    - 点击**保存**存储
    - 下载CSV文件
    - 点击**重置**清除
    """)

st.markdown("---")
st.caption("© 2026 人体数字模型定位平台 | 版本 3.0")