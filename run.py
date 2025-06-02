import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from App import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 