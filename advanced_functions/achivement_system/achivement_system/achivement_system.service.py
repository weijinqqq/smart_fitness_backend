    #初始化成就数据
    # achievement_service.py
def init_achievements():
    achievements = [
        {"name": "健身新手", "description": "完成首次运动", "rule_type": "first_activity"},
        {"name": "持之以恒", "description": "连续7天运动", "rule_type": "streak", "threshold": 7},
        {"name": "卡路里燃烧者", "description": "累计消耗5000卡路里", "rule_type": "total_calories", "threshold": 5000},
        # 更多成就...
    ]
    
    for ach in achievements:
        if not Achievement.query.filter_by(name=ach["name"]).first():
            new_ach = Achievement(**ach)
            db.session.add(new_ach)
    db.session.commit()


#成就检测逻辑
def check_achievements(user_id):
    user = User.query.get(user_id)
    if not user:
        return
    
    # 获取用户所有运动记录
    activities = Activity.query.filter_by(user_id=user_id).order_by(Activity.activity_date).all()
    
    # 检测首次运动成就
    if len(activities) == 1:
        grant_achievement(user_id, "健身新手")
    
    # 检测连续打卡成就
    if check_streak(activities, 7):
        grant_achievement(user_id, "持之以恒")
    
    # 检测总卡路里成就
    total_calories = sum(a.calories_burned for a in activities)
    if total_calories >= 5000:
        grant_achievement(user_id, "卡路里燃烧者")

def grant_achievement(user_id, achievement_name):
    achievement = Achievement.query.filter_by(name=achievement_name).first()
    if achievement and not UserAchievement.query.filter_by(
        user_id=user_id, achievement_id=achievement.id).first():
        
        user_ach = UserAchievement(
            user_id=user_id,
            achievement_id=achievement.id
        )
        db.session.add(user_ach)
        db.session.commit()
        
        # 可以在这里添加通知逻辑

#集成到现有API
# 在记录运动的API中触发检测
@app.route('/activities', methods=['POST'])
def create_activity():
    # ... 原有记录逻辑 ...
    db.session.commit()
    
    # 新增成就检测
    check_achievements(data['user_id'])
    
    return jsonify(...)

# 添加获取用户成就API
@app.route('/users/<int:user_id>/achievements', methods=['GET'])
def get_user_achievements(user_id):
    achievements = db.session.query(Achievement).join(
        UserAchievement,
        UserAchievement.achievement_id == Achievement.id
    ).filter(UserAchievement.user_id == user_id).all()
    
    return jsonify([{
        "name": a.name,
        "description": a.description,
        "icon": a.icon,
        "earned_date": ua.earned_date.isoformat()
    } for a in achievements])
