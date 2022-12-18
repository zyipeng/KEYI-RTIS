#!/usr/bin/env python
import numpy as np
from PIL import Image
from scipy.cluster.vq import kmeans, vq


def quantize(image, bits_per_channel=None):
    """减少给定图像中每个通道的比特数。"""

    if bits_per_channel is None:
        bits_per_channel = 6

    assert image.dtype == np.uint8

    shift = 8 - bits_per_channel
    halfbin = (1 << shift) >> 1

    return ((image.astype(int) >> shift) << shift) + halfbin


def pack_rgb(rgb):
    """将一个24位RGB三元组打包到一个整数中，对数组和元组都有效。"""

    orig_shape = None

    if isinstance(rgb, np.ndarray):
        assert rgb.shape[-1] == 3
        orig_shape = rgb.shape[:-1]
    else:
        assert len(rgb) == 3
        rgb = np.array(rgb)

    rgb = rgb.astype(int).reshape((-1, 3))

    packed = (rgb[:, 0] << 16 |
              rgb[:, 1] << 8 |
              rgb[:, 2])

    if orig_shape is None:
        return packed
    else:
        return packed.reshape(orig_shape)


def unpack_rgb(packed):
    """
    将单个整数或整数数组解压为一个或多个24位RGB值。
    """

    orig_shape = None

    if isinstance(packed, np.ndarray):
        assert packed.dtype == int
        orig_shape = packed.shape
        packed = packed.reshape((-1, 1))

    rgb = ((packed >> 16) & 0xff,
           (packed >> 8) & 0xff,
           (packed) & 0xff)

    if orig_shape is None:
        return rgb
    else:
        return np.hstack(rgb).reshape(orig_shape + (3,))


def get_bg_color(image, bits_per_channel=None):
    """
    通过将相似颜色分组到箱子中并找到最频繁的颜色，从一幅图像或RGB颜色数组中获取背景颜色。
    """
    assert image.shape[-1] == 3

    quantized = quantize(image, bits_per_channel).astype(int)
    packed = pack_rgb(quantized)

    unique, counts = np.unique(packed, return_counts=True)

    packed_mode = unique[counts.argmax()]

    return unpack_rgb(packed_mode)


def rgb_to_sv(rgb):
    """
    将RGB颜色的RGB图像或数组转换为饱和度和值，返回每一个单独的32位浮点数组或值。
    """
    if not isinstance(rgb, np.ndarray):
        rgb = np.array(rgb)

    axis = len(rgb.shape) - 1
    cmax = rgb.max(axis=axis).astype(np.float32)
    cmin = rgb.min(axis=axis).astype(np.float32)
    delta = cmax - cmin

    saturation = delta.astype(np.float32) / cmax.astype(np.float32)
    saturation = np.where(cmax == 0, 0, saturation)

    value = cmax / 255.0

    return saturation, value


def percent(string):
    """Convert a string (i.e. 85) to a fraction (i.e. .85)."""
    return float(string) / 100.0


def load(pil_img):
    """
    加载一个带有Pillow的图像，并将其转换为numpy数组。
    也将x和y中的图像DPI作为元组返回。
    """
    if pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')

    if 'dpi' in pil_img.info:
        dpi = pil_img.info['dpi']
    else:
        dpi = (300, 300)

    img = np.array(pil_img)

    return img, dpi


def sample_pixels(img, options):
    """
    在图像中选择一个固定百分比的像素，以随机的顺序返回。
    """
    pixels = img.reshape((-1, 3))
    num_pixels = pixels.shape[0]
    num_samples = int(num_pixels * options.get('sample_fraction'))

    idx = np.arange(num_pixels)
    np.random.shuffle(idx)

    return pixels[idx[:num_samples]]


def get_fg_mask(bg_color, samples, options):
    """
    通过将一组样本中的每个像素与背景颜色进行比较，判断其是否为前景。
    如果一个像素的值或饱和度与背景有一个阈值不同，则该像素被归类为前景像素。
    """

    s_bg, v_bg = rgb_to_sv(bg_color)
    s_samples, v_samples = rgb_to_sv(samples)

    s_diff = np.abs(s_bg - s_samples)
    v_diff = np.abs(v_bg - v_samples)

    return ((v_diff >= options.get('value_threshold')) |
            (s_diff >= options.get('sat_threshold')))


def get_palette(samples, options, return_mask=False, kmeans_iter=40):
    """
    提取一组采样RGB值的调色板。第一个调色板条目总是背景颜色;
    其余的通过运行K-means聚类从前景像素中确定。返回调色板，以及
    与前景像素相对应的蒙版。
    """

    if not options.get("quiet"):
        print('  getting palette...')

    bg_color = get_bg_color(samples, 6)

    fg_mask = get_fg_mask(bg_color, samples, options)

    centers, _ = kmeans(samples[fg_mask].astype(np.float32),
                        options.get('num_colors') - 1,
                        iter=kmeans_iter)

    palette = np.vstack((bg_color, centers)).astype(np.uint8)

    if not return_mask:
        return palette
    else:
        return palette, fg_mask


def apply_palette(img, palette, options):
    """
    对给定的图像应用调色板。第一步是设置所有背景像素为背景颜色;
    然后，使用最近近邻匹配将每个前景色映射到调色板中最近的景色。
    """

    if not options.get("quiet"):
        print('  applying palette...')

    bg_color = palette[0]

    fg_mask = get_fg_mask(bg_color, img, options)

    orig_shape = img.shape

    pixels = img.reshape((-1, 3))
    fg_mask = fg_mask.flatten()

    num_pixels = pixels.shape[0]

    labels = np.zeros(num_pixels, dtype=np.uint8)

    labels[fg_mask], _ = vq(pixels[fg_mask], palette)

    return labels.reshape(orig_shape[:-1])


def save(labels, palette, dpi, options):
    """
    保存标签/调色板对作为一个索引PNG图像。通过将最小的颜色组件映射为0，
    最大的颜色组件映射为255，这可选地使调色板饱和，并且还可选地将背景颜色
    设置为纯白色。
    """
    if options.get('saturate'):
        palette = palette.astype(np.float32)
        pmin = palette.min()
        pmax = palette.max()
        palette = 255 * (palette - pmin) / (pmax - pmin)
        palette = palette.astype(np.uint8)

    if options.get('white_bg'):
        palette = palette.copy()
        palette[0] = (255, 255, 255)

    output_img = Image.fromarray(labels, 'P')
    output_img.putpalette(palette.flatten().tolist())
    # output_img.save(output_filename, dpi=dpi)
    return output_img


def notescan_main(input_file):
    """此程序的主要功能。"""
    options = {
        "basename": "page",
        "input_filename": "C:\\Users\\ke_yi\\Desktop\\456789.jpg",
        "output_filename": "C:\\Users\\ke_yi\\Desktop\\456789-out.jpg",
        "global_palette": False,
        "num_colors": 8,
        "quiet": False,
        "sample_fraction": 0.05,
        "sat_threshold": 0.2,
        "saturate": True,
        "sort_numerically": True,
        "value_threshold": 0.25,
        "white_bg": False
    }

    img, dpi = load(input_file)
    if img is None:
        print('img is none')

    if not options.get("quiet"):
        print('opened')
    # 返回百分比为sample_fraction的像素
    samples = sample_pixels(img, options)
    palette = get_palette(samples, options)

    labels = apply_palette(img, palette, options)

    return save(labels, palette, dpi, options)
