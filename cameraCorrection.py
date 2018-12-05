# coding=utf-8
import cv2
import numpy as np
import argparse


def getCameraInstance(index, cam_flag, resolution):
    """
    用于初始化获取相机实例，从而读取数据

    :param index: 相机的索引编号，如果只有一个相机那就是0，有多个则以此类推
    :param cam_flag: 标定相机类型，单目或双目
    :param resolution: 相机数据的分辨率设置
    :return: 相机实例，以及设置的影像长宽
    """
    cap = cv2.VideoCapture(index)

    if cam_flag == 'single':
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return cap, width, height
    else:
        if resolution == '960p':
            width = 2560
            height = 960
        elif resolution == '480p':
            width = 1280
            height = 480
        elif resolution == '240p':
            width = 640
            height = 240
        # OpenCV有相关API可以设置视频流的长宽
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        return cap, width, height


if __name__ == '__main__':
    # 创建一个Parser用于处理参数，description是帮助描述信息
    parser = argparse.ArgumentParser(description='Camera Correction Script Written by Zhao Xuhui.')
    # 向parser中增加参数，第一个参数是自定义的参数形式，第二个是默认值，第三个是帮助信息
    parser.add_argument('-inner', default='./inner.txt', help='File path of inner params.')
    parser.add_argument('-distort', default='./distort.txt', help='File path of distort params.')
    parser.add_argument('-num', default='0',
                        help='Index of camera that you want to calibrate in your computer,0 as default')
    parser.add_argument('-flag', default='single',
                        help='Camera type,one of these:\'single\',\'left\',\'right\',\'single\' as default')
    parser.add_argument('-reso', default='480p',
                        help='Camera resolution for stero camera,one of these:\'240p\',\'480p\',\'960p\',\'480p\' as default')

    # 获取parser中的所有参数
    args = parser.parse_args()

    # 读取启动参数
    inner_path = args.inner
    distort_path = args.distort
    cam_no = int(args.num)
    cam_flag = args.flag
    reso_flag = args.reso

    dist = np.loadtxt(distort_path)
    inner = np.loadtxt(inner_path)

    # 获取相机实例并返回对象
    cap, width, height = getCameraInstance(cam_no, cam_flag, reso_flag)

    # 不断循环读取帧数据
    while True:
        ret, frame = cap.read()

        if cam_flag == 'single':
            img_cam = frame
        elif cam_flag == 'left':
            img_cam = frame[:, :int(width / 2), :]
        elif cam_flag == 'right':
            img_cam = frame[:, int(width / 2):, :]

        cv2.imshow("frame_cam", img_cam)

        h, w = img_cam.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(inner, dist, (w, h), 1, (w, h))
        # undistort
        dst = cv2.undistort(img_cam, inner, dist, None, newcameramtx)

        # crop the image
        x, y, w, h = roi
        dst = dst[y:y + h, x:x + w]

        cv2.imshow("correct_cam", dst)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
