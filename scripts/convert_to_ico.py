from PIL import Image
import os

def convert_png_to_ico():
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 源文件和目标文件路径
    png_path = os.path.join(project_root, 'static', 'icon.png')
    ico_path = os.path.join(project_root, 'static', 'icon.ico')
    
    # 打开PNG图片
    img = Image.open(png_path)
    
    # 转换为ICO格式并保存
    img.save(ico_path, format='ICO')
    print(f"图标已转换为ICO格式并保存到: {ico_path}")

if __name__ == '__main__':
    convert_png_to_ico() 