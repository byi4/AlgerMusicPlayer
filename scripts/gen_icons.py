# -*- coding: utf-8 -*-
"""从 resources/AppIcon.png 生成全套应用图标（打包/运行时/PWA/菜单）。"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'resources', 'AppIcon.png')

# 圆角半径占边长的比例（≈ Windows 11 应用图标的视觉圆角）
RADIUS_RATIO = 0.18
# 圆角遮罩的超采样倍数，抗锯齿更平滑
SUPERSAMPLE = 4

src = Image.open(SRC).convert('RGBA')
print(f'源图: {src.size[0]}x{src.size[1]} {src.mode}')


def rounded_mask(size):
    """生成指定尺寸的圆角矩形 alpha 遮罩（超采样抗锯齿）。"""
    big = size * SUPERSAMPLE
    radius = int(big * RADIUS_RATIO)
    mask = Image.new('L', (big, big), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, big - 1, big - 1), radius=radius, fill=255)
    return mask.resize((size, size), Image.LANCZOS)


def r(size, rounded=False):
    """按目标尺寸高质量缩放；rounded=True 时把四角抹成透明圆角。"""
    img = src.resize((size, size), Image.LANCZOS)
    if not rounded:
        return img
    mask = rounded_mask(size)
    # 用圆角遮罩与原 alpha 取交集，保留原图自带的透明区域
    alpha = img.getchannel('A')
    alpha = Image.composite(alpha, Image.new('L', img.size, 0), mask)
    img.putalpha(alpha)
    return img


def save(img, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print(f'  写入 {os.path.relpath(path, ROOT)}')


# 1. Linux 打包多尺寸 PNG（build/icons）
linux_sizes = [16, 32, 48, 64, 128, 256, 512, 1024]
for s in linux_sizes:
    save(r(s), 'build', 'icons', f'{s}x{s}.png')

# 2. 运行时窗口图标 + 托盘图标（resources）
save(r(1084, rounded=True), 'resources', 'icon.png')  # 主窗口图标（非 mac），圆角
save(r(16), 'resources', 'icon_16x16.png')            # 系统托盘（太小，保持方形）

# 3. PWA 图标（resources）
save(r(192), 'resources', 'icon-192.png')
save(r(512), 'resources', 'icon-512.png')
save(r(512), 'resources', 'icon-512-maskable.png')  # 源图为全出血方图，直接用作 maskable

# 4. 应用内菜单 logo
save(r(256), 'src', 'renderer', 'assets', 'icon.png')

# 5. Windows ICO（打包 + NSIS 安装/卸载 + favicon），多尺寸内嵌，圆角
# Windows 原样显示 ICO 位图，四角透明即呈圆角。用一张烘焙好圆角的 256 图，
# 靠 sizes= 自动缩放出各内嵌尺寸（Pillow 对 append_images 组装 ICO 支持不稳）。
ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
ico_img = r(256, rounded=True)
for name in ['icon.ico', 'favicon.ico']:
    p = os.path.join(ROOT, 'resources', name)
    ico_img.save(p, format='ICO', sizes=ico_sizes)
    print(f'  写入 resources/{name}')
# build 目录备份 ico
ico_img.save(os.path.join(ROOT, 'build', 'icon.ico'), format='ICO', sizes=ico_sizes)
print('  写入 build/icon.ico')
save(r(1024), 'build', 'icon.png')

# 6. macOS ICNS
for p in [os.path.join(ROOT, 'resources', 'icon.icns'),
          os.path.join(ROOT, 'build', 'icon.icns')]:
    r(1024).save(p, format='ICNS')
    print(f'  写入 {os.path.relpath(p, ROOT)}')

print('完成。')
