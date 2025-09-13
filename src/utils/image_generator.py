"""
签到图片生成器
生成美观的签到卡片图片
"""
import io
import aiohttp
import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from typing import NamedTuple, Optional

from datetime import datetime


class SignInData(NamedTuple):
    """签到数据结构"""
    sign_rank: int  # 签到排名
    today_gold: int  # 今日获得金币
    all_gold: int  # 总金币
    sign_times: int  # 累计签到次数
    today_lucky: int  # 今日幸运值
    user_id: Optional[int] = None  # 用户QQ号


class SignInImageGenerator:
    """签到图片生成器"""
    
    def __init__(self):
        self.width = 720
        self.height = 960
        # 配色方案
        self.card_bg_color = (255, 255, 255, 200)  # 半透明白色卡片
        self.primary_text_color = (80, 80, 80)  # 主要文字颜色
        self.welcome_text_color = (180, 180, 180)  # 欢迎文字颜色
        self.gold_color = (255, 193, 7)  # 金币颜色
        self.rank_color = (76, 175, 80)  # 排名颜色
        self.lucky_color = (233, 30, 99)  # 幸运值颜色
        self.quote_color = (120, 120, 120)  # 一言颜色
        
    async def _download_avatar(self, user_id: int) -> Optional[Image.Image]:
        """下载QQ用户头像"""
        try:
            import aiohttp
            avatar_url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as response:
                    if response.status == 200:
                        avatar_data = await response.read()
                        avatar_img = Image.open(io.BytesIO(avatar_data))
                        return avatar_img
        except Exception as e:
            print(f"下载头像失败: {e}")
        return None
    
    def _create_circular_avatar(self, avatar_img: Image.Image, size: int) -> Image.Image:
        """将头像裁剪为圆形"""
        # 调整头像大小
        avatar_img = avatar_img.resize((size, size), Image.Resampling.LANCZOS)
        
        # 创建圆形遮罩
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size, size), fill=255)
        
        # 创建透明背景的圆形头像
        circular_avatar = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        circular_avatar.paste(avatar_img, (0, 0))
        circular_avatar.putalpha(mask)
        
        return circular_avatar
        
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """获取字体，优先使用项目内的 LXGW Wenkai"""
        try:
            # 获取项目根目录路径
            current_file = Path(__file__)  # src/utils/image_generator.py
            project_root = current_file.parent.parent.parent  # 回到项目根目录
            font_dir = project_root / "asserts" / "fonts"

            font_paths = [
                str(font_dir / "LXGWWenKai-Regular.ttf"),
                str(font_dir / "LXGWWenKai-Medium.ttf"),
                str(font_dir / "LXGWWenKai-Light.ttf"),
                # 兼容原有字体作为备选
                "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/simsun.ttc",
                "arial.ttf"
            ]

            for font_path in font_paths:
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception:
                    continue
            return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()
    
    async def _create_background(self) -> Image.Image:
        """创建背景，使用随机图片API"""
        try:
            # 下载随机背景图片
            async with aiohttp.ClientSession() as session:
                async with session.get("https://t.alcy.cc/mp") as response:
                    if response.status == 200:
                        img_data = await response.read()
                        bg = Image.open(io.BytesIO(img_data))

                        # 调整图片大小以适应画布
                        bg = bg.resize((self.width, self.height), Image.Resampling.LANCZOS)

                        # 转换为RGB模式（如果不是的话）
                        if bg.mode != 'RGB':
                            bg = bg.convert('RGB')

                        # 添加轻微的模糊效果，使背景不会干扰前景内容
                        bg = bg.filter(ImageFilter.GaussianBlur(radius=3))

                        return bg
        except Exception as e:
            print(f"下载背景图片失败: {e}")

        # 如果下载失败，使用原来的渐变背景作为备选
        bg = Image.new('RGB', (self.width, self.height), (240, 220, 200))
        
        # 添加一些装饰性元素来模拟动漫背景
        draw = ImageDraw.Draw(bg)
        
        # 绘制一些几何图形作为装饰
        for i in range(5):
            x = (i * 120 + 50) % self.width
            y = (i * 80 + 30) % self.height
            size = 40 + i * 10
            color = (220 + i * 5, 200 + i * 8, 180 + i * 6)
            draw.ellipse([x, y, x + size, y + size], fill=color)
        
        # 添加模糊效果（简化版）
        return bg.filter(ImageFilter.GaussianBlur(radius=2))
    
    def _draw_semi_transparent_card(self, bg_img: Image.Image) -> Image.Image:
        """绘制半透明卡片"""
        # 创建RGBA图像以支持透明度
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 卡片尺寸和位置
        card_width = 540
        card_height = 720
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2
        
        # 绘制半透明卡片
        self._draw_rounded_rectangle_rgba(
            draw, 
            (card_x, card_y, card_x + card_width, card_y + card_height),
            self.card_bg_color, 
            radius=20
        )
        
        # 合并背景和半透明卡片
        result = Image.alpha_composite(bg_img.convert('RGBA'), overlay)
        return result.convert('RGB')
    
    def _draw_rounded_rectangle_rgba(self, draw: ImageDraw.ImageDraw, 
                                   bbox: tuple, fill: tuple, radius: int = 10):
        """绘制带透明度的圆角矩形"""
        x1, y1, x2, y2 = bbox
        
        # 绘制圆角
        draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
        draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
        draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
        draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)
        
        # 绘制矩形部分
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

    async def generate_sign_in_image(self, data: SignInData, yiyan: str, user_name: str) -> io.BytesIO:
        """生成签到图片 - 仿照参考布局"""
        # 创建背景
        bg_img = await self._create_background()

        # 绘制半透明卡片
        img = self._draw_semi_transparent_card(bg_img)
        draw = ImageDraw.Draw(img)
        
        # 字体设置
        title_font = self._get_font(32, bold=True)
        subtitle_font = self._get_font(28)
        content_font = self._get_font(24)
        small_font = self._get_font(18)
        tiny_font = self._get_font(16)
        
        # 头像设置
        avatar_size = 120
        avatar_x = (self.width - avatar_size) // 2
        avatar_y = 160
        
        # 绘制头像
        if data.user_id:
            avatar_img = await self._download_avatar(data.user_id)
            if avatar_img:
                circular_avatar = self._create_circular_avatar(avatar_img, avatar_size)
                
                # 转换为RGBA模式进行合成
                img_rgba = img.convert('RGBA')
                
                # 绘制头像白色边框
                border_size = avatar_size + 12
                border_x = avatar_x - 6
                border_y = avatar_y - 6
                border_draw = ImageDraw.Draw(img_rgba)
                border_draw.ellipse((border_x, border_y, border_x + border_size, border_y + border_size), 
                                  fill=(255, 255, 255, 255))
                
                # 粘贴圆形头像
                img_rgba.paste(circular_avatar, (avatar_x, avatar_y), circular_avatar)
                img = img_rgba.convert('RGB')
                draw = ImageDraw.Draw(img)
            else:
                # 默认头像
                self._draw_default_avatar(draw, avatar_x, avatar_y, avatar_size)
        else:
            # 默认头像
            self._draw_default_avatar(draw, avatar_x, avatar_y, avatar_size)
        
        # 时间问候语
        now_time = datetime.now()
        if 5 <= now_time.hour < 12:
            welcome_text = "早上好，欢迎回来！"
        elif 12 <= now_time.hour < 18:
            welcome_text = "下午好，欢迎回来！"
        else:
            welcome_text = "晚上好，欢迎回来！"
            
        welcome_bbox = draw.textbbox((0, 0), welcome_text, font=title_font)
        welcome_width = welcome_bbox[2] - welcome_bbox[0]
        welcome_x = (self.width - welcome_width) // 2
        welcome_y = avatar_y + avatar_size + 30
        draw.text((welcome_x, welcome_y), welcome_text, fill=self.welcome_text_color, font=title_font)
        
        # 签到成功提示
        sign_success_text = user_name
        sign_bbox = draw.textbbox((0, 0), sign_success_text, font=subtitle_font)
        sign_width = sign_bbox[2] - sign_bbox[0]
        sign_x = (self.width - sign_width) // 2
        sign_y = welcome_y + 50
        draw.text((sign_x, sign_y), sign_success_text, fill=self.primary_text_color, font=subtitle_font)
        
        # 今日获得金币信息
        gold_gain_text = f"获得金币 + {data.today_gold}!"
        total_gold_text = f"/ 现在拥有金币: {data.all_gold}"
        
        # 今日获得金币 (较大字体，橙色)
        gold_gain_bbox = draw.textbbox((0, 0), gold_gain_text, font=subtitle_font)
        gold_gain_width = gold_gain_bbox[2] - gold_gain_bbox[0]
        
        # 当前总金币 (较小字体，灰色)
        total_gold_bbox = draw.textbbox((0, 0), total_gold_text, font=content_font)
        total_gold_width = total_gold_bbox[2] - total_gold_bbox[0]
        
        # 计算居中位置
        total_width = gold_gain_width + total_gold_width + 20
        start_x = (self.width - total_width) // 2
        gold_y = sign_y + 60
        
        draw.text((start_x, gold_y), gold_gain_text, fill=self.gold_color, font=subtitle_font)
        draw.text((start_x + gold_gain_width + 20, gold_y + 5), total_gold_text, fill=self.primary_text_color, font=content_font)
        
        # 签到排名
        rank_text = f"今日排名: 第 {data.sign_rank} 位"
        rank_bbox = draw.textbbox((0, 0), rank_text, font=content_font)
        rank_width = rank_bbox[2] - rank_bbox[0]
        rank_x = (self.width - rank_width) // 2
        rank_y = gold_y + 70
        draw.text((rank_x, rank_y), rank_text, fill=self.rank_color, font=content_font)
        
        # 累计签到次数
        sign_times_text = f"累计签到次数: {data.sign_times}"
        times_bbox = draw.textbbox((0, 0), sign_times_text, font=small_font)
        times_width = times_bbox[2] - times_bbox[0]
        times_x = (self.width - times_width) // 2
        times_y = rank_y + 50
        draw.text((times_x, times_y), sign_times_text, fill=self.primary_text_color, font=small_font)
        
        # 幸运值信息
        if hasattr(data, 'today_lucky') and data.today_lucky:
            lucky_text = f"今日幸运值: {data.today_lucky}"
            lucky_bbox = draw.textbbox((0, 0), lucky_text, font=small_font)
            lucky_width = lucky_bbox[2] - lucky_bbox[0]
            lucky_x = (self.width - lucky_width) // 2
            lucky_y = times_y + 40
            draw.text((lucky_x, lucky_y), lucky_text, fill=self.lucky_color, font=small_font)
            next_y = lucky_y + 80
        else:
            next_y = times_y + 80
        
        # 感谢文字
        thanks_text = yiyan
        thanks_bbox = draw.textbbox((0, 0), thanks_text, font=content_font)
        thanks_width = thanks_bbox[2] - thanks_bbox[0]
        thanks_x = (self.width - thanks_width) // 2
        draw.text((thanks_x, next_y), thanks_text, fill=self.quote_color, font=content_font)

        # 底部生成标识（使用黑体字体）
        generate_text = "Generated by DuNaiBot, designed with Claude Sonnet 4"
        heiti_font = self._get_font(16)  # 使用黑体（加粗）字体
        generate_bbox = draw.textbbox((0, 0), generate_text, font=heiti_font)
        generate_width = generate_bbox[2] - generate_bbox[0]
        generate_x = (self.width - generate_width) // 2
        generate_y = self.height - 50
        draw.text((generate_x, generate_y), generate_text, fill=(0, 0, 0), font=heiti_font)
        
        # 保存到内存
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', quality=95)
        img_buffer.seek(0)
        
        return img_buffer
    
    def _draw_default_avatar(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int):
        """绘制默认头像"""
        # 白色边框
        border_size = size + 12
        border_x = x - 6
        border_y = y - 6
        draw.ellipse((border_x, border_y, border_x + border_size, border_y + border_size), 
                   fill=(255, 255, 255))
        
        # 头像背景
        draw.ellipse((x, y, x + size, y + size), fill=(200, 200, 200))
        
        # 用户图标
        icon_font = self._get_font(size // 3)
        icon_x = x + size // 2 - size // 6
        icon_y = y + size // 2 - size // 6
        draw.text((icon_x, icon_y), "👤", fill=(255, 255, 255), font=icon_font)
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
        """文字换行"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " " if current_line else word
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines


async def create_sign_in_image(sign_rank: int, today_gold: int, 
                        all_gold: int, sign_times: int, 
                        today_lucky: int = 0, user_id: Optional[int] = None, yiyan: str = "", user_name: str = "") -> io.BytesIO:
    """
    创建签到图片的便捷函数
    
    Args:
        sign_rank: 签到排名
        today_gold: 今日获得金币
        all_gold: 总金币
        sign_times: 累计签到次数
        today_lucky: 今日幸运值
        user_id: 用户QQ号
        
    Returns:
        io.BytesIO: 图片字节流
    """
    data = SignInData(
        sign_rank=sign_rank,
        today_gold=today_gold,
        all_gold=all_gold,
        sign_times=sign_times,
        today_lucky=today_lucky,
        user_id=user_id
    )
    
    generator = SignInImageGenerator()
    return await generator.generate_sign_in_image(data, yiyan, user_name)


def create_sign_in_image_sync(sign_rank: int, today_gold: int, 
                        all_gold: int, sign_times: int, 
                        today_lucky: int = 0, user_id: Optional[int] = None) -> io.BytesIO:
    """
    创建签到图片的同步版本（兼容旧代码）
    
    Args:
        sign_rank: 签到排名
        today_gold: 今日获得金币
        all_gold: 总金币
        sign_times: 累计签到次数
        today_lucky: 今日幸运值
        user_id: 用户QQ号
        
    Returns:
        io.BytesIO: 图片字节流
    """
    return asyncio.run(create_sign_in_image(
        sign_rank=sign_rank,
        today_gold=today_gold,
        all_gold=all_gold,
        sign_times=sign_times,
        today_lucky=today_lucky,
        user_id=user_id
    ))