from app import db
from datetime import datetime

#数据库扩展
# models.py 添加新模型
class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 成就名称
    description = db.Column(db.Text)  # 成就描述
    icon = db.Column(db.String(200))  # 徽章图标URL
    rule_type = db.Column(db.String(50))  # 规则类型：streak/duration/total等
    threshold = db.Column(db.Integer)  # 达成阈值

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'))
    earned_date = db.Column(db.DateTime, default=datetime.utcnow)

