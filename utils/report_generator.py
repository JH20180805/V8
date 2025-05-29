"""
报告生成器
"""
import os
import datetime
from docxtpl import DocxTemplate


class ReportGenerator:
    """报告生成器类"""

    def __init__(self, key, value):
        """初始化报告生成器

        Args:
            templates_dir: 模板目录
        """
        self.key = key
        self.value = value
        self.sample_name = self.key[1]

    def get_template_path(self):
        """根据样品名称获取模板路径

        Args:
            sample_name: 样品名称

        Returns:
            模板路径
        """

        template_path = "./templates/" + self.sample_name + ".docx"
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"模板文件 {template_path} 不存在")

        return template_path

    def generate_report(self):
        """生成试验报告
        Returns:
            生成的报告文件路径
        """
        

        # # 获取模板路径
        template_path = self.get_template_path()
        # print(template_path)
        # print(self.value)

        # # 加载模板
        doc = DocxTemplate(template_path)

        self.value['序号'] = range(1, len(self.value) + 1)
         
        # 准备模板数据
        context = {
            'rows': self.value.to_dict(orient='records'),
            **self.value.iloc[0].to_dict()
        }



        # 渲染模板
        doc.render(context)

        # # 生成报告文件名
        report_name = f"{self.key[0]}_{self.key[1]}_{self.key[2]}试验报告"
        report_path = "./reports/" + report_name + ".docx"

        # # 保存报告
        doc.save(report_path)
        abs_path = os.path.abspath(report_path)
        print(abs_path)
        os.startfile(abs_path)


