#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################
#                     version 1.2                      #
########################################################
# window
import tkinter as tk
from tkinter import INSERT
from tkinter import messagebox, filedialog
# Image Processing
from PIL import ImageTk, Image, ImageGrab
# OCR
import pyperclip
from time import sleep
# clipboard
import pytesseract as pytesseract
import noteshrink as noteshrink
# HD screenshot
import win32api
import win32con
import win32gui
import win32ui
# baidu ocr
from aip import AipOcr
# config
from configparser import ConfigParser


def window_capture():
    #  窗口的编号，0号表示当前活跃窗口
    hwnd = 0
    # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
    hwndDC = win32gui.GetWindowDC(hwnd)
    # 根据窗口的DC获取mfcDC
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    # mfcDC创建可兼容的DC
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建bigmap准备保存图片
    saveBitMap = win32ui.CreateBitmap()
    # 获取监控器信息
    MoniterDev = win32api.EnumDisplayMonitors(None, None)
    w = MoniterDev[0][2][2]
    h = MoniterDev[0][2][3]
    # print w,h　　　#图片大小
    # 为bitmap开辟空间
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    # 高度saveDC，将截图保存到saveBitmap中
    saveDC.SelectObject(saveBitMap)
    # 截取从左上角（0，0）长宽为（w，h）的图片
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
    # saveBitMap.SaveBitmapFile(saveDC, filename)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    #saveBitMap.SaveBitmapFile(saveDC, "C:\\Users\\ke_yi\\Desktop\\temp.png")
    return Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)


class FullScreen:
    def __init__(self, full_screen_img):
        # 变量X和Y用来记录鼠标左键按下的位置
        self.X = tk.IntVar(value=0)
        self.Y = tk.IntVar(value=0)
        self.selectPosition = None
        # 屏幕尺寸
        screenWidth = window.winfo_screenwidth()
        screenHeight = window.winfo_screenheight()
        # 创建顶级组件容器
        self.top = tk.Toplevel(window, width=screenWidth, height=screenHeight)
        # 不显示最大化、最小化按钮
        self.top.overrideredirect(True)
        self.canvas = tk.Canvas(self.top, bg='white', width=screenWidth, height=screenHeight)
        # 显示全屏截图，在全屏截图上进行区域截图
        self.p_w_picpath = full_screen_img
        self.p_w_picpath = ImageTk.PhotoImage(self.p_w_picpath)
        self.canvas.create_image(screenWidth // 2, screenHeight // 2, image=self.p_w_picpath)

        # 鼠标左键按下的位置
        def onLeftButtonDown(event):
            self.X.set(event.x)
            self.Y.set(event.y)
            # 开始截图
            self.sel = True

        self.canvas.bind('<Button-1>', onLeftButtonDown)

        # 鼠标左键移动，显示选取的区域
        def onLeftButtonMove(event):
            if not self.sel:
                return
            global lastDraw
            try:
                # 删除刚画完的图形，要不然鼠标移动的时候是黑乎乎的一片矩形
                self.canvas.delete(lastDraw)
            except Exception:
                pass
            lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y, outline='black')

        self.canvas.bind('<B1-Motion>', onLeftButtonMove)

        # 获取鼠标左键抬起的位置，保存区域截图
        def onLeftButtonUp(event):
            global pic
            from io import BytesIO
            self.sel = False
            try:
                self.canvas.delete(lastDraw)
            except Exception as e:
                pass
            sleep(0.1)
            # 考虑鼠标左键从右下方按下而从左上方抬起的截图
            myleft, myright = sorted([self.X.get(), event.x])
            mytop, mybottom = sorted([self.Y.get(), event.y])
            self.selectPosition = (myleft, myright, mytop, mybottom)
            pic_img = ImageGrab.grab((myleft + 1, mytop + 1, myright, mybottom))
            # 识别文字
            b = BytesIO()
            pic_img.save(b, format="jpeg")
            pic = Image.open(b)
            # 关闭当前窗口
            self.top.destroy()
            # 识别内容
            import time
            global ocr_word
            print('start deal with pic')
            time_start = time.time()
            lang = "eng" + lang_g
            global var3
            if not customize_lang.get() == '' and var3.get() == 1:
                lang += '+'+customize_lang.get()
            print(lang)

            try:
                noteshrink.notescan_main(pic)
            except Exception as e:
                messagebox.showinfo(title='提示', message=e)
            global tool_g
            if tool_g.get() == 1:
                """ 你的 APPID AK SK """
                cfg = ConfigParser()
                cfg.read('config.ini')
                cfg.sections()
                APP_ID = cfg.get('application', 'APP_ID')
                API_KEY = cfg.get('application', 'API_KEY')
                SECRET_KEY = cfg.get('application', 'SECRET_KEY')
                """ 如果有可选参数 """
                options = {}
                options["language_type"] = "CHN_ENG"
                options["detect_direction"] = "true"
                options["detect_language"] = "true"
                options["probability"] = "false"

                try:
                    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
                    """ 调用通用文字识别, 图片参数为本地图片 """
                    words_result = client.basicGeneral(b.getvalue(), options)['words_result']
                    ocr_word = ''
                    for word_result in words_result:
                        ocr_word += word_result['words']
                except BaseException as e:
                    messagebox.showinfo(title='提示', message='识别失败，请确认百度文字识别认证信息！')
                    ocr_word = '识别失败'
            elif tool_g.get() == 0:
                try:
                    ocr_word = pytesseract.image_to_string(pic, lang=lang)
                    ocr_word = ocr_word[:-1]
                except BaseException as e:
                    messagebox.showinfo(title='提示', message=e)
            time_end = time.time()
            print('get ocr_word by pic of time cost', time_end - time_start, 's')
            l1['state'] = 'normal'
            l1.delete('0.0', 'end')
            l1.insert('end', ocr_word)
            l1['state'] = 'disabled'
            # t2.delete('0.0', 'end')
            t2.insert(INSERT, ocr_word)

        self.canvas.bind('<ButtonRelease-1>', onLeftButtonUp)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)


