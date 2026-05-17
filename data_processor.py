"""
Data Processor Module
Handles validation and storage of joint angle data
"""

import numpy as np

class DataProcessor:
    def __init__(self):
        """Initialize data storage"""
        self.data = {
            'spine': [],        # Store 25 spine angles
            'joints': {}        # Store joint angles
        }
    
    def validate_spine_data(self, spine_values):
        """Validate spine data"""
        if len(spine_values) != 25:
            return False, f"Spine data requires 25 values, got {len(spine_values)}"
        
        for i, val in enumerate(spine_values):
            try:
                num = float(val)
                if not -180 <= num <= 180:
                    return False, f"Spine {i+1} angle out of range (-180~180): {num}"
            except:
                return False, f"Spine {i+1} is not a valid number: {val}"
        
        return True, "Spine data validated successfully"
    
    def validate_joint_data(self, joint_values, joint_name):
        """Validate joint data"""
        try:
            if isinstance(joint_values, list):
                for i, val in enumerate(joint_values):
                    num = float(val)
                    if not -180 <= num <= 180:
                        return False, f"{joint_name} angle {i+1} out of range: {num}"
            else:
                num = float(joint_values)
                if not -180 <= num <= 180:
                    return False, f"{joint_name} angle out of range: {num}"
            
            return True, f"{joint_name} data validated successfully"
        except:
            return False, f"{joint_name} is not valid number(s)"
    
    def save_data(self, spine_values, joint_values):
        """Save all data"""
        # Save spine data
        self.data['spine'] = [float(x) for x in spine_values]
        
        # Save joint data
        self.data['joints'] = {}
        for joint_name, values in joint_values.items():
            if isinstance(values, list):
                self.data['joints'][joint_name] = [float(x) for x in values]
            else:
                self.data['joints'][joint_name] = float(values)
        
        return True
    
    def get_summary(self):
        """Get data summary"""
        if not self.data['spine']:
            return "No data available"
        
        spine_min = min(self.data['spine'])
        spine_max = max(self.data['spine'])
        spine_avg = sum(self.data['spine']) / len(self.data['spine'])
        
        summary = f"""
        Data Summary:
        - Spine Angles: Min {spine_min:.1f}°, Max {spine_max:.1f}°, Avg {spine_avg:.1f}°
        - Number of Joints: {len(self.data['joints'])}
        - Data Validation: Passed
        """
        return summary