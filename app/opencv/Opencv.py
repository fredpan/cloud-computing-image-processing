# USAGE
# python text_detection.py --image images/lebron_james.jpg --east frozen_east_text_detection.pb
# import the necessary packages
import time
import cv2
import numpy as np
from imutils.object_detection import non_max_suppression


# for test
# folderPath = "/home/yixiao/Desktop/img_database/"
# imgName = "IMG-2019-Slider-01.jpg"
# saveImgName = "s_IMG-2019-Slider-01.jpg"


def imageProcess(folderPath, imgName, saveImgName):
    '''
    This function implemented Opencv2 and numpy library and the “object_detection” method from imutils package.
    The function reads a given image as a openCV image object, then it implement the object_detection method with an
    open source database “frozen_east_text_detection.pb” which includes feature samples of texts . The function then
    creates green squares near all the detected texts and save the processed image with the given saveImgName.
    :param folderPath: (String) the folder path which includes the image which will be read and saved
    :param imgName: (String) the image name which will be processed
    :param saveImgName: (Strinh) the name of the image which will be exported after processing
    :return: Boolean value of True indicating the process is finished successfully
    '''
    image = cv2.imread(folderPath + imgName)
    originalImgCopy = image.copy()
    (H, W) = image.shape[:2]
    (newW, newH) = (320, 320)
    rW = W / float(newW)
    rH = H / float(newH)
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]

    layerNames = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"]

    print("[INFO] loading EAST text detector...")
    net = cv2.dnn.readNet("/var/lib/jenkins/workspace/ece1779-image-processing/app/opencv/frozen_east_text_detection.pb")

    #server should use below address:
    #"/var/lib/jenkins/workspace/ece1779-image-processing/app/opencv/frozen_east_text_detection.pb"

    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    start = time.time()
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)
    end = time.time()

    print("[INFO] text detection took {:.6f} seconds".format(end - start))

    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    for y in range(0, numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]
        for x in range(0, numCols):
            if scoresData[x] < 0.5:
                continue
            (offsetX, offsetY) = (x * 4.0, y * 4.0)
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    for (startX, startY, endX, endY) in boxes:
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        cv2.rectangle(originalImgCopy, (startX, startY), (endX, endY), (0, 255, 0), 2)

    # save the processed img
    cv2.imwrite(folderPath + saveImgName, originalImgCopy)

    return True

# for test
# print(imageProcess(folderPath,imgName,saveImgName))