def save_pic():
    try:
        type(pic)
        # 弹出保存截图对话框
        file_name = filedialog.asksaveasfilename(title='保存截图', filetypes=[('JPG files', '*.jpg')])
        if file_name:
            pic.save(file_name + '.jpg')
    except NameError:
        messagebox.showinfo(title='提示', message='请先新建截图！')


def buttonCaptureClick():
    # 最小化主窗口
    window.state('icon')
    sleep(0.2)
    filename = 'temp.png'
    full_screen_img = window_capture()
    # 显示全屏幕截图
    w = FullScreen(full_screen_img)
    buttonCapture.wait_window(w.top)
    # 截图结束，恢复主窗口，并删除临时的全屏幕截图文件
    window.state('normal')


if __name__ == '__main__':
    # 第1步，实例化object，建立窗口window
    window = tk.Tk()

    # 第2步，给窗口的可视化起名字
    window.title('SCREEN OCR BY KE_YI_')

    # 第3步，设定窗口的大小(长 * 宽)
    window.geometry('500x320')

    global lang_g
    lang_g = ''


    def check_chi_sim():
        global lang_g
        if var1.get() == 1:
            lang_g += '+chi_sim'
        else:
            lang_g = lang_g.replace('+chi_sim', '')


    def check_jpn():
        global lang_g
        if var2.get() == 1:
            lang_g += '+jpn'
        else:
            lang_g = lang_g.replace('+jpn', '')

    # 第5步，定义Checkbutton选项并放置
    var1 = tk.IntVar()  # 定义var1和var2整型变量用来存放选择行为返回值
    var2 = tk.IntVar()
    global var3
    var3 = tk.IntVar()
    global customize_lang
    customize_lang = tk.StringVar()
    global tool_g
    tool_g = tk.IntVar()
    c1 = tk.Checkbutton(window, text='百度', variable=tool_g, onvalue=1, offvalue=0)
    c1.place(x=6, y=5)
    tk.Label(window, text='选择语言：').place(x=70, y=6)

    c2 = tk.Checkbutton(window, text='中文', variable=var1, onvalue=1, offvalue=0, command=check_chi_sim)
    c2.place(x=130, y=5)
    c3 = tk.Checkbutton(window, text='日文', variable=var2, onvalue=1, offvalue=0, command=check_jpn)
    c3.place(x=190, y=5)
    c4 = tk.Checkbutton(window, variable=var3, onvalue=1, offvalue=0)
    c4.place(x=250, y=5)
    e = tk.Entry(window, textvariable=customize_lang, show=None, font=('Arial', 10), bd='0', bg='#f0f0f0')
    e.place(x=275, y=9)

    # 第7步，创建并放置一个多行文本框text用以显示，指定height=3为文本框是三个字符高度
    l1 = tk.Text(window, width=60, height=10, state='disabled')
    l1.place(x=10, y=30)
    # 第7步，创建并放置一个多行文本框text用以显示，指定height=3为文本框是三个字符高度
    t2 = tk.Text(window, width=60, height=10)
    t2.place(x=10, y=175)


    def view():
        try:
            type(pic)
            top1 = tk.Toplevel()
            img = ImageTk.PhotoImage(pic)
            canvas = tk.Canvas(top1, width=pic.width, height=pic.height, bg='white')
            canvas.create_image(0, 0, image=img, anchor="nw")
            canvas.pack()
            top1.mainloop()
        except NameError:
            messagebox.showinfo(title='提示', message='请先新建截图！')


    bb2 = tk.Button(window, text='查看', width=6, height=1, command=view)
    bb2.place(x=441, y=30)
    buttonCapture = tk.Button(window, text='新建', width=6, height=1, command=buttonCaptureClick)
    buttonCapture.place(x=441, y=65)
    bb3 = tk.Button(window, text='保存', width=6, height=1, command=save_pic)
    bb3.place(x=441, y=100)


    def reset():
        try:
            type(ocr_word)
            t2.delete('0.0', 'end')
            t2.insert('end', ocr_word)
        except NameError:
            messagebox.showinfo(title='提示', message='请先新建截图！')


    b2 = tk.Button(window, text='重置', width=6, height=1, command=reset)
    b2.place(x=441, y=175)


    def clear():
        t2.delete("0.0", "end")


    b3 = tk.Button(window, text='清空', width=6, height=1, command=clear)
    b3.place(x=441, y=210)


    def copy():
        pyperclip.copy(t2.get('0.0', 'end'))


    b4 = tk.Button(window, text='复制', width=6, height=1, command=copy)
    b4.place(x=441, y=245)
    # 第12步，主窗口循环显示
    window.mainloop()
