import tkinter as tk

# 创建主窗口
root = tk.Tk()
root.title("股票应用程序")


class Myfunction:

    # 定义按钮点击事件处理函数
    @classmethod
    def button1_click(cls):
        print("按钮1被点击")

    @classmethod
    def button2_click(cls):
        print("按钮2被点击")

    @classmethod
    def button3_click(cls):
        print("按钮3被点击")

    @classmethod
    def button4_click(cls):
        print("按钮4被点击")

    @classmethod
    def button5_click(cls):
        print("按钮5被点击")

    @classmethod
    def button6_click(cls):
        print("按钮6被点击")

    @classmethod
    def button7_click(cls):
        print("按钮7被点击")

    @classmethod
    def button8_click(cls):
        print("按钮8被点击")

    @classmethod
    def button9_click(cls):
        print("按钮9被点击")

    @classmethod
    def button10_click(cls):
        print("按钮10被点击")

    @classmethod
    def button11_click(cls):
        print("按钮11被点击")

    @classmethod
    def button12_click(cls):
        print("按钮12被点击")

    @classmethod
    def button13_click(cls):
        print("按钮13被点击")

    @classmethod
    def button14_click(cls):
        print("按钮14被点击")

    @classmethod
    def button15_click(cls):
        print("按钮15被点击")

    @classmethod
    def button16_click(cls):
        print("按钮16被点击")

    @classmethod
    def button17_click(cls):
        print("按钮17被点击")

    @classmethod
    def button18_click(cls):
        print("按钮18被点击")

    @classmethod
    def button19_click(cls):
        print("按钮19被点击")

    @classmethod
    def button20_click(cls):
        print("按钮20被点击")

    @classmethod
    def button21_click(cls):
        print("按钮21被点击")

    @classmethod
    def button22_click(cls):
        print("按钮22被点击")

    @classmethod
    def button23_click(cls):
        print("按钮23被点击")

    @classmethod
    def button24_click(cls):
        print("按钮24被点击")

    @classmethod
    def button25_click(cls):
        print("按钮25被点击")

    @classmethod
    def button26_click(cls):
        print("按钮26被点击")

    @classmethod
    def button27_click(cls):
        print("按钮27被点击")

    @classmethod
    def button28_click(cls):
        print("按钮28被点击")

    @classmethod
    def button29_click(cls):
        print("按钮129被点击")

    @classmethod
    def button30_click(cls):
        print("按钮30被点击")


# ...定义其他按钮的点击事件处理函数...

# 创建导航栏
nav_bar = tk.Frame(root, bg="blue", height=30)
nav_bar.pack(fill=tk.X)

# 创建区域1
frame1 = tk.Frame(root, borderwidth=2, relief="solid")
label1 = tk.Label(frame1, text="股票日常运行", font=("Helvetica", 14))
frame1.pack(side=tk.TOP, padx=10, pady=10)
label1.pack()

# 创建按钮1
button_names1 = ["按钮01", "按钮02", "按钮03", "按钮04", "按钮05", "按钮06", "按钮07", "按钮08", "按钮09", "按钮10"]

for i in range(2):
    button_row = tk.Frame(frame1)
    button_row.pack()
    for j in range(5):
        idx = i * 5 + j
        if idx < len(button_names1):
            button = tk.Button(button_row, text=button_names1[idx], command=eval(f'Myfunction.button{idx + 1}_click'))
            button.pack(side=tk.LEFT, padx=5, pady=5)

# 创建区域2
frame2 = tk.Frame(root, borderwidth=2, relief="solid")
label2 = tk.Label(frame2, text="股票模拟交易", font=("Helvetica", 14))
frame2.pack(side=tk.TOP, padx=10, pady=10)
label2.pack()

# 创建按钮2
button_names2 = ["按钮11", "按钮12", "按钮13", "按钮14", "按钮15", "按钮16", "按钮17", "按钮18", "按钮19", "按钮20"]
for i in range(2):
    # print(i)
    button_row = tk.Frame(frame2)
    button_row.pack()
    for j in range(5):
        idx = i * 5 + j
        bdx = 11 + idx
        if idx < len(button_names2):
            button = tk.Button(button_row, text=button_names2[idx], command=eval(f'Myfunction.button{bdx}_click'))
            button.pack(side=tk.LEFT, padx=5, pady=5)

# 创建区域3
frame3 = tk.Frame(root, borderwidth=2, relief="solid")
label3 = tk.Label(frame3, text="股票数据绘图", font=("Helvetica", 14))
frame3.pack(side=tk.TOP, padx=10, pady=10)
label3.pack()

# 创建按钮3
button_names3 = ["按钮21", "按钮22", "按钮23", "按钮24", "按钮25", "按钮26", "按钮27", "按钮28", "按钮29", "按钮30"]
for i in range(2):
    button_row = tk.Frame(frame3)
    button_row.pack()
    for j in range(5):
        idx = i * 5 + j
        bdx = 21 + idx
        if idx < len(button_names3):
            button = tk.Button(button_row, text=button_names3[idx], command=eval(f'Myfunction.button{bdx}_click'))
            button.pack(side=tk.LEFT, padx=5, pady=5)

# 启动主循环
root.mainloop()
