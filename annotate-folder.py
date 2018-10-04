'''
File: annotate-folder.py
Author: Sai Prajwal Kotamraju
Description: This script generates annotations for images of a given dataset
             in KITTI data format. Annotations are saved into a specified
             destination folder.
'''
import cv2
import numpy as np
from os import listdir, mkdir, getcwd
from os.path import isfile, join, exists
import json
from shutil import copyfile

# Global variables
ix,iy = -1,-1 # Iintial mouse point coordinates
fx, fy, lx, ly = -1,-1,-1,-1 # coordinates to keep track of mouse movement
draw = False # Enables only on left mouse click
mask_prev = None # Keeps track of previous renderings
mask = None # Mask for current rendering
kitti_data_cell = None # Info on label and bbox for single object
kitti_data = None # List that holds all the data cells for one image
obj_label = None # Object Label

# mouse callback function
def draw_annotation(event,x,y,flags,param):
    # Declaring the following variables as global ensures that the changes
    # made in this function last out of the function
    global ix,iy,draw, fx, fy, lx, ly
    global mask_prev, mask, obj_label, kitti_data_cell, kitti_data
    # As soon as left mouse button is clicked, store the initial mouse
    # pointer coordinates.
    if event == cv2.EVENT_LBUTTONDOWN:
        ix,iy = x,y
        draw = True
        fx,fy = ix,iy
    elif event == cv2.EVENT_LBUTTONUP:
        # mask_prev saves every mask rendering in order to get back
        # recursively when 'c' is pressed
        mask_prev.append(mask.copy())
        cv2.rectangle(mask,(ix,iy),(x,y),(0,50,-50),-1)
        kitti_data_cell['label'] = obj_label
        kitti_data_cell['bbox'] = dict()
        kitti_data_cell['bbox']['xmin'] = min(ix,x)
        kitti_data_cell['bbox']['ymin'] = min(iy,y)
        kitti_data_cell['bbox']['xmax'] = max(ix,x)
        kitti_data_cell['bbox']['ymax'] = max(iy,y)
        kitti_data.append(kitti_data_cell)
        draw = False
        fx, fy, lx, ly = -1, -1, -1, -1
    elif event == cv2.EVENT_MOUSEMOVE:
        if(draw):
            lx = x
            ly = y

if __name__ == '__main__':
    datasetPath = input('Enter the path to dataset: ')
    current_path = getcwd()
    destination_images_path = current_path+'/'+datasetPath.split('/')[-1]+'_Images_KITTI'
    destination_annotations_path = current_path+'/'+datasetPath.split('/')[-1]+'_Annotations_KITTI'

    obj_label = input('Enter default object label: ')
    obj_label_default = obj_label

    if(not exists(destination_images_path)):
        mkdir(destination_images_path)

    if(not exists(destination_annotations_path)):
        mkdir(destination_annotations_path)

    for datasetImgFile in listdir(datasetPath):
        if isfile(join(datasetPath, datasetImgFile)):
            obj_label = obj_label_default
            filepath = datasetPath+'/'+datasetImgFile
            img = cv2.imread(filepath,1)
            try:
                rows, columns, colors = img.shape
            except:
                continue
            destFileName = datasetImgFile.split('.')[0]
            destAnnFile = destination_annotations_path + '/' + destFileName +'.txt'
            destImgFile = destination_images_path + '/' + datasetImgFile
            if(exists(destAnnFile)):
                continue
            kitti_data = list()
            mask = np.zeros((rows, columns, colors), dtype=np.uint8)
            mask_prev = list()
            cv2.namedWindow('image',cv2.WINDOW_NORMAL)
            cv2.setMouseCallback('image',draw_annotation)
            check = 0 # Flag to stop annotation process
            cancel_check = 0 # Flag to skip annotation to next image
            while(1):
                mask_ref = np.zeros((rows, columns, colors), dtype=np.uint8)
                kitti_data_cell = dict()
                if(fx != -1 and fy != -1 and lx != -1 and ly != -1):
                    cv2.rectangle(mask_ref,(fx,fy),(lx,ly),(0,0,50),-1)
                cv2.imshow('image',img+mask+mask_ref)
                k = cv2.waitKey(1) & 0xFF
                if k == 27: # Stop annotating the dataset (Esc key)
                    check = 1
                    break
                elif k == ord('q'): # Finish annotating present image
                    break
                elif k == ord('c'): # Cancel annotation for most recent bbox
                    mask = mask_prev.pop()
                    kitti_data.pop()
                elif k == ord('l'): # Change the label for next object
                    obj_label = input('Enter the object label: ')
                elif k == ord('n'): # Skip to next image
                    cancel_check = 1
                    break
            # End of draw_annotation
            cv2.destroyAllWindows()
            if(not (len(kitti_data) == 0) and not(cancel_check)):
                print(kitti_data[:])
                # Write the contents into file
                annotation_file_obj = open(destAnnFile,'w')
                for objct in kitti_data:
                    annotation_file_obj.write( '%s' % (objct['label']))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(0))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.0f'%(0))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(0))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(objct['bbox']['xmin']))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(objct['bbox']['ymin']))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(objct['bbox']['xmax']))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(objct['bbox']['ymax']))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(0))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(0))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(0))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(0))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(0))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(0))
                    annotation_file_obj.write(' ')
                    annotation_file_obj.write('%.2f'%(0))
                    annotation_file_obj.write('\n')
                annotation_file_obj.close()
                # Copy the image into separate folder
                copyfile(filepath,destImgFile)
            if(check): # Corresponding to the Esc key
                break
