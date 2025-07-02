# weather_service.py
import requests
from config import WEATHER_API_KEY

def get_weather(location):
    """获取指定位置的天气数据"""
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': WEATHER_API_KEY,
        'q': location,
        'aqi': 'no'
    }
    try:
        response = requests.get(base_url, params=params, timeout=3)
        data = response.json()
        return {
            "condition": data['current']['condition']['text'],
            "is_day": data['current']['is_day'],
            "temp_c": data['current']['temp_c']
        }
    except Exception as e:
        # 失败时返回默认值
        return {"condition": "Unknown", "is_day": 1, "temp_c": 25}
    

#推荐逻辑实现
# recommendation_service.py
from datetime import datetime

def generate_recommendation(location, current_time=None):
    if not current_time:
        current_time = datetime.utcnow()
    
    weather = get_weather(location)
    hour = current_time.hour
    
    # 根据天气和时间生成推荐
    if weather['condition'].lower() in ['rain', 'snow', 'storm']:
        return "室内跳绳"
    
    if 6 <= hour < 10:
        if weather['temp_c'] > 25:
            return "户外慢跑"
        else:
            return "室内瑜伽"
    
    if 10 <= hour < 16:
        return "高强度间歇训练"
    
    if 16 <= hour < 20:
        if weather['condition'].lower() == 'sunny':
            return "户外骑行"
        else:
            return "力量训练"
    
    if 20 <= hour < 23:
        return "拉伸与放松"
    
    return "基础健身操"  # 默认推荐


#添加推荐API
@app.route('/users/<int:user_id>/recommendation', methods=['GET'])
def get_recommendation(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # 需要先确保用户设置了位置信息
    if not user.location:
        return jsonify({"error": "Location not set"}), 400
    
    recommendation = generate_recommendation(
        location=user.location,
        current_time=datetime.utcnow()
    )
    
    return jsonify({
        "recommendation": recommendation,
        "timestamp": datetime.utcnow().isoformat()
    })
