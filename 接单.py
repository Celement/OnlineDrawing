from flask import Flask, render_template, request, redirect,url_for
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

import io
import base64
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__,static_url_path="")

# 创建SQLite数据库连接
engine = create_engine('mysql+pymysql://root:root@localhost:3306/yali')

@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        # 获取表单数据
        x_values=request.form.get('x_values')
        y_values=request.form.get('y_values')
        z_pa =request.form.get('z_pa')
        if x_values!="" and y_values!="" and z_pa!="":
            x = list(map(int, request.form.get('x_values').split(',')))
            y = list(map(int, request.form.get('y_values').split(',')))
            # z_pa = request.form.get('z_pa')
            # if x.count()<0:
            #     print("传入数据为空")
            # 将数据插入到数据库
            df = pd.DataFrame({'time': x, 'mpa': y, 'z_pa': z_pa})
            df.to_sql('ya_li', con=engine, if_exists='append', index=False)
            return redirect(url_for('index'))
        else:
            return "请传入合法数据"
    return ""

@app.route('/', methods=['GET', 'POST'])
def index():


        # 设置字体路径
    font_path = 'C:/Users/song/PycharmProjects/gpt_pr/SimSun.ttf'  # 替换为你的字体文件路径
    # 创建FontProperties对象
    font = FontProperties(fname=font_path)
    # 读取数据库表到pandas DataFrame
    df = pd.read_sql('SELECT * FROM ya_li', con=engine)

    # 按最后一列分组并转换为列表
    grouped = df.groupby('z_pa')

    # 创建一个列表来存储处理后的数据
    processed_data = []

    # 颜色列表
    colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown', 'pink']

    # 遍历每个分组
    for i, (group_name, data) in enumerate(grouped):
        # 提取第二列和第三列数据并按索引转换为列表
        col2_list = data['time'].tolist()
        col3_list = data['mpa'].tolist()

        # 将数据添加到处理后的数据列表中，并包含分组名字
        processed_data.append((group_name, [col2_list, col3_list], colors[i % len(colors)]))

    # 创建图像
    fig, ax = plt.subplots(figsize=(18, 7.5))  # 设置图像大小

    # 主题设置
    plt.style.use('seaborn-darkgrid')

    # 绘制折线图
    for group_name, data, color in processed_data:
        x_values, y_values = data
        ax.plot(x_values, y_values, marker='D', linestyle='-', label=f'mpa: {group_name}', color=color)

    # 设置横坐标和纵坐标标签
    ax.set_xlabel('time(s)')
    ax.set_ylabel('mpa')

    # 设置标题
    ax.set_title('压力xy图',fontproperties=font)

    # 添加图例
    ax.legend()

    # 将图像保存到一个字节缓冲区中
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    # 将图像转换为Base64编码
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return render_template('index.html', image_base64=image_base64)


if __name__ == '__main__':
    app.run(debug=True)
