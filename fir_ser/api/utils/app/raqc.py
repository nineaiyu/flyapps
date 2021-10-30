#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 12月 
# author: NinEveN
# date: 2019/12/19

'''
Python生成二维码 v1.0
主要将文本生成二维码图片

测试一：将文本生成白底黑字的二维码图片
测试二：将文本生成带logo的二维码图片

'''

import os

import qrcode
from PIL import Image


# 生成二维码图片
def make_qr(str, save):
    qr = qrcode.QRCode(
        version=4,  # 生成二维码尺寸的大小 1-40  1:21*21（21+(n-1)*4）
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # L:7% M:15% Q:25% H:30%
        box_size=10,  # 每个格子的像素大小
        border=2,  # 边框的格子宽度大小
    )
    qr.add_data(str)
    qr.make(fit=True)

    img = qr.make_image()
    img.save(save)


# 生成带logo的二维码图片
def make_logo_qr(str, logo, save):
    # 参数配置
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=8,
        border=2
    )
    # 添加转换内容
    qr.add_data(str)
    #
    qr.make(fit=True)
    # 生成二维码
    img = qr.make_image()
    #
    img = img.convert("RGBA")

    # 添加logo
    if logo and os.path.exists(logo):
        icon = Image.open(logo)
        # 获取二维码图片的大小
        img_w, img_h = img.size

        factor = 4
        size_w = int(img_w / factor)
        size_h = int(img_h / factor)

        # logo图片的大小不能超过二维码图片的1/4
        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
        # 详见：http://pillow.readthedocs.org/handbook/tutorial.html

        # 计算logo在二维码图中的位置
        w = int((img_w - icon_w) / 2)
        h = int((img_h - icon_h) / 2)
        icon = icon.convert("RGBA")
        img.paste(icon, (w, h), icon)
        # 详见：http://pillow.readthedocs.org/reference/Image.html#PIL.Image.Image.paste

    # 保存处理后图片
    img.save(save)


if __name__ == '__main__':
    save_path = 'base__runmethod_02.png'  # 生成后的保存文件
    logo = '/tmp/pycharm_project_986/fir/tmp/icon/cmjpwyltznbioseh'  # logo图片

    str = "https://fir.im/luy4"

    make_logo_qr(str, logo, save_path)
