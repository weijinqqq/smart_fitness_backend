from app import create_app
from app.models import db, User, Activity, FitnessPlan

# 创建Flask应用实例
app = create_app()

@app.cli.command('initdb')
def init_db_command():
    """初始化数据库命令"""
    db.create_all()
    
    # 创建示例预设计划
    preset_plan = FitnessPlan(
        plan_name="初学者健身计划",
        description="适合刚开始健身的人群",
        content={
            'days': [
                {'day': 1, 'exercises': ['慢跑 30分钟', '深蹲 3组×15次']},
                # ...其他天数的计划
            ]
        },
        is_preset=True
    )
    db.session.add(preset_plan)
    db.session.commit()
    print("Database initialized with preset plans.")

if __name__ == '__main__':
    app.run(debug=True)  # 启动开发服务器