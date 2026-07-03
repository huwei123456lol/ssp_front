import os
import base64
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatTongyi
from dotenv import load_dotenv
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

# 加载环境变量
load_dotenv()

class ImageProcessor:
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # 如果没有API Key，仅警告，不抛出异常，允许使用本地功能
            print("警告: 未检测到 DASHSCOPE_API_KEY 或 OPENAI_API_KEY。多模态识别功能将不可用。")
            self.api_key = None
        
        # 初始化多模态模型 (Qwen-VL) 用于识别图片类型
        if self.api_key:
            try:
                self.vl_model = ChatTongyi(
                    model_name="qwen-vl-max", 
                    dashscope_api_key=self.api_key
                )
            except Exception as e:
                print(f"初始化 VL 模型失败: {e}")
                self.vl_model = None
        else:
            self.vl_model = None

    def _ensure_valid_ext(self, path: str, default_ext: str = ".png") -> str:
        """
        确保文件路径有一个受支持的扩展名。
        OpenCV imwrite 支持: .jpg, .jpeg, .png, .bmp, .tiff, .webp
        """
        supported_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        _, ext = os.path.splitext(path)
        if ext.lower() not in supported_exts:
            new_path = os.path.splitext(path)[0] + default_ext
            print(f"注意: 原始扩展名 '{ext}' 不受支持，已更改为 '{default_ext}'。路径: {new_path}")
            return new_path
        return path

    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片转换为 Base64 编码"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def identify_image_type(self, image_path: str) -> str:
        """
        使用多模态 LLM 识别图片类型
        """
        if not self.api_key or not self.vl_model:
            return "{\"type\": \"unknown\", \"has_watermark\": false, \"quality\": \"unknown\", \"error\": \"No API Key\"}"

        print(f"正在识别图片类型: {image_path}")
        prompt_template = """
        你是一个专业的图像分析助手。请分析这张图片，并告诉我：
        1. 图片的主要类型（例如：风景、人像、文档、截图、插画等）
        2. 图片中是否包含明显的水印？如果有，请描述水印的位置和内容。
        3. 图片的清晰度如何？（模糊、一般、清晰）
        
        请以 JSON 格式返回结果，例如：
        {{
            "type": "风景",
            "has_watermark": true,
            "watermark_description": "右下角有白色文字水印",
            "quality": "一般"
        }}
        """
        
        try:
            from dashscope import MultiModalConversation
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": f"file://{os.path.abspath(image_path)}"}, 
                        {"text": prompt_template}
                    ]
                }
            ]
            
            response = MultiModalConversation.call(
                model='qwen-vl-max',
                messages=messages,
                api_key=self.api_key
            )
            
            if response.status_code == 200:
                result = response.output.choices[0].message.content[0]['text']
                return result
            else:
                return f"Error: {response.code} - {response.message}"
        except Exception as e:
            return f"Exception during identification: {str(e)}"

    def remove_watermark_placeholder(self, image_path: str, output_path: str):
        """去水印功能占位符 (目前仅复制图片，可扩展为实际去水印算法)"""
        print(f"正在尝试去水印: {image_path} -> {output_path}")
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"无法读取图片: {image_path}")
        
        output_path = self._ensure_valid_ext(output_path, ".jpg")
        cv2.imwrite(output_path, img)
        return output_path

    def enhance_clarity_placeholder(self, image_path: str, output_path: str):
        """增强清晰度功能占位符 (使用锐化滤镜)"""
        print(f"正在增强清晰度: {image_path} -> {output_path}")
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"无法读取图片: {image_path}")
        
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(img, -1, kernel)
        
        output_path = self._ensure_valid_ext(output_path, ".jpg")
        cv2.imwrite(output_path, sharpened)
        return output_path

    def add_artistic_text(self, image_path: str, output_path: str, text: str = "TEST"):
        """
        使用 PIL 在图片上添加艺术字（大写、加粗、带描边）
        """
        print(f"正在添加艺术字: '{text}' 到 {output_path}")
        
        # 1. 使用 PIL 打开图片
        try:
            pil_img = Image.open(image_path).convert("RGBA")
        except Exception as e:
            raise FileNotFoundError(f"无法读取图片用于添加文字: {image_path}, Error: {str(e)}")
            
        draw = ImageDraw.Draw(pil_img)
        
        # 2. 设置字体
        font_size = max(20, pil_img.size[1] // 15) # 动态字体大小
        font = None
        font_paths = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc", # 微软雅黑
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", # Linux
            "/System/Library/Fonts/Helvetica.ttc" # macOS
        ]
        
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    font = ImageFont.truetype(fp, font_size)
                    break
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
            print("警告: 未找到指定字体文件，使用默认字体。")

        # 3. 获取文字尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        img_width, img_height = pil_img.size
        
        # 4. 计算位置 (腰部位置)
        waist_ratio = 0.75 
        x = (img_width - text_width) / 2
        y = (img_height * waist_ratio) - (text_height / 2)

        # 边界检查
        if y < 0: y = 10
        if y + text_height > img_height: y = img_height - text_height - 10

        # 5. 绘制描边和主体
        outline_color = (0, 0, 0, 255) 
        fill_color = (255, 255, 255, 255) 
        offset = 2
        
        for dx in [-offset, offset]:
            for dy in [-offset, offset]:
                draw.text((x + dx, y + dy), text.upper(), font=font, fill=outline_color)
        
        draw.text((x, y), text.upper(), font=font, fill=fill_color)

        # 6. 转换回 OpenCV 格式并保存
        cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGR)
        
        output_path = self._ensure_valid_ext(output_path, ".png")
        success = cv2.imwrite(output_path, cv2_img)
        if not success:
            raise IOError(f"OpenCV 无法保存图片到: {output_path}")
            
        return output_path

    def change_white_to_black(self, image_path: str, output_path: str):
        """
        将图片中的白色区域（近似衣服）替换为黑色
        使用 HSV 颜色空间进行阈值分割
        """
        print(f"正在将白色衣物替换为黑色 (HSV方法): {image_path} -> {output_path}")
        
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"无法读取图片: {image_path}")
            
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 定义白色的 HSV 范围
        lower_white = np.array([0, 0, 150], dtype=np.uint8)
        upper_white = np.array([180, 30, 255], dtype=np.uint8)
        
        mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # 形态学操作优化掩膜
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.dilate(mask, kernel, iterations=1)

        # 处理颜色替换
        indices = np.where(mask > 0)
        hsv_result = hsv.copy()
        hsv_result[indices[0], indices[1], 2] = 30 # 变黑
        hsv_result[indices[0], indices[1], 1] = np.clip(hsv_result[indices[0], indices[1], 1] + 10, 0, 255)
        
        result_img = cv2.cvtColor(hsv_result, cv2.COLOR_HSV2BGR)

        output_path = self._ensure_valid_ext(output_path, ".jpg")
        success = cv2.imwrite(output_path, result_img)
        if not success:
            raise IOError(f"OpenCV 无法保存图片到: {output_path}")
            
        return output_path
    
    def change_clothes_color_pytorch(self, image_path: str, output_path: str, target_color=(0, 0, 0)):
        """
        使用 PyTorch DeepLabV3 识别人物并替换衣服颜色
        """
        print(f"正在使用 PyTorch 进行智能换色: {image_path}")
        
        try:
            import torch
            import torchvision.transforms as T
            from torchvision.models.segmentation import deeplabv3_resnet50, DeepLabV3_ResNet50_Weights
        except ImportError:
            raise ImportError("请安装 torch 和 torchvision: pip install torch torchvision")

        # 1. 加载预训练模型
        # 【修改点】使用 weights 参数替代 pretrained=True
        weights = DeepLabV3_ResNet50_Weights.DEFAULT
        model = deeplabv3_resnet50(weights=weights)
        model.eval()
        
        # 2. 读取图片
        original_img = Image.open(image_path).convert("RGB")
        input_size = (520, 520)
        
        # 3. 预处理
        # 注意：如果使用 DEFAULT weights，可能需要检查具体的 transform 要求
        # 通常 DEFAULT weights 对应的 preprocess 包含在 weights.transforms() 中
        # 这里为了保持简单且兼容，我们手动构建 transform，但使用 weights 推荐的均值和方差
        preprocess = weights.transforms()
        
        # 由于 weights.transforms() 可能包含 Resize 等逻辑，我们尽量复用或手动对齐
        # 这里保留原有的手动 transform 逻辑以确保输入尺寸可控，但更新均值方差为 DEFAULT 推荐值
        # 如果报错维度不匹配，可以改用: input_tensor = preprocess(original_img).unsqueeze(0)
        
        transform = T.Compose([
            T.Resize(input_size),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        input_tensor = transform(original_img)
        input_batch = input_tensor.unsqueeze(0) 

        # 4. 推理
        with torch.no_grad():
            output = model(input_batch)['out'][0]
        
        # 5. 获取预测结果 (Class 1 is person)
        person_mask = output[1].argmax(dim=0).numpy() 
        
        # 将掩膜 resize 回原图大小
        person_mask_img = Image.fromarray((person_mask * 255).astype(np.uint8))
        person_mask_resized = person_mask_img.resize(original_img.size, Image.NEAREST)
        person_mask_array = np.array(person_mask_resized) > 0
        
        # 6. 简单的肤色检测以排除脸和手
        img_np = np.array(original_img)
        hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
        
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin) > 0
        
        # 最终掩膜：是人 且 不是肤色
        final_mask = person_mask_array & ~skin_mask
        
        # 7. 应用颜色替换
        result_img = img_np.copy()
        r, g, b = target_color 
        result_img[final_mask] = [r, g, b]
        
        # 8. 保存
        output_path = self._ensure_valid_ext(output_path, ".jpg")
        final_pil = Image.fromarray(result_img)
        final_pil.save(output_path)
        
        return output_path
    def process_image(self, image_path: str, output_dir: str = "./output"):
        """完整处理流程：识别 -> 去水印 -> 增强 -> 换色 -> 添加文字"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        basename = os.path.basename(image_path)
        name, ext = os.path.splitext(basename)
        
        # 如果原图没有扩展名，给一个默认值
        if not ext:
            ext = ".png"

        current_img_path = image_path # 追踪当前处理到的图片路径

        # 1. 识别图片类型
        print("--- Step 1: Identify ---")
        identification_result = self.identify_image_type(image_path)
        print(f"识别结果:\n{identification_result}")
        
        # 2. 去水印
        print("--- Step 2: Remove Watermark ---")
        no_watermark_path = os.path.join(output_dir, f"{name}_no_wm{ext}")
        try:
            current_img_path = self.remove_watermark_placeholder(current_img_path, no_watermark_path)
        except Exception as e:
            print(f"去水印失败: {e}，跳过此步骤。")
            
        # 3. 增强清晰度
        print("--- Step 3: Enhance Clarity ---")
        enhanced_path = os.path.join(output_dir, f"{name}_enhanced{ext}")
        try:
            current_img_path = self.enhance_clarity_placeholder(current_img_path, enhanced_path)
        except Exception as e:
            print(f"增强清晰度失败: {e}，跳过此步骤。")

        # 4. 将白色衣服换为黑色 (优先 PyTorch，失败则回退 HSV)
        print("--- Step 4: Change Clothes Color ---")
        black_clothes_path = os.path.join(output_dir, f"{name}_black_clothes{ext}")
        success_change_color = False
        
        # 尝试 PyTorch
        try:
            current_img_path = self.change_clothes_color_pytorch(current_img_path, black_clothes_path, target_color=(0, 0, 0))
            success_change_color = True
        except Exception as e:
            print(f"PyTorch 换色失败: {e}")
            
        # 回退 HSV
        if not success_change_color:
            try:
                print("回退到传统 HSV 方法...")
                current_img_path = self.change_white_to_black(current_img_path, black_clothes_path)
                success_change_color = True
            except Exception as e2:
                print(f"传统换色也失败: {e2}，跳过此步骤。")

        # 5. 添加艺术字测试
        print("--- Step 5: Add Text ---")
        # 修正：之前这里错误地使用了 black_clothes_path 作为目录，现在使用 output_dir
        final_path = os.path.join(output_dir, f"{name}_final{ext}")
        try:
            current_img_path = self.add_artistic_text(current_img_path, final_path, text="HELLO WORLD")
        except Exception as e:
            print(f"添加文字失败: {e}")
            # 尝试 PNG 格式
            final_path_png = os.path.join(output_dir, f"{name}_final.png")
            try:
                current_img_path = self.add_artistic_text(current_img_path, final_path_png, text="HELLO WORLD")
                final_path = final_path_png
            except Exception as e2:
                print(f"PNG 格式添加文字也失败: {e2}")
                # 如果都失败，最终路径就是上一步的路径
            
        return {
            "original": image_path,
            "identified_info": identification_result,
            "no_watermark": no_watermark_path if os.path.exists(no_watermark_path) else current_img_path,
            "enhanced": enhanced_path if os.path.exists(enhanced_path) else current_img_path,
            "black_clothes": black_clothes_path if os.path.exists(black_clothes_path) else current_img_path,
            "final_with_text": final_path if os.path.exists(final_path) else current_img_path
        }

# 使用示例
if __name__ == "__main__":
    test_image_path = "C:\\Users\\admin\\Downloads\\test.jfif" 
    
    # 如果测试文件不存在，创建一个简单的测试图
    if not os.path.exists(test_image_path):
        print(f"警告: 文件 {test_image_path} 不存在，创建测试图片。")
        # 创建一个带有一些白色区域（模拟衣服）和颜色的图片
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        img[:] = (100, 100, 100) # 灰色背景
        # 画一个白色矩形模拟衣服
        cv2.rectangle(img, (100, 100), (300, 300), (255, 255, 255), -1)
        # 确保目录存在
        os.makedirs(os.path.dirname(test_image_path), exist_ok=True)
        cv2.imwrite(test_image_path, img)

    processor = ImageProcessor()
    
    if os.path.exists(test_image_path):
        try:
            result = processor.process_image(test_image_path)
            print("\n--- 处理完成 ---")
            for key, value in result.items():
                if isinstance(value, str) and os.path.exists(value):
                    print(f"[OK] {key}: {value}")
                else:
                    print(f"[INFO] {key}: {value}")
        except Exception as e:
            print(f"程序运行出错: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("请提供有效的图片路径。")