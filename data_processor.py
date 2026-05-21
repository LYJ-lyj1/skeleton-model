"""
数据处理器模块
处理关节角度数据的验证和存储
"""

import numpy as np

class DataProcessor:
    def __init__(self):
        """初始化数据存储"""
        self.data = {
            'spine': [],        # 存储25个脊柱角度
            'joints': {}        # 存储关节角度
        }
    
    def validate_spine_data(self, spine_values):
        """验证脊柱数据"""
        if len(spine_values) != 25:
            return False, f"脊柱数据需要25个值，但得到{len(spine_values)}个"
        
        for i, val in enumerate(spine_values):
            try:
                num = float(val)
                if not -180 <= num <= 180:
                    return False, f"脊柱{i+1}角度超出范围(-180~180): {num}"
            except:
                return False, f"脊柱{i+1}不是有效的数字: {val}"
        
        return True, "脊柱数据验证成功"
    
    def validate_joint_data(self, joint_values, joint_name):
        """验证关节数据"""
        try:
            if isinstance(joint_values, list):
                for i, val in enumerate(joint_values):
                    num = float(val)
                    if not -180 <= num <= 180:
                        return False, f"{joint_name}角度{i+1}超出范围: {num}"
            else:
                num = float(joint_values)
                if not -180 <= num <= 180:
                    return False, f"{joint_name}角度超出范围: {num}"
            
            return True, f"{joint_name}数据验证成功"
        except:
            return False, f"{joint_name}不是有效的数字"
    
    def save_data(self, spine_values, joint_values):
        """保存所有数据"""
        # 保存脊柱数据
        self.data['spine'] = [float(x) for x in spine_values]
        
        # 保存关节数据
        self.data['joints'] = {}
        for joint_name, values in joint_values.items():
            if isinstance(values, list):
                self.data['joints'][joint_name] = [float(x) for x in values]
            else:
                self.data['joints'][joint_name] = float(values)
        
        return True
    
    def get_summary(self):
        """获取数据摘要"""
        if not self.data['spine']:
            return "无可用数据"
        
        spine_min = min(self.data['spine'])
        spine_max = max(self.data['spine'])
        spine_avg = sum(self.data['spine']) / len(self.data['spine'])
        
        summary = f"""
        数据摘要:
        - 脊柱角度: 最小 {spine_min:.1f}°, 最大 {spine_max:.1f}°, 平均 {spine_avg:.1f}°
        - 关节数量: {len(self.data['joints'])}
        - 数据验证: 通过
        """
        return summary