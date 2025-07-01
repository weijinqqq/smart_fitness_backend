from app import db
from datetime import datetime

#数据库模型

#运动记录数据模型
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False) #运动类型
    duration_minutes = db.Column(db.Integer, nullable=False) #运动时长
    calories_burned = db.Column(db.Integer, nullable=False) #卡路里消耗
    activity_date = db.Column(db.DateTime, default=datetime.utcnow) #记录时间

    def to_dict(self):
        #将模型对象转换为字典，用于JSON响应
        return {
            "id": self.id,
            "activity_type": self.activity_type,
            "duration_minutes": self.duration_minutes,
            "calories_burned": self.calories_burned,
            "activity_date": self.activity_date.isoformat()
        }

#健身计划数据模型
class FitnessPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False) #计划名称
    description = db.Column(db.Text) #计划描述
    content = db.Column(db.JSON)  # 存储计划详情
    is_preset = db.Column(db.Boolean, default=False)  # 是否为系统预设
    created_at = db.Column(db.DateTime, default=datetime.utcnow) #创建时间

    def to_dict(self):
        #将模型对象转换为字典，用于JSON响应
        return {
            "id": self.id,
            "plan_name": self.plan_name,
            "description": self.description,
            "is_preset": self.is_preset,
            "created_at": self.created_at.isoformat()
        }
