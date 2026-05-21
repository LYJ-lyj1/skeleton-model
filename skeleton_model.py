import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 设置 Matplotlib 中文支持（防止乱码）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class SkeletonModel3D:
    def __init__(self):
        self.joints = {}
        # 定义骨骼连接关系
        self.connections = [
            # 脊柱 (蓝色)
            (['pelvis', 'spine_1', 'spine_2', 'spine_3', 'spine_4', 'spine_5',
              'spine_6', 'spine_7', 'spine_8', 'spine_9', 'spine_10',
              'spine_11', 'spine_12', 'spine_13', 'spine_14', 'spine_15',
              'spine_16', 'spine_17', 'spine_18', 'spine_19', 'spine_20',
              'spine_21', 'spine_22', 'spine_23', 'spine_24', 'spine_25', 'head'], 'blue'),
            
            # 手臂 (红色)
            (['left_shoulder', 'left_elbow', 'left_wrist'], 'red'),
            (['right_shoulder', 'right_elbow', 'right_wrist'], 'red'),
            
            # 腿部 (绿色)
            (['left_hip', 'left_knee', 'left_ankle'], 'green'),
            (['right_hip', 'right_knee', 'right_ankle'], 'green'),
        ]
        
        # 基础骨骼长度参数
        self.base_lengths = {
            'spine': 0.8, 'leg': 0.9, 'arm': 0.7, 'head': 0.3
        }

    def _create_simple_skeleton_data(self):
        """创建一个默认直立姿势的数据"""
        joints = {}
        # 骨盆在原点
        joints['pelvis'] = [0, 0, 0]
        
        # 脊柱向上 (沿着 Z 轴)
        for i in range(1, 26):
            joints[f'spine_{i}'] = [0, 0, i * self.base_lengths['spine']]
        joints['head'] = [0, 0, 26 * self.base_lengths['spine'] + self.base_lengths['head']]
        
        # 肩膀和髋部
        joints['left_hip'] = [-0.2, 0, 0]
        joints['right_hip'] = [0.2, 0, 0]
        joints['left_shoulder'] = [-0.3, 0, 5 * self.base_lengths['spine']]
        joints['right_shoulder'] = [0.3, 0, 5 * self.base_lengths['spine']]
        
        # 手脚 (为了简化，暂时放在同一个位置，实际应该根据角度计算)
        # 膝盖和脚踝
        joints['left_knee'] = [-0.2, 0, -self.base_lengths['leg']]
        joints['right_knee'] = [0.2, 0, -self.base_lengths['leg']]
        joints['left_ankle'] = [-0.2, 0, -2 * self.base_lengths['leg']]
        joints['right_ankle'] = [0.2, 0, -2 * self.base_lengths['leg']]
        
        # 手腕
        joints['left_wrist'] = [-0.4, 0, 5 * self.base_lengths['spine'] + self.base_lengths['arm']]
        joints['right_wrist'] = [0.4, 0, 5 * self.base_lengths['spine'] + self.base_lengths['arm']]
        
        return joints

    def calculate_from_angles(self, spine_angles, joint_angles):
        """
        根据角度计算骨架坐标
        TODO: 目前这里只是生成默认数据，你需要在未来实现真正的FK（正向运动学）计算
        """
        try:
            # 目前直接生成默认直立姿势
            self.joints = self._create_simple_skeleton_data()
            
            # 这里应该是根据 spine_angles 和 joint_angles 修改 self.joints 的逻辑
            # 例如：如果左腿弯曲 30 度，就修改 left_knee 和 left_ankle 的 Z 坐标
            
            return True
        except Exception as e:
            print(f"Error calculating skeleton: {e}")
            return False

    def plot_clean_skeleton(self, figsize=(8, 6)):
        """
        【核心功能】绘制完全干净的骨架图
        特性：无坐标轴、无边框、透明背景
        """
        if not self.joints:
            return None, None

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')

        # 绘制骨骼连接
        for joint_names, color in self.connections:
            coords = {'x': [], 'y': [], 'z': []}
            
            valid_points = 0
            for name in joint_names:
                if name in self.joints:
                    x, y, z = self.joints[name]
                    coords['x'].append(x)
                    coords['y'].append(y)
                    coords['z'].append(z)
                    valid_points += 1
            
            if coords['x'] and valid_points > 1:
                ax.plot(coords['x'], coords['y'], coords['z'],
                       color=color, linewidth=4, marker='o', markersize=6, alpha=0.9)

        # === 核心去坐标轴设置 ===
        
        # 1. 彻底关闭坐标轴显示 (包括刻度、标签、轴线)
        ax.axis('off') 
        
        # 2. 关闭所有边框线 (spine)
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        # 3. 设置背景为透明 (解决白底遮挡问题)
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)

        # 4. 调整视角 (仰角20度，方位角-60度)
        ax.view_init(elev=20, azim=-60)

        # 5. 限制坐标轴范围，让模型居中并强制等比例
        all_points = np.array(list(self.joints.values()))
        if len(all_points) > 0:
            min_vals = np.min(all_points, axis=0)
            max_vals = np.max(all_points, axis=0)
            
            center = (max_vals + min_vals) / 2
            # 增加一点范围，让骨架不至于贴边
            max_range = np.max(max_vals - min_vals) * 0.7
            
            ax.set_xlim(center[0] - max_range, center[0] + max_range)
            ax.set_ylim(center[1] - max_range, center[1] + max_range)
            ax.set_zlim(center[2] - max_range, center[2] + max_range)
            
            # 强制等比例，防止人体被压扁
            ax.set_box_aspect([1, 1, 1])

        plt.tight_layout()
        return fig, ax

#====== 本地测试代码 =======
if __name__ == "__main__":
    skeleton = SkeletonModel3D()
    skeleton.calculate_from_angles([], {})
    
    # 测试干净骨架图
    fig, ax = skeleton.plot_clean_skeleton()
    if fig:
        plt.show()