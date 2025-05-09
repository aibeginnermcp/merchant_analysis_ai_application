from fpdf import FPDF
import os

def test_chinese_pdf():
    # 创建PDF对象
    pdf = FPDF()
    pdf.add_page()
    
    # 使用Arial Unicode MS字体（macOS系统自带）
    pdf.add_font("Arial Unicode MS", fname="/Library/Fonts/Arial Unicode.ttf", uni=True)
    pdf.set_font("Arial Unicode MS", size=16)
    
    # 添加中文测试文本
    pdf.cell(0, 10, '中文字体测试', align='C')
    pdf.ln(20)
    
    pdf.set_font_size(12)
    pdf.multi_cell(0, 10, '这是一段测试文字，用于验证PDF中的中文显示是否正常。\n包含一些常用汉字：你好世界！')
    
    # 保存PDF
    pdf.output('test_chinese.pdf')

if __name__ == '__main__':
    test_chinese_pdf() 