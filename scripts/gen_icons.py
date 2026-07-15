# -*- coding: utf-8 -*-
"""从 resources/AppIcon.png 生成全套应用图标（打包/运行时/PWA/菜单）。"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'resources', 'AppIcon.png')

src = Image.open(SRC).convert('RGBA')
print(f'源图: {src.size[0]}x{src.size[1]} {src.mode}')


def r(size):
    """按目标尺寸高质量缩放。"""
    return src.resize((size, size), Image.LANCZOS)


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
save(r(1084), 'resources', 'icon.png')          # 主窗口图标（非 mac）
save(r(16), 'resources', 'icon_16x16.png')      # 系统托盘

# 3. PWA 图标（resources）
save(r(192), 'resources', 'icon-192.png')
save(r(512), 'resources', 'icon-512.png')
save(r(512), 'resources', 'icon-512-maskable.png')  # 源图为全出血方图，直接用作 maskable

# 4. 应用内菜单 logo
save(r(256), 'src', 'renderer', 'assets', 'icon.png')

# 5. Windows ICO（打包 + NSIS 安装/卸载 + favicon），多尺寸内嵌
ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
for name in ['icon.ico', 'favicon.ico']:
    p = os.path.join(ROOT, 'resources', name)
    r(256).save(p, format='ICO', sizes=ico_sizes)
    print(f'  写入 resources/{name}')
# build 目录备份 ico
r(256).save(os.path.join(ROOT, 'build', 'icon.ico'), format='ICO', sizes=ico_sizes)
print('  写入 build/icon.ico')
save(r(1024), 'build', 'icon.png')

# 6. macOS ICNS
for p in [os.path.join(ROOT, 'resources', 'icon.icns'),
          os.path.join(ROOT, 'build', 'icon.icns')]:
    r(1024).save(p, format='ICNS')
    print(f'  写入 {os.path.relpath(p, ROOT)}')

print('完成。')
