import csv
import datetime
import os.path

from django.contrib.auth.models import User
from django.shortcuts import render
from .models import MosaicArt

from PIL import Image

from .mosaic_art import calc
from .mosaic_art import image_process


DOT_AREA_ONE_SIDE = 10
THUMBNAIL_ONE_SIDE = 40
# 2つの色(R,G,B)の間の最大の距離
MAX_COLOR_DISTANCE = 255**2 * 3
# CSVファイル中のカラムの意味づけ
POS_NAME  = 0
POS_RED   = 1
POS_GREEN = 2
POS_BLUE  = 3


def art_list(request):
    if request.method == "POST":
        print('送信ボタン押下されたのでモザイクアートを作る')
        # 現状はadminがモザイクアートを作ったことになる
        target_im = request.POST['target_image']
        print('対象画像', target_im)
        # モザイクアートのファイル名とDBのfile_nameフィールドが一致するように
        # ファイル名の組み立てをここで実施する
        saved_file_name = mosaic_art_file_name(target_im)
        make_mosaic(target_im, saved_file_name)
        me = User.objects.get(username='ftnext')
        MosaicArt.objects.create(user = me,
            file_name=saved_file_name, original_image=target_im)
        print('Mosaic art created at', saved_file_name)
    else:  # ← methodが'POST'ではない = 最初のページ表示時の処理
        print('POSTでないので処理はなにもしない')
    mosaic_arts = MosaicArt.objects.order_by('-created_date')[:2]
    return render(request, 'gallery/art_list.html', {'mosaic_arts': mosaic_arts})

def make_mosaic(target_im, saved_file_name):
    """Creates mosaic art from target image

    Args:
        target_im: target image file name (:str)
            example: 'bar.png'
        saved_file_name: mosaic art file name (:str)
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    color_data_file = os.path.join(BASE_DIR, 'static/images/data/average_color.csv')
    color_data = materials_list_from_file(color_data_file)

    target_file = os.path.join(BASE_DIR, 'static/images/target/{}'.format(target_im))
    icon_im = image_process.open_image_RGB(target_file)
    icon_im_width, icon_im_height = icon_im.size
    mosaic_icon_im = Image.new('RGBA', (1600, 1600))

    for left in range(0, icon_im_width, DOT_AREA_ONE_SIDE):
        for top in range(0, icon_im_height, DOT_AREA_ONE_SIDE):
            average_color = calc.average_color_in_range(icon_im, left, top,
                                left+DOT_AREA_ONE_SIDE, top+DOT_AREA_ONE_SIDE)
            if len(average_color) != 3:
                continue

            filename = similar_color_filename(average_color, color_data)
            # 距離最小のファイルを1600×1600の画像に貼り付け
            open_file = os.path.join(BASE_DIR, 'static/images/material/euph_part_icon/'+filename)
            area_im = Image.open(open_file)
            mosaic_icon_im.paste(area_im, (left//DOT_AREA_ONE_SIDE * THUMBNAIL_ONE_SIDE,
                                           top//DOT_AREA_ONE_SIDE * THUMBNAIL_ONE_SIDE))

    saved_file_path = 'static/images/ftnext/{}'.format(saved_file_name)
    saved_file = os.path.join(BASE_DIR, saved_file_path)
    mosaic_icon_im.save(saved_file)

def mosaic_art_file_name(target_im):
    """Returns a file name from target image name

    Args:
        target_im: path of target image file (:str)
            example: 'foo/bar.png'

    Returns:
        str
            example: 'bar_mosaic_20180331121251.png'
    """
    target_file_name = extract_file_name(target_im)
    now_dt = now_datetime()
    return '{0}_mosaic_{1}.png'.format(target_file_name, now_dt)

def extract_file_name(file_path):
    """Extracts file name from file path (not including extension)

    Args:
        file_path: str
            example: 'foo/bar.png'

    Returns:
        str
            example: 'bar'

    """
    # ファイルパスからファイル名(拡張子含む)を取り出す
    file_name = file_path.split('/')[-1]
    # 拡張子を取り除く
    return file_name.split('.')[0]

def now_datetime():
    """Returns current time as '%Y%m%d%H%M%S' string

    Returns:
        str
            example: '20180331121251'
                current time 2018/3/31 12:12:51
    """
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d%H%M%S')

def materials_list_from_file(filename):
    """Returns a list which contains material image information.

    Args:
        filename: File name such as "foo.csv"
            The file contains information on average color of image.
            (Average color maens the average of the values of R of all pixels,
             the average of the values of G of all pixels,
             and the average of the values of B of all pixels)
            A row is as follows:
                image_name, R_average, G_average, B_average

    Returns:
        A list of tuples
        Tuple is like (
            image_name   : str (such as "bar.png"),
            red_average  : int,
            green_average: int,
            blue_average : int
            )
    """
    color_data = []
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            image_info = (row[POS_NAME], int(row[POS_RED]),
                          int(row[POS_GREEN]), int(row[POS_BLUE]))
            color_data.append(image_info)
    return color_data

def color_distance(RGB1, RGB2):
    """Returns color distance

    Considering the distance between two points
    (x1, y1, z1) and (x2, y2, z2) in three dimensions

    Args:
        RGB1: A tuple which means (R, G, B)
        RGB2: A tuple which means (R, G, B)

    Returns:
        color distance(:int)

    """
    d2_r = (RGB1[0] - RGB2[0]) ** 2
    d2_g = (RGB1[1] - RGB2[1]) ** 2
    d2_b = (RGB1[2] - RGB2[2]) ** 2
    return d2_r + d2_g + d2_b

def similar_color_filename(average_color, color_data):
    """Returns name of file similar to average color

    Find the image with average color closest to `average_color` from `color_data`

    Args:
        average_color: a tuple which means (R, G, B) of average color of a certain range
        color_data: A list of tuples
                    Tuple is like (image_name, red_average, green_average, blue_average)

    Returns:
        A name of file such as 'foo.png' (NOT path)
    """
    distance = MAX_COLOR_DISTANCE
    filename = ''
    # 色の差が最小になるファイルを決定(距離に見立てている)
    for color in color_data:
        sample_color = (color[POS_RED], color[POS_GREEN], color[POS_BLUE])
        d = color_distance(average_color, sample_color)
        if d < distance:
            distance = d
            filename = color[POS_NAME]
    return filename
