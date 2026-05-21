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
        # 骨骼长度（相对单位）
        self.bone_lengths = {
            'spine': 0.8,        # 每个脊柱节段
            'upper_arm': 1.2,    # 上臂
            'forearm': 1.0,      # 前臂
            'thigh': 1.5,        # 大腿
            'shin': 1.3,         # 小腿
        }
        
        # 关节位置
        self.joints = {}

    def calculate_from_angles(self, spine_angles, joint_angles):
        """
        从角度计算关节位置
        
        参数:
            spine_angles: 25个脊柱角度
            joint_angles: 关节角度字典
        """
        # 重置关节位置
        self.joints = {}
        
        # 1. 计算脊柱（从骨盆到头部）
        self._calculate_spine(spine_angles)
        
        # 2. 计算四肢
        self._calculate_limbs(joint_angles)
        
        return self.joints

    def _calculate_spine(self, spine_angles):
        """计算具有自然曲度的脊柱位置"""
        # 从骨盆中心开始
        x, y, z = 0, 0, 0
        self.joints['pelvis'] = (x, y, z)
        
        # 脊柱自然曲度参数
        cervical_curve = 20.0  # 颈椎前凸
        thoracic_curve = 40.0  # 胸椎后凸
        lumbar_curve = 30.0    # 腰椎前凸
        
        # 计算25个脊柱节段
        for i in range(25):
            angle = np.radians(spine_angles[i])
            height = self.bone_lengths['spine']
            
            # 根据脊柱区域添加自然曲度
            if i < 7:  # 颈椎 (C1-C7)
                natural_curve = np.radians(cervical_curve * (i / 6))
            elif i < 19:  # 胸椎 (T1-T12)
                natural_curve = np.radians(thoracic_curve * ((i - 7) / 11))
            else:  # 腰椎 (L1-L5) 和骶骨
                natural_curve = np.radians(lumbar_curve * ((i - 19) / 5))
            
            # 组合输入角度和自然曲度
            total_angle = angle + natural_curve
            
            # 计算下一个脊柱位置
            y += height * np.cos(total_angle)
            z += height * np.sin(total_angle)
            
            self.joints[f'spine_{i+1}'] = (x, y, z)
        
        # 头部位置
        neck_x, neck_y, neck_z = self.joints['spine_7']  # C7
        self.joints['head'] = (neck_x, neck_y + 0.3, neck_z)

    def _calculate_limbs(self, joint_angles):
        """计算四肢位置"""
        # 获取颈部位置 (C7)
        neck_x, neck_y, neck_z = self.joints.get('spine_7', (0, 3, 0))
        
        # 左肩
        shoulder_width = 1.2
        self.joints['left_shoulder'] = (neck_x - shoulder_width, neck_y, neck_z)
        
        # 左肘
        l_shoulder = self.joints['left_shoulder']
        l_shoulder_angles = joint_angles.get('left_shoulder', [0, 0, 0])
        self.joints['left_elbow'] = self._calculate_joint_position(
            l_shoulder, l_shoulder_angles, self.bone_lengths['upper_arm']
        )
        
        # 左腕
        l_elbow = self.joints['left_elbow']
        l_elbow_angle = joint_angles.get('left_elbow', 0)
        self.joints['left_wrist'] = self._calculate_joint_position(
            l_elbow, [0, 0, l_elbow_angle], self.bone_lengths['forearm']
        )
        
        # 右肩
        self.joints['right_shoulder'] = (neck_x + shoulder_width, neck_y, neck_z)
        
        # 右肘
        r_shoulder = self.joints['right_shoulder']
        r_shoulder_angles = joint_angles.get('right_shoulder', [0, 0, 0])
        self.joints['right_elbow'] = self._calculate_joint_position(
            r_shoulder, r_shoulder_angles, self.bone_lengths['upper_arm']
        )
        
        # 右腕
        r_elbow = self.joints['right_elbow']
        r_elbow_angle = joint_angles.get('right_elbow', 0)
        self.joints['right_wrist'] = self._calculate_joint_position(
            r_elbow, [0, 0, r_elbow_angle], self.bone_lengths['forearm']
        )
        
        # 获取骨盆位置
        pelvis_x, pelvis_y, pelvis_z = self.joints['pelvis']
        hip_width = 0.8
        
        # 左髋
        self.joints['left_hip'] = (pelvis_x - hip_width, pelvis_y, pelvis_z)
        
        # 左膝
        l_hip = self.joints['left_hip']
        l_hip_angles = joint_angles.get('left_hip', [0, 0, 0])
        self.joints['left_knee'] = self._calculate_joint_position(
            l_hip, l_hip_angles, self.bone_lengths['thigh']
        )
        
        # 左踝
        l_knee = self.joints['left_knee']
        l_knee_angle = joint_angles.get('left_knee', 0)
        self.joints['left_ankle'] = self._calculate_joint_position(
            l_knee, [0, 0, l_knee_angle], self.bone_lengths['shin']
        )
        
        # 右髋
        self.joints['right_hip'] = (pelvis_x + hip_width, pelvis_y, pelvis_z)
        
        # 右膝
        r_hip = self.joints['right_hip']
        r_hip_angles = joint_angles.get('right_hip', [0, 0, 0])
        self.joints['right_knee'] = self._calculate_joint_position(
            r_hip, r_hip_angles, self.bone_lengths['thigh']
        )
        
        # 右踝
        r_knee = self.joints['right_knee']
        r_knee_angle = joint_angles.get('right_knee', 0)
        self.joints['right_ankle'] = self._calculate_joint_position(
            r_knee, [0, 0, r_knee_angle], self.bone_lengths['shin']
        )

    def _calculate_joint_position(self, parent_joint, angles, length):
        """从父关节计算子关节位置"""
        px, py, pz = parent_joint
        
        # 转换为弧度
        rx, ry, rz = np.radians(angles)
        
        # 计算偏移量（简化旋转）
        dx = length * np.sin(ry) * np.cos(rz)
        dy = length * np.cos(rx) * np.sin(rz)
        dz = length * np.sin(rx) * np.cos(ry)
        
        return (px + dx, py + dy, pz + dz)

    def plot_3d_skeleton(self, figsize=(10, 8)):
        """绘制3D骨架可视化（固定Z轴显示）"""
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # 如果没有关节数据，显示空图
        if not self.joints:
            ax.text(0, 0, 0, "无数据", ha='center', fontsize=12)
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.set_zlim(-5, 5)
            ax.set_xlabel('X轴')
            ax.set_ylabel('Y轴')
            ax.set_zlabel('Z轴')
            ax.set_title('3D人体骨架模型')
            return fig, ax
        
        # 定义骨骼连接
        connections = [
            # 脊柱
            (['pelvis', 'spine_1', 'spine_2', 'spine_3', 'spine_4', 'spine_5',
              'spine_6', 'spine_7', 'spine_8', 'spine_9', 'spine_10',
              'spine_11', 'spine_12', 'spine_13', 'spine_14', 'spine_15',
              'spine_16', 'spine_17', 'spine_18', 'spine_19', 'spine_20',
              'spine_21', 'spine_22', 'spine_23', 'spine_24', 'spine_25', 'head'], 'blue'),
            # 左上肢
            (['left_shoulder', 'left_elbow', 'left_wrist'], 'red'),
            # 右上肢
            (['right_shoulder', 'right_elbow', 'right_wrist'], 'red'),
            # 左下肢
            (['left_hip', 'left_knee', 'left_ankle'], 'green'),
            # 右下肢
            (['right_hip', 'right_knee', 'right_ankle'], 'green'),
        ]
        
        # 绘制骨骼
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
        
        # 设置坐标轴标签
        ax.set_xlabel('X轴')
        ax.set_ylabel('Y轴')
        ax.set_zlabel('Z轴')
        ax.set_title('3D人体骨架模型')
        
        # 设置视角
        ax.view_init(elev=25, azim=-45)  # 更合理的默认视角
        
        # 关键修复：强制3D等比例缩放
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
        
        plt.tight_layout()
        return fig, ax
    
    def plot_multi_view(self, figsize=(15, 10)):
        """绘制多视角（正面、侧面、俯视、3D）骨架图"""
        fig = plt.figure(figsize=figsize)
        
        # 定义四个子图
        ax_3d = fig.add_subplot(221, projection='3d')
        ax_front = fig.add_subplot(222)  # 正面视图 (X-Z平面)
        ax_side = fig.add_subplot(223)   # 侧面视图 (Y-Z平面)
        ax_top = fig.add_subplot(224)    # 俯视图 (X-Y平面)
        
        # 如果没有关节数据，显示空图
        if not self.joints:
            for ax, title in [(ax_3d, "3D视图"), (ax_front, "正面视图"), 
                             (ax_side, "侧面视图"), (ax_top, "俯视图")]:
                if ax is ax_3d:
                    ax.text(0, 0, 0, "无数据", ha='center', fontsize=10)
                    ax.set_xlim(-5, 5)
                    ax.set_ylim(-5, 5)
                    ax.set_zlim(-5, 5)
                else:
                    ax.text(0.5, 0.5, "无数据", ha='center', va='center', 
                           transform=ax.transAxes, fontsize=10)
                    ax.set_xlim(-5, 5)
                    ax.set_ylim(-5, 5)
                ax.set_title(title)
                ax.set_aspect('equal')
            return fig
        
        # 定义骨骼连接（与plot_3d_skeleton相同）
        connections = [
            (['pelvis', 'spine_1', 'spine_2', 'spine_3', 'spine_4', 'spine_5',
              'spine_6', 'spine_7', 'spine_8', 'spine_9', 'spine_10',
              'spine_11', 'spine_12', 'spine_13', 'spine_14', 'spine_15',
              'spine_16', 'spine_17', 'spine_18', 'spine_19', 'spine_20',
              'spine_21', 'spine_22', 'spine_23', 'spine_24', 'spine_25', 'head'], 'blue'),
            (['left_shoulder', 'left_elbow', 'left_wrist'], 'red'),
            (['right_shoulder', 'right_elbow', 'right_wrist'], 'red'),
            (['left_hip', 'left_knee', 'left_ankle'], 'green'),
            (['right_hip', 'right_knee', 'right_ankle'], 'green'),
        ]
        
        # 绘制所有视图
        views = [
            (ax_3d, "3D视图", '3d'),
            (ax_front, "正面视图 (X-Z平面)", '2d'),
            (ax_side, "侧面视图 (Y-Z平面)", '2d'),
            (ax_top, "俯视图 (X-Y平面)", '2d'),
        ]
        
        for ax, title, view_type in views:
            for joint_names, color in connections:
                coords = {'x': [], 'y': [], 'z': []}
                
                for name in joint_names:
                    if name in self.joints:
                        x, y, z = self.joints[name]
                        coords['x'].append(x)
                        coords['y'].append(y)
                        coords['z'].append(z)
                
                if coords['x']:
                    if view_type == '3d':
                        # 3D视图
                        ax.plot(coords['x'], coords['y'], coords['z'],
                               color=color, linewidth=2, marker='o', markersize=3)
                    else:
                        # 2D视图
                        if ax is ax_front:  # 正面视图: X-Z
                            ax.plot(coords['x'], coords['z'], 
                                   color=color, linewidth=2, marker='o', markersize=3)
                        elif ax is ax_side:  # 侧面视图: Y-Z
                            ax.plot(coords['y'], coords['z'], 
                                   color=color, linewidth=2, marker='o', markersize=3)
                        else:  # 俯视图: X-Y
                            ax.plot(coords['x'], coords['y'], 
                                   color=color, linewidth=2, marker='o', markersize=3)
            
            # 设置各视图的坐标轴标签和标题
            if view_type == '3d':
                ax.set_xlabel('X轴')
                ax.set_ylabel('Y轴')
                ax.set_zlabel('Z轴')
                ax.view_init(elev=25, azim=-45)
                
                # 设置3D视图的等比例缩放
                all_points = np.array(list(self.joints.values()))
                xs, ys, zs = all_points[:, 0], all_points[:, 1], all_points[:, 2]
                
                max_range = max(
                    np.max(xs) - np.min(xs),
                    np.max(ys) - np.min(ys),
                    np.max(zs) - np.min(zs)
                ) * 0.6
                
                mid_x = (np.max(xs) + np.min(xs)) * 0.5
                mid_y = (np.max(ys) + np.min(ys)) * 0.5
                mid_z = (np.max(zs) + np.min(zs)) * 0.5
                
                ax.set_xlim(mid_x - max_range, mid_x + max_range)
                ax.set_ylim(mid_y - max_range, mid_y + max_range)
                ax.set_zlim(mid_z - max_range, mid_z + max_range)
                ax.set_box_aspect([1, 1, 1])
            else:
                # 2D视图设置
                ax.set_aspect('equal')
                ax.grid(True, alpha=0.3)
                
                if ax is ax_front:
                    ax.set_xlabel('X轴')
                    ax.set_ylabel('Z轴')
                elif ax is ax_side:
                    ax.set_xlabel('Y轴')
                    ax.set_ylabel('Z轴')
                else:  # ax_top
                    ax.set_xlabel('X轴')
                    ax.set_ylabel('Y轴')
            
            ax.set_title(title)
        
        plt.tight_layout()
        return fig

#====== 测试代码 =======
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
    
    # 绘制3D骨架
    fig_3d, ax_3d = skeleton.plot_3d_skeleton()
    
    # 绘制多视图
    fig_multi = skeleton.plot_multi_view()
    
    # 添加Z轴网格线
    ax_3d.zaxis._axinfo["grid"]["linewidth"] = 0.5
    ax_3d.zaxis._axinfo["grid"]["color"] = "gray"
    
    plt.show()