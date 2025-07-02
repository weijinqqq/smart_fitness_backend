#实现基础API

# 记录膳食
@app.route('/meals', methods=['POST'])
def create_meal():
    data = request.json
    new_meal = Meal(
        user_id=data['user_id'],
        name=data['name'],
        calories=data['calories'],
        protein=data.get('protein', 0),
        carbs=data.get('carbs', 0),
        fat=data.get('fat', 0),
        meal_type=data.get('meal_type', 'other')
    )
    db.session.add(new_meal)
    db.session.commit()
    return jsonify({"message": "Meal recorded"}), 201

# 获取用户膳食记录
@app.route('/users/<int:user_id>/meals', methods=['GET'])
def get_user_meals(user_id):
    meals = Meal.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": m.id,
        "name": m.name,
        "calories": m.calories,
        "meal_type": m.meal_type,
        "meal_time": m.meal_time.isoformat()
    } for m in meals])

#简单营养建议

def generate_nutrition_tips(user_id):
    # 获取用户目标（需要扩展用户模型）
    user = User.query.get(user_id)
    goal = user.fitness_goal  # 假设有字段：weight_loss/muscle_gain/maintenance
    
    # 获取今日膳食
    today = datetime.utcnow().date()
    meals_today = Meal.query.filter(
        Meal.user_id == user_id,
        db.func.date(Meal.meal_time) == today
    ).all()
    
    total_calories = sum(m.calories for m in meals_today)
    total_protein = sum(m.protein for m in meals_today)
    
    # 生成建议
    tips = []
    
    if goal == "weight_loss":
        if total_calories > 1800:
            tips.append("今日摄入已超过减脂建议量，建议增加运动消耗")
    
    if goal == "muscle_gain":
        if total_protein < 120:
            tips.append("蛋白质摄入不足，建议补充高蛋白食物")
    
    if not meals_today:
        tips.append("今日尚未记录任何餐食")
    elif len(meals_today) < 3:
        tips.append("建议增加餐次，保持规律饮食")
    
    return tips