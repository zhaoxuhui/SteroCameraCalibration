# coding=utf-8
import cv2
import numpy as np
import argparse

start_x = 30
start_y = 30


def reactionEvent(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if start_x < x < start_x + 70 and start_y < y < start_y + 30:
            if not img_ret:
                print "No chessboard detected."
            else:
                objpoints.append(objp)
                imgpoints.append(img_corners2)
                cv2.imwrite(
                    args.flag + "_" + int(width).__str__() + "@" + int(
                        height).__str__() + "_" + imgpoints.__len__().__str__().zfill(2) + ".jpg",
                    img_gray)
                print imgpoints.__len__(), "image(s) added."
        elif start_x + 80 < x < start_x + 215 and start_y < y < start_y + 30:
            if imgpoints.__len__() >= 10:
                ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img_gray.shape[::-1], None,
                                                                   None)
                np.savetxt(args.flag + "_" + int(width).__str__() + "@" + int(height).__str__() + "_inner.txt", mtx)
                np.savetxt(args.flag + "_" + int(width).__str__() + "@" + int(height).__str__() + "_distort.txt", dist)
                print "Saved parameters."
            else:
                print imgpoints.__len__().__str__() + " images,no enough 10 images."
        elif start_x + 225 < x < start_x + 285 and start_y < y < start_y + 30:
            cv2.destroyAllWindows()
            exit()


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
    parser = argparse.ArgumentParser(description='Camera Calibration Script Written by Zhao Xuhui.')
    # 向parser中增加参数，第一个参数是自定义的参数形式，第二个是默认值，第三个是帮助信息
    parser.add_argument('-row', default='6', help='Row number of chessboard,6 as default')
    parser.add_argument('-col', default='8', help='Column number of chessboard,8 as default')
    parser.add_argument('-num', default='0',
                        help='Index of camera that you want to calibrate in your computer,0 as default')
    parser.add_argument('-flag', default='single',
                        help='Camera type,one of these:\'single\',\'left\',\'right\',\'single\' as default')
    parser.add_argument('-reso', default='480p',
                        help='Camera resolution for stero camera,one of these:\'240p\',\'480p\',\'960p\',\'480p\' as default')

    # 获取parser中的所有参数
    args = parser.parse_args()

    ROWS = int(args.row)
    COLOMONS = int(args.col)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((ROWS * COLOMONS, 3), np.float32)
    objp[:, :2] = np.mgrid[0:ROWS, 0:COLOMONS].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # 读取启动参数
    cam_no = int(args.num)
    cam_flag = args.flag
    reso_flag = args.reso
    # 获取相机实例并返回对象
    cap, width, height = getCameraInstance(cam_no, cam_flag, reso_flag)

    cv2.namedWindow("img_cam")
    cv2.setMouseCallback("img_cam", reactionEvent)

    # 不断循环读取帧数据
    while True:
        ret, frame = cap.read()

        if cam_flag == 'single':
            img_cam = frame
        elif cam_flag == 'left':
            img_cam = frame[:, :int(width / 2), :]
        elif cam_flag == 'right':
            img_cam = frame[:, int(width / 2):, :]

        # Find the chess board corners
        img_gray = cv2.cvtColor(img_cam, cv2.COLOR_BGR2GRAY)
        img_ret, img_corners = cv2.findChessboardCorners(img_gray, (ROWS, COLOMONS), None)
        if img_corners is not None:
            img_corners2 = cv2.cornerSubPix(img_gray, img_corners, (11, 11), (-1, -1), criteria)
            img_cam = cv2.drawChessboardCorners(img_cam, (ROWS, COLOMONS), img_corners2, img_ret)

        cv2.rectangle(img_cam, (start_x, start_y), (start_x + 70, start_y + 30), (0, 0, 255), 2)
        cv2.putText(img_cam, "save", (start_x, start_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1,
                    cv2.LINE_AA)

        cv2.rectangle(img_cam, (start_x + 80, start_y), (start_x + 215, start_y + 30), (0, 0, 255), 2)
        cv2.putText(img_cam, "calibrate", (start_x + 80, start_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1,
                    cv2.LINE_AA)

        cv2.rectangle(img_cam, (start_x + 225, start_y), (start_x + 285, start_y + 30), (0, 0, 255), 2)
        cv2.putText(img_cam, "exit", (start_x + 225, start_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1,
                    cv2.LINE_AA)

        cv2.imshow("img_cam", img_cam)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
