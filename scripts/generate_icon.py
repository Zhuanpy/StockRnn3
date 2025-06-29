from PIL import Image, ImageDraw, ImageFont
import os

def create_quant_trading_icon():
    # 创建一个512x512的透明背景图片
    size = 512
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制圆形背景
    circle_color = (41, 128, 185, 255)  # 蓝色
    draw.ellipse([(50, 50), (size-50, size-50)], fill=circle_color)
    
    # 绘制K线图
    k_line_color = (255, 255, 255, 255)  # 白色
    # 绘制K线
    draw.rectangle([(150, 200), (180, 300)], fill=k_line_color)  # 实体
    draw.line([(165, 150), (165, 200)], fill=k_line_color, width=2)  # 上影线
    draw.line([(165, 300), (165, 350)], fill=k_line_color, width=2)  # 下影线
    
    # 绘制第二个K线
    draw.rectangle([(250, 150), (280, 250)], fill=k_line_color)  # 实体
    draw.line([(265, 100), (265, 150)], fill=k_line_color, width=2)  # 上影线
    draw.line([(265, 250), (265, 300)], fill=k_line_color, width=2)  # 下影线
    
    # 绘制第三个K线
    draw.rectangle([(350, 250), (380, 350)], fill=k_line_color)  # 实体
    draw.line([(365, 200), (365, 250)], fill=k_line_color, width=2)  # 上影线
    draw.line([(365, 350), (365, 400)], fill=k_line_color, width=2)  # 下影线
    
    # 保存图标
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(project_root, 'static', 'icon.png')
    os.makedirs(os.path.dirname(icon_path), exist_ok=True)
    image.save(icon_path)
    print(f"图标已保存到: {icon_path}")

if __name__ == '__main__':
    create_quant_trading_icon() 