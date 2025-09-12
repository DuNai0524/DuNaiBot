"""
签到图片生成器
生成美观的签到卡片图片
"""
import io
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import NamedTuple


class SignInData(NamedTuple):
    """签到数据结构"""
    sign_rank: int  # 签到排名
    today_gold: int  # 今日获得金币
    all_gold: int  # 总金币
    sign_times: int  # 累计签到次数
    today_lucky: int  # 今日幸运值


class SignInImageGenerator:
    """签到图片生成器"""
    
    def __init__(self):
        self.width = 600
        self.height = 400
        self.bg_color = (245, 248, 255)  # 浅蓝色背景
        self.primary_color = (74, 144, 226)  # 主色调
        self.text_color = (51, 51, 51)  # 文字颜色
        self.accent_color = (255, 193, 7)  # 强调色（金色）
        self.success_color = (40, 167, 69)  # 成功色（绿色）
        
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """获取字体"""
        try:
            # 尝试使用系统字体
            if bold:
                font_paths = [
                    "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑 Bold
                    "C:/Windows/Fonts/simhei.ttf",  # 黑体
                    "arial.ttf"
                ]
            else:
                font_paths = [
                    "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                    "C:/Windows/Fonts/simsun.ttc",  # 宋体
                    "arial.ttf"
                ]
            
            for font_path in font_paths:
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
                    
            # 如果都失败了，使用默认字体
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def _draw_rounded_rectangle(self, draw: ImageDraw.ImageDraw, 
                              bbox: tuple, fill: tuple, radius: int = 10):
        """绘制圆角矩形"""
        x1, y1, x2, y2 = bbox
        
        # 绘制圆角
        draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
        draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
        draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
        draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)
        
        # 绘制矩形部分
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    
    def _draw_gradient_background(self, draw: ImageDraw.ImageDraw):
        """绘制渐变背景"""
        # 简单的垂直渐变效果
        for y in range(self.height):
            alpha = y / self.height
            color = (
                int(self.bg_color[0] * (1 - alpha) + 235 * alpha),
                int(self.bg_color[1] * (1 - alpha) + 245 * alpha),
                int(self.bg_color[2] * (1 - alpha) + 255 * alpha)
            )
            draw.line([(0, y), (self.width, y)], fill=color)
    
    def generate_sign_in_image(self, data: SignInData) -> io.BytesIO:
        """生成签到图片"""
        # 创建画布
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # 绘制渐变背景
        self._draw_gradient_background(draw)
        
        # 绘制主卡片
        card_margin = 30
        card_bbox = (card_margin, card_margin, 
                    self.width - card_margin, self.height - card_margin)
        self._draw_rounded_rectangle(draw, card_bbox, (255, 255, 255), radius=15)
        
        # 添加阴影效果
        shadow_offset = 3
        shadow_bbox = (card_margin + shadow_offset, card_margin + shadow_offset,
                      self.width - card_margin + shadow_offset, 
                      self.height - card_margin + shadow_offset)
        shadow_img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        self._draw_rounded_rectangle(shadow_draw, shadow_bbox, (0, 0, 0, 30), radius=15)
        
        # 合并阴影
        img = Image.alpha_composite(img.convert('RGBA'), shadow_img).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # 重新绘制主卡片（覆盖阴影）
        self._draw_rounded_rectangle(draw, card_bbox, (255, 255, 255), radius=15)
        
        # 字体设置
        title_font = self._get_font(32, bold=True)
        content_font = self._get_font(20)
        small_font = self._get_font(16)
        
        # 标题
        title = "每日签到成功！"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.width - title_width) // 2
        draw.text((title_x, 60), title, fill=self.primary_color, font=title_font)
        
        # 签到排名标识
        rank_text = f"第 {data.sign_rank} 位"
        rank_bbox = draw.textbbox((0, 0), rank_text, font=content_font)
        rank_width = rank_bbox[2] - rank_bbox[0]
        rank_height = rank_bbox[3] - rank_bbox[1]
        
        # 排名背景
        rank_bg_bbox = (self.width - 120, 45, self.width - 20, 85)
        self._draw_rounded_rectangle(draw, rank_bg_bbox, self.accent_color, radius=8)
        
        # 排名文字
        rank_x = self.width - 70 - rank_width // 2
        rank_y = 65 - rank_height // 2
        draw.text((rank_x, rank_y), rank_text, fill=(255, 255, 255), font=content_font)
        
        # 分割线
        line_y = 110
        draw.line([(60, line_y), (self.width - 60, line_y)], 
                 fill=(230, 230, 230), width=2)
        
        # 数据展示区域
        data_start_y = 140
        line_height = 35
        
        # 今日获得金币
        gold_text = f"获得金币: {data.today_gold}"
        draw.text((80, data_start_y), gold_text, fill=self.success_color, font=content_font)
        
        # 总金币
        total_gold_text = f"现在拥有金币: {data.all_gold}"
        draw.text((80, data_start_y + line_height), total_gold_text, 
                 fill=self.text_color, font=content_font)
        
        # 累计签到次数
        sign_times_text = f"累计签到次数: {data.sign_times}"
        draw.text((80, data_start_y + line_height * 2), sign_times_text, 
                 fill=self.text_color, font=content_font)
        
        # 幸运值（如果有的话）
        if hasattr(data, 'today_lucky') and data.today_lucky:
            lucky_text = f"今日幸运值: {data.today_lucky}"
            draw.text((80, data_start_y + line_height * 3), lucky_text, 
                     fill=self.primary_color, font=content_font)
        
        # 底部装饰
        decoration_y = self.height - 70
        draw.text((80, decoration_y), "感谢您的每日签到！", 
                 fill=(150, 150, 150), font=small_font)
        
        # 右下角小图标（简单的星星）
        star_x, star_y = self.width - 80, self.height - 60
        star_points = [
            (star_x, star_y - 10),
            (star_x + 3, star_y - 3),
            (star_x + 10, star_y - 3),
            (star_x + 5, star_y + 2),
            (star_x + 7, star_y + 10),
            (star_x, star_y + 6),
            (star_x - 7, star_y + 10),
            (star_x - 5, star_y + 2),
            (star_x - 10, star_y - 3),
            (star_x - 3, star_y - 3)
        ]
        draw.polygon(star_points, fill=self.accent_color)
        
        # 保存到内存
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', quality=95)
        img_buffer.seek(0)
        
        return img_buffer


def create_sign_in_image(sign_rank: int, today_gold: int, 
                        all_gold: int, sign_times: int, 
                        today_lucky: int = 0) -> io.BytesIO:
    """
    创建签到图片的便捷函数
    
    Args:
        sign_rank: 签到排名
        today_gold: 今日获得金币
        all_gold: 总金币
        sign_times: 累计签到次数
        today_lucky: 今日幸运值
        
    Returns:
        io.BytesIO: 图片字节流
    """
    data = SignInData(
        sign_rank=sign_rank,
        today_gold=today_gold,
        all_gold=all_gold,
        sign_times=sign_times,
        today_lucky=today_lucky
    )
    
    generator = SignInImageGenerator()
    return generator.generate_sign_in_image(data)