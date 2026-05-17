"""
3D Human Skeleton Visualization System
Main Application with Anatomy Images
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import base64
import os
from io import BytesIO

# ============ Page Configuration ============
st.set_page_config(
    page_title="3D Skeleton Visualizer",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ Import Custom Modules ============
try:
    from skeleton_model import SkeletonModel3D
    from data_processor import DataProcessor
except ImportError as e:
    st.error(f"❌ Module Import Error: {e}")
    st.info("Please ensure skeleton_model.py and data_processor.py are in the same directory")

# ============ Initialization Functions ============
@st.cache_resource
def get_skeleton_model():
    return SkeletonModel3D()

@st.cache_resource
def get_data_processor():
    return DataProcessor()

# Create instances
skeleton_model = get_skeleton_model()
data_processor = get_data_processor()

# ============ Helper Functions ============
def reset_all_inputs():
    """Reset all input fields"""
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
    """Load anatomy image and convert to base64 format"""
    # Image mapping - using PNG format
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
        # Check anatomy_images directory
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
                    st.warning(f"Failed to load image {filepath}: {e}")
                    return None
        
        # If image doesn't exist, show placeholder
        st.warning(f"Image file not found: {filename}")
    
    return None

def get_joint_description(joint_name):
    """Get anatomical description of joint"""
    descriptions = {
        "left_shoulder": """
        **Left Shoulder Anatomy:**
        - Type: Ball-and-socket joint
        - Components: Humeral head + glenoid cavity of scapula
        - Movements: Flexion/Extension, Abduction/Adduction, Rotation
        - Features: Most mobile joint in the human body
        
        **Key Structures:**
        1. Humerus (upper arm bone)
        2. Scapula (shoulder blade)
        3. Clavicle (collarbone)
        4. Joint capsule
        5. Rotator cuff muscles
        """,
        "right_shoulder": """
        **Right Shoulder Anatomy:**
        - Type: Ball-and-socket joint
        - Components: Humeral head + glenoid cavity of scapula
        - Movements: Flexion/Extension, Abduction/Adduction, Rotation
        - Features: Most mobile joint in the human body
        """,
        "left_elbow": """
        **Left Elbow Anatomy:**
        - Type: Hinge joint
        - Components: Distal humerus + olecranon of ulna + radial head
        - Movements: Primarily flexion/extension
        - Features: High stability, limited range of motion
        """,
        "right_elbow": """
        **Right Elbow Anatomy:**
        - Type: Hinge joint
        - Components: Distal humerus + olecranon of ulna + radial head
        - Movements: Primarily flexion/extension
        """,
        "left_hip": """
        **Left Hip Anatomy:**
        - Type: Ball-and-socket joint
        - Components: Femoral head + acetabulum
        - Movements: Multi-directional movement
        - Features: Weight-bearing joint, high stability
        """,
        "right_hip": """
        **Right Hip Anatomy:**
        - Type: Ball-and-socket joint
        - Components: Femoral head + acetabulum
        - Movements: Multi-directional movement
        """,
        "left_knee": """
        **Left Knee Anatomy:**
        - Type: Complex joint
        - Components: Femur, tibia, patella
        - Movements: Primarily flexion/extension
        - Features: Largest and most complex joint in the body
        """,
        "right_knee": """
        **Right Knee Anatomy:**
        - Type: Complex joint
        - Components: Femur, tibia, patella
        - Movements: Primarily flexion/extension
        """
    }
    return descriptions.get(joint_name, "Joint Anatomy Diagram")

# ============ Session State Initialization ============
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

# ============ Page Title ============
st.title("🦴 3D Human Skeleton Joint Angle Visualization System")
st.markdown("---")

# ============ Sidebar: Data Input ============
st.sidebar.header("📊 Data Input Panel")

# 1. Spine Angle Input
st.sidebar.subheader("Spine Angles (25 Vertebrae)")
st.sidebar.caption("C1-C7: Cervical | T1-T12: Thoracic | L1-L5: Lumbar | S1: Sacrum")

# Create spine labels
spine_labels = [f"C{i+1}" for i in range(7)] + [f"T{i+1}" for i in range(12)] + [f"L{i+1}" for i in range(5)] + ["S1"]

# Display 25 spine input boxes in 5 columns
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

# 2. Joint Angle Input
st.sidebar.subheader("Joint Angles")

# Create left/right columns layout
left_col, right_col = st.sidebar.columns(2)

# ============ Left Side Joints ============
with left_col:
    st.markdown("**Left Side Joints**")
    
    # Left Shoulder
    shoulder_row1, shoulder_row2 = st.columns([3, 1])
    with shoulder_row1:
        st.markdown("##### Left Shoulder")
    with shoulder_row2:
        with st.popover("❓", help="Click to view left shoulder anatomy"):
            st.markdown("**Left Shoulder Anatomy**")
            img_b64 = load_anatomy_image("left_shoulder")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}", 
                        caption="Left Shoulder Anatomy", 
                        width=300)
            else:
                st.info("Placeholder for left shoulder anatomy image")
            st.markdown(get_joint_description("left_shoulder"))
    
    # Left shoulder 3 angles
    l_shoulder_cols = st.columns(3)
    l_shoulder_values = []
    for j in range(3):
        with l_shoulder_cols[j]:
            angle_names = ["Flex/Ext", "Abd/Add", "Rotation"]
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
    
    # Left Elbow
    elbow_row1, elbow_row2 = st.columns([3, 1])
    with elbow_row1:
        st.markdown("##### Left Elbow")
    with elbow_row2:
        with st.popover("❓", help="Click to view left elbow anatomy"):
            st.markdown("**Left Elbow Anatomy**")
            img_b64 = load_anatomy_image("left_elbow")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}", 
                        caption="Left Elbow Anatomy", 
                        width=300)
            else:
                st.info("Placeholder for left elbow anatomy image")
            st.markdown(get_joint_description("left_elbow"))
    
    l_elbow_value = st.number_input(
        label="Flexion Angle",
        min_value=-180.0,
        max_value=180.0,
        value=st.session_state.joint_data['left_elbow'],
        step=1.0,
        key="left_elbow"
    )
    st.session_state.joint_data['left_elbow'] = l_elbow_value
    
    # Left Hip
    hip_row1, hip_row2 = st.columns([3, 1])
    with hip_row1:
        st.markdown("##### Left Hip")
    with hip_row2:
        with st.popover("❓", help="Click to view left hip anatomy"):
            st.markdown("**Left Hip Anatomy**")
            img_b64 = load_anatomy_image("left_hip")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}", 
                        caption="Left Hip Anatomy", 
                        width=300)
            else:
                st.info("Placeholder for left hip anatomy image")
            st.markdown(get_joint_description("left_hip"))
    
    l_hip_cols = st.columns(3)
    l_hip_values = []
    for j in range(3):
        with l_hip_cols[j]:
            angle_names = ["Flex/Ext", "Abd/Add", "Rotation"]
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
    
    # Left Knee
    knee_row1, knee_row2 = st.columns([3, 1])
    with knee_row1:
        st.markdown("##### Left Knee")
    with knee_row2:
        with st.popover("❓", help="Click to view left knee anatomy"):
            st.markdown("**Left Knee Anatomy**")
            img_b64 = load_anatomy_image("left_knee")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}", 
                        caption="Left Knee Anatomy", 
                        width=300)
            else:
                st.info("Placeholder for left knee anatomy image")
            st.markdown(get_joint_description("left_knee"))
    
    l_knee_value = st.number_input(
        label="Flexion Angle",
        min_value=-180.0,
        max_value=180.0,
        value=st.session_state.joint_data['left_knee'],
        step=1.0,
        key="left_knee"
    )
    st.session_state.joint_data['left_knee'] = l_knee_value

# ============ Right Side Joints ============
with right_col:
    st.markdown("**Right Side Joints**")
    
    # Right Shoulder
    shoulder_row1, shoulder_row2 = st.columns([3, 1])
    with shoulder_row1:
        st.markdown("##### Right Shoulder")
    with shoulder_row2:
        with st.popover("❓", help="Click to view right shoulder anatomy"):
            st.markdown("**Right Shoulder Anatomy**")
            img_b64 = load_anatomy_image("right_shoulder")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}", 
                        caption="Right Shoulder Anatomy", 
                        width=300)
            else:
                st.info("Placeholder for right shoulder anatomy image")
            st.markdown(get_joint_description("right_shoulder"))
    
    r_shoulder_cols = st.columns(3)
    r_shoulder_values = []
    for j in range(3):
        with r_shoulder_cols[j]:
            angle_names = ["Flex/Ext", "Abd/Add", "Rotation"]
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
    
    # Right Elbow
    elbow_row1, elbow_row2 = st.columns([3, 1])
    with elbow_row1:
        st.markdown("##### Right Elbow")
    with elbow_row2:
        with st.popover("❓", help="Click to view right elbow anatomy"):
            st.markdown("**Right Elbow Anatomy**")
            img_b64 = load_anatomy_image("right_elbow")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}", 
                        caption="Right Elbow Anatomy", 
                        width=300)
            else:
                st.info("Placeholder for right elbow anatomy image")
            st.markdown(get_joint_description("right_elbow"))
    
    r_elbow_value = st.number_input(
        label="Flexion Angle",
        min_value=-180.0,
        max_value=180.0,
        value=st.session_state.joint_data['right_elbow'],
        step=1.0,
        key="right_elbow"
    )
    st.session_state.joint_data['right_elbow'] = r_elbow_value
    
    # Right Hip
    hip_row1, hip_row2 = st.columns([3, 1])
    with hip_row1:
        st.markdown("##### Right Hip")
    with hip_row2:
        with st.popover("❓", help="Click to view right hip anatomy"):
            st.markdown("**Right Hip Anatomy**")
            img_b64 = load_anatomy_image("right_hip")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}", 
                        caption="Right Hip Anatomy", 
                        width=300)
            else:
                st.info("Placeholder for right hip anatomy image")
            st.markdown(get_joint_description("right_hip"))
    
    r_hip_cols = st.columns(3)
    r_hip_values = []
    for j in range(3):
        with r_hip_cols[j]:
            angle_names = ["Flex/Ext", "Abd/Add", "Rotation"]
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
    
    # Right Knee
    knee_row1, knee_row2 = st.columns([3, 1])
    with knee_row1:
        st.markdown("##### Right Knee")
    with knee_row2:
        with st.popover("❓", help="Click to view right knee anatomy"):
            st.markdown("**Right Knee Anatomy**")
            img_b64 = load_anatomy_image("right_knee")
            if img_b64:
                st.image(f"data:image/png;base64,{img_b64}", 
                        caption="Right Knee Anatomy", 
                        width=300)
            else:
                st.info("Placeholder for right knee anatomy image")
            st.markdown(get_joint_description("right_knee"))
    
    r_knee_value = st.number_input(
        label="Flexion Angle",
        min_value=-180.0,
        max_value=180.0,
        value=st.session_state.joint_data['right_knee'],
        step=1.0,
        key="right_knee"
    )
    st.session_state.joint_data['right_knee'] = r_knee_value

# ============ Control Buttons ============
st.sidebar.markdown("---")
st.sidebar.subheader("Controls Panel")

btn_col1, btn_col2, btn_col3 = st.sidebar.columns(3)
with btn_col1:
    preview_btn = st.button("🔍 Preview", use_container_width=True, type="primary")
with btn_col2:
    save_btn = st.button("💾 Save", use_container_width=True)
with btn_col3:
    reset_btn = st.button("🔄 Reset", use_container_width=True)

# Load Example Data Button
if st.sidebar.button("📋 Load Example Data", use_container_width=True):
    # Create example data
    example_spine = [5*i for i in range(25)]  # 0, 5, 10, ..., 120
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
    
    st.sidebar.success("Example data loaded! Click 'Preview' to see.")
    st.session_state.example_loaded = True
    st.session_state.example_spine = example_spine
    st.session_state.example_joints = example_joints

# ============ Main Display Area ============
st.markdown("## 3D Skeleton Visualization")

# Prepare joint data
joint_data = st.session_state.joint_data

# If there's example data, use example data
if hasattr(st.session_state, 'example_loaded') and st.session_state.example_loaded:
    spine_values = st.session_state.example_spine
    joint_data = st.session_state.example_joints

# Create visualization placeholder
viz_placeholder = st.empty()
status_placeholder = st.empty()
summary_placeholder = st.empty()

# Preview function
if preview_btn:
    with st.spinner("🔄 Generating 3D skeleton model..."):
        # Validate data
        spine_valid, spine_msg = data_processor.validate_spine_data(spine_values)
        
        if not spine_valid:
            st.error(f"❌ Spine Data Error: {spine_msg}")
        else:
            # Validate joint data
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
                # Calculate skeleton positions
                joints = skeleton_model.calculate_from_angles(spine_values, joint_data)
                
                # Generate visualization
                fig, ax = skeleton_model.plot_3d_skeleton()
                
                # Display in placeholder
                with viz_placeholder.container():
                    st.pyplot(fig)
                
                # Save data
                data_processor.save_data(spine_values, joint_data)
                
                # Show success message
                status_placeholder.success("✅ 3D model generated successfully!")
                
                # Show data summary
                with summary_placeholder.container():
                    st.subheader("📈 Data Summary")
                    st.info(data_processor.get_summary())
                    
                    # Expandable data view
                    with st.expander("📊 View Detailed Data"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Spine Data:**")
                            for i, (label, angle) in enumerate(zip(spine_labels, spine_values)):
                                st.write(f"{label}: {angle}°")
                        
                        with col2:
                            st.write("**Joint Data:**")
                            for joint_name, angles in joint_data.items():
                                if isinstance(angles, list):
                                    st.write(f"{joint_name}: {angles[0]}°, {angles[1]}°, {angles[2]}°")
                                else:
                                    st.write(f"{joint_name}: {angles}°")

# Save function
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
                st.success("✅ Data saved successfully!")
                
                # Provide download
                import csv
                from io import StringIO
                
                output = StringIO()
                writer = csv.writer(output)
                
                # Write spine data
                writer.writerow(['Spine Segment', 'Angle(°)'])
                for i, angle in enumerate(spine_values):
                    writer.writerow([spine_labels[i], angle])
                
                writer.writerow([])
                writer.writerow(['Joint', 'Angle1', 'Angle2', 'Angle3'])
                
                for joint_name, angles in joint_data.items():
                    if isinstance(angles, list):
                        writer.writerow([joint_name, angles[0], angles[1], angles[2]])
                    else:
                        writer.writerow([joint_name, angles, '', ''])
                
                csv_data = output.getvalue()
                
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_data,
                    file_name="joint_angles_data.csv",
                    mime="text/csv"
                )
            else:
                st.error("❌ Data save failed")
    else:
        st.error(f"❌ {spine_msg}")

# Reset function
if reset_btn:
    reset_all_inputs()
    st.success("🔄 All input fields reset to 0")
    st.rerun()

# ============ Page Footer ============
st.markdown("---")
st.markdown("### 📖 User Guide")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **1. Input Data**
    - Enter 25 spine angles in the sidebar
    - Enter 8 joint angles
    - Click ❓ to view anatomy diagrams
    """)

with col2:
    st.markdown("""
    **2. Generate Model**
    - Click **Preview** to generate 3D skeleton
    - Model displays in main area
    - Data summary appears below
    """)

with col3:
    st.markdown("""
    **3. Save & Export**
    - Click **Save** to store data
    - Download as CSV file
    - Click **Reset** to clear all data
    """)

# Footer
st.markdown("---")
st.caption("© 2026 3D Human Skeleton Visualization System | Version 2.0 | Biomechanics Research Tool")