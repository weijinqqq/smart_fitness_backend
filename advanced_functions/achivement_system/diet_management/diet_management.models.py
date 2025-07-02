from app import db
from datetime import datetime

# models.py
class Meal(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer)
    protein = db.Column(db.Float)  # 蛋白质(g)
    carbs = db.Column(db.Float)    # 碳水化合物(g)
    fat = db.Column(db.Float)      # 脂肪(g)
    meal_time = db.Column(db.DateTime, default=datetime.utcnow)
    meal_type = db.Column(db.String(20))  # breakfast/lunch/dinner/snack