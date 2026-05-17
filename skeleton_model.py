"""
3D Skeleton Model Module
Calculates and visualizes human skeleton with FIXED Z-AXIS DISPLAY
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math

class SkeletonModel3D:
    def __init__(self):
        """Initialize skeleton model"""
        # Bone lengths (relative units)
        self.bone_lengths = {
            'spine': 0.8,        # Each spine segment
            'upper_arm': 1.2,    # Upper arm
            'forearm': 1.0,      # Forearm
            'thigh': 1.5,        # Thigh
            'shin': 1.3,         # Shin
        }
        
        # Joint positions
        self.joints = {}
    
    def calculate_from_angles(self, spine_angles, joint_angles):
        """
        Calculate joint positions from angles
        
        Args:
            spine_angles: 25 spine angles
            joint_angles: Dictionary of joint angles
        """
        # Reset joint positions
        self.joints = {}
        
        # 1. Calculate spine (from pelvis to head)
        self._calculate_spine(spine_angles)
        
        # 2. Calculate limbs
        self._calculate_limbs(joint_angles)
        
        return self.joints
    
    def _calculate_spine(self, spine_angles):
        """Calculate spine positions with natural curvature"""
        # Start from pelvis center
        x, y, z = 0, 0, 0
        self.joints['pelvis'] = (x, y, z)
        
        # Natural spine curvature parameters
        cervical_curve = 20.0   # Cervical lordosis
        thoracic_curve = 40.0   # Thoracic kyphosis
        lumbar_curve = 30.0     # Lumbar lordosis
        
        # Calculate 25 spine segments
        for i in range(25):
            angle = np.radians(spine_angles[i])
            height = self.bone_lengths['spine']
            
            # Add natural curvature based on spine region
            if i < 7:  # Cervical (C1-C7)
                natural_curve = np.radians(cervical_curve * (i / 6))
            elif i < 19:  # Thoracic (T1-T12)
                natural_curve = np.radians(thoracic_curve * ((i-7) / 11))
            else:  # Lumbar (L1-L5) and Sacrum
                natural_curve = np.radians(lumbar_curve * ((i-19) / 5))
            
            # Combine input angle with natural curve
            total_angle = angle + natural_curve
            
            # Calculate next spine position
            y += height * np.cos(total_angle)
            z += height * np.sin(total_angle)
            
            self.joints[f'spine_{i+1}'] = (x, y, z)
        
        # Head position
        neck_x, neck_y, neck_z = self.joints['spine_7']  # C7
        self.joints['head'] = (neck_x, neck_y + 0.3, neck_z)
    
    def _calculate_limbs(self, joint_angles):
        """Calculate limb positions"""
        # Get neck position (C7)
        neck_x, neck_y, neck_z = self.joints.get('spine_7', (0, 3, 0))
        
        # Left shoulder
        shoulder_width = 1.2
        self.joints['left_shoulder'] = (neck_x - shoulder_width, neck_y, neck_z)
        
        # Left elbow
        l_shoulder = self.joints['left_shoulder']
        l_shoulder_angles = joint_angles.get('left_shoulder', [0, 0, 0])
        self.joints['left_elbow'] = self._calculate_joint_position(
            l_shoulder, l_shoulder_angles, self.bone_lengths['upper_arm']
        )
        
        # Left wrist
        l_elbow = self.joints['left_elbow']
        l_elbow_angle = joint_angles.get('left_elbow', 0)
        self.joints['left_wrist'] = self._calculate_joint_position(
            l_elbow, [0, 0, l_elbow_angle], self.bone_lengths['forearm']
        )
        
        # Right shoulder
        self.joints['right_shoulder'] = (neck_x + shoulder_width, neck_y, neck_z)
        
        # Right elbow
        r_shoulder = self.joints['right_shoulder']
        r_shoulder_angles = joint_angles.get('right_shoulder', [0, 0, 0])
        self.joints['right_elbow'] = self._calculate_joint_position(
            r_shoulder, r_shoulder_angles, self.bone_lengths['upper_arm']
        )
        
        # Right wrist
        r_elbow = self.joints['right_elbow']
        r_elbow_angle = joint_angles.get('right_elbow', 0)
        self.joints['right_wrist'] = self._calculate_joint_position(
            r_elbow, [0, 0, r_elbow_angle], self.bone_lengths['forearm']
        )
        
        # Get pelvis position
        pelvis_x, pelvis_y, pelvis_z = self.joints['pelvis']
        hip_width = 0.8
        
        # Left hip
        self.joints['left_hip'] = (pelvis_x - hip_width, pelvis_y, pelvis_z)
        
        # Left knee
        l_hip = self.joints['left_hip']
        l_hip_angles = joint_angles.get('left_hip', [0, 0, 0])
        self.joints['left_knee'] = self._calculate_joint_position(
            l_hip, l_hip_angles, self.bone_lengths['thigh']
        )
        
        # Left ankle
        l_knee = self.joints['left_knee']
        l_knee_angle = joint_angles.get('left_knee', 0)
        self.joints['left_ankle'] = self._calculate_joint_position(
            l_knee, [0, 0, l_knee_angle], self.bone_lengths['shin']
        )
        
        # Right hip
        self.joints['right_hip'] = (pelvis_x + hip_width, pelvis_y, pelvis_z)
        
        # Right knee
        r_hip = self.joints['right_hip']
        r_hip_angles = joint_angles.get('right_hip', [0, 0, 0])
        self.joints['right_knee'] = self._calculate_joint_position(
            r_hip, r_hip_angles, self.bone_lengths['thigh']
        )
        
        # Right ankle
        r_knee = self.joints['right_knee']
        r_knee_angle = joint_angles.get('right_knee', 0)
        self.joints['right_ankle'] = self._calculate_joint_position(
            r_knee, [0, 0, r_knee_angle], self.bone_lengths['shin']
        )
    
    def _calculate_joint_position(self, parent_joint, angles, length):
        """Calculate child joint position from parent"""
        px, py, pz = parent_joint
        
        # Convert to radians
        rx, ry, rz = np.radians(angles)
        
        # Calculate offsets (simplified rotation)
        dx = length * np.sin(ry) * np.cos(rz)
        dy = length * np.cos(rx) * np.sin(rz)
        dz = length * np.sin(rx) * np.cos(ry)
        
        return (px + dx, py + dy, pz + dz)
    
    def plot_3d_skeleton(self, figsize=(10, 8)):
        """Plot 3D skeleton visualization with FIXED Z-AXIS DISPLAY"""
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # If no joint data, show empty plot
        if not self.joints:
            ax.text(0, 0, 0, "No Data", ha='center', fontsize=12)
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.set_zlim(-5, 5)
            ax.set_xlabel('X Axis')
            ax.set_ylabel('Y Axis')
            ax.set_zlabel('Z Axis')
            ax.set_title('3D Human Skeleton Model')
            return fig, ax
        
        # Define bone connections
        connections = [
            # Spine
            (['pelvis', 'spine_1', 'spine_2', 'spine_3', 'spine_4', 'spine_5',
              'spine_6', 'spine_7', 'spine_8', 'spine_9', 'spine_10',
              'spine_11', 'spine_12', 'spine_13', 'spine_14', 'spine_15',
              'spine_16', 'spine_17', 'spine_18', 'spine_19', 'spine_20',
              'spine_21', 'spine_22', 'spine_23', 'spine_24', 'spine_25', 'head'], 'blue'),
            
            # Left upper limb
            (['left_shoulder', 'left_elbow', 'left_wrist'], 'red'),
            
            # Right upper limb
            (['right_shoulder', 'right_elbow', 'right_wrist'], 'red'),
            
            # Left lower limb
            (['left_hip', 'left_knee', 'left_ankle'], 'green'),
            
            # Right lower limb
            (['right_hip', 'right_knee', 'right_ankle'], 'green'),
        ]
        
        # Draw bones
        for joint_names, color in connections:
            x_coords = []
            y_coords = []
            z_coords = []
            
            for name in joint_names:
                if name in self.joints:
                    x, y, z = self.joints[name]
                    x_coords.append(x)
                    y_coords.append(y)
                    z_coords.append(z)
            
            if x_coords:
                ax.plot(x_coords, y_coords, z_coords, 
                       color=color, linewidth=3, marker='o', markersize=4)
        
        # Set axis labels
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Z Axis')
        ax.set_title('3D Human Skeleton Model')
        
        # Set view
        ax.view_init(elev=25, azim=-45)  # 更合理的默认视角
        
        # ====== CRITICAL FIX: FORCE EQUAL SCALING IN 3D ======
        # 获取所有点的坐标
        all_points = np.array(list(self.joints.values()))
        xs, ys, zs = all_points[:, 0], all_points[:, 1], all_points[:, 2]
        
        # 计算全局范围（确保X/Y/Z轴单位长度一致）
        max_range = max(
            np.max(xs) - np.min(xs),
            np.max(ys) - np.min(ys),
            np.max(zs) - np.min(zs)
        ) * 0.6  # 0.6是留白系数
        
        # 设置中心点
        mid_x = (np.max(xs) + np.min(xs)) * 0.5
        mid_y = (np.max(ys) + np.min(ys)) * 0.5
        mid_z = (np.max(zs) + np.min(zs)) * 0.5
        
        # 强制等比例坐标系（核心修复）
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        ax.set_box_aspect([1, 1, 1])  # 这是解决Z轴压缩的关键！
        # ===================================================
        
        plt.tight_layout()
        return fig, ax

# ====== 测试代码 ======
if __name__ == "__main__":
    # 创建模型实例
    skeleton = SkeletonModel3D()
    
    # 生成测试角度（直立姿势）
    spine_angles = [0] * 25  # 脊柱各段角度
    joint_angles = {
        'left_shoulder': [0, 0, 0],
        'right_shoulder': [0, 0, 0],
        'left_elbow': 0,
        'right_elbow': 0,
        'left_hip': [0, 0, 0],
        'right_hip': [0, 0, 0],
        'left_knee': 0,
        'right_knee': 0
    }
    
    # 计算骨架
    skeleton.calculate_from_angles(spine_angles, joint_angles)
    
    # 绘制3D骨架（Z轴现在会正确显示）
    fig, ax = skeleton.plot_3d_skeleton()
    
    # 添加Z轴网格线（更清晰显示）
    ax.zaxis._axinfo["grid"]["linewidth"] = 0.5
    ax.zaxis._axinfo["grid"]["color"] = "gray"
    
    plt.show()