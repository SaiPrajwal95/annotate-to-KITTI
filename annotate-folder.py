import cv2
import numpy as np
from os import listdir, mkdir
from os.path import isfile, join, isdir, exists
import json

ix,iy = -1,-1
draw = False

# mouse callback function
def draw_annotation(event,x,y,flags,param):
    global ix,iy,draw
    if event == cv2.EVENT_LBUTTONDOWN:
        ix,iy = x,y
        draw = True
    elif event == cv2.EVENT_LBUTTONUP:
        cv2.rectangle(mask,(ix,iy),(x,y),(0,0,50),-1)
        print(min(ix,x),min(iy,y),max(ix,x),max(iy,y))
        #img_data['bboxes'].append((ix,iy,x,y))
        draw = False
    elif event == cv2.EVENT_MOUSEMOVE:
        if(draw):
            cv2.rectangle(mask,(ix,iy),(x,y),(0,0,50),-1)
            # pass

if __name__ == '__main__':
    # path = input('Enter the path to dataset: ')
    # destination_path = input('Enter the destination path: ')
    path = '/home/saiprajwalk/Desktop/TestImages'
    destination_path = '/home/saiprajwalk/Desktop/TestImagesANN'
    if(not exists(destination_path)):
        mkdir(destination_path)
    for f in listdir(path):
        if isfile(join(path, f)):
            filepath = path+'/'+f
            img = cv2.imread(filepath,1)
            try:
                rows, columns, colors = img.shape
            except:
                continue
            cv2.namedWindow('image',cv2.WINDOW_NORMAL)
            cv2.setMouseCallback('image',draw_annotation)
            check = 0
            while(1):
                mask = np.zeros((rows, columns, colors), dtype=np.uint8)
                cv2.imshow('image',img+mask)
                k = cv2.waitKey(1) & 0xFF
                if k == 27:
                    check = 1
                    break
                elif k == ord('q'):
                    break
                # mask = np.zeros((rows, columns, colors), dtype=np.uint8)
            # End of draw_annotation
            cv2.destroyAllWindows()
            #if(len(img_data['bboxes'])>0):
                #data_annotations.append(img_data)
            #    pass
            if(check):
                break
