import cv2
import numpy as np
from os import listdir, mkdir
from os.path import isfile, join, isdir, exists
import json

ix,iy = -1,-1
fx, fy, lx, ly = -1,-1,-1,-1
draw = False
mask_prev = None
mask = None

# mouse callback function
def draw_annotation(event,x,y,flags,param):
    global ix,iy,draw, fx, fy, lx, ly, mask_prev, mask
    if event == cv2.EVENT_LBUTTONDOWN:
        ix,iy = x,y
        draw = True
        fx,fy = ix,iy
    elif event == cv2.EVENT_LBUTTONUP:
        mask_prev = mask.copy()
        cv2.rectangle(mask,(ix,iy),(x,y),(0,50,-50),-1)
        print(min(ix,x),min(iy,y),max(ix,x),max(iy,y))
        draw = False
        fx, fy, lx, ly = -1, -1, -1, -1
    elif event == cv2.EVENT_MOUSEMOVE:
        if(draw):
            lx = x
            ly = y

if __name__ == '__main__':
    path = input('Enter the path to dataset: ')
    destination_path = input('Enter the destination path: ')

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
            mask = np.zeros((rows, columns, colors), dtype=np.uint8)
            mask_prev = np.zeros((rows, columns, colors), dtype=np.uint8)
            cv2.namedWindow('image',cv2.WINDOW_NORMAL)
            cv2.setMouseCallback('image',draw_annotation)
            check = 0
            while(1):
                mask_ref = np.zeros((rows, columns, colors), dtype=np.uint8)
                if(fx != -1 and fy != -1 and lx != -1 and ly != -1):
                    cv2.rectangle(mask_ref,(fx,fy),(lx,ly),(0,0,50),-1)
                cv2.imshow('image',img+mask+mask_ref)
                k = cv2.waitKey(1) & 0xFF
                if k == 27: # Stop annotating the dataset
                    check = 1
                    break
                elif k == ord('q'): # Stop annotating present image
                    break
                elif k == ord('c'): # Cancel annotation for most recent bbox
                    mask = mask_prev.copy()
            # End of draw_annotation
            cv2.destroyAllWindows()
            if(check):
                break
