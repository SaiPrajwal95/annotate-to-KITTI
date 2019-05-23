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
# Prefixes: f -> first, l -> last
fx, fy, lx, ly = -1,-1,-1,-1 # coordinates to keep track of mouse movement
draw = False # Enables only on left mouse click
mask_prev = None # Keeps track of previous renderings
mask = None # Mask for current rendering
kitti_data_cell = None # Info on label and bbox for single object
kitti_data = None # List that holds all the data cells for one image
obj_label = None # Object Label

# mouse callback function
def draw_annotation(event,x,y,flags,param):
    """function generates mask renderings depending upon the left mouse button
    position, and mode of operation.
    Parameters:
    event: Refers to the external events of a mouse click.
    x,y: Posiion of mouse pointer
    flags: Flags that can be used to enable/disable any features.
    params: Parameters/thresholds to vary the functionality.
    """
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
        cv2.rectangle(mask,(ix,iy),(x,y),(0,-200,200),-1)
        kitti_data_cell['label'] = obj_label
        kitti_data_cell['bbox'] = dict()
        kitti_data_cell['bbox']['xmin'] = min(ix,x)
        kitti_data_cell['bbox']['ymin'] = min(iy,y)
        kitti_data_cell['bbox']['xmax'] = max(ix,x)
        kitti_data_cell['bbox']['ymax'] = max(iy,y)
        kitti_data.append(kitti_data_cell)
        draw = False
        fx, fy, lx, ly = -1, -1, -1, -1
    elif (event == cv2.EVENT_MOUSEMOVE and draw):
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
    logf = open("logFile.log", "w")
    for datasetImgFile in listdir(datasetPath):
        if isfile(join(datasetPath, datasetImgFile)):
            obj_label = obj_label_default
            filepath = datasetPath+'/'+datasetImgFile
            img = cv2.imread(filepath,1)
            try:
                rows, columns, colors = img.shape
            except Exception as e:
                logf.write("Failed to open {0}: {1}\n".format(filepath, str(e)))
                continue
            logf.write("\nOpened the image {0} for annotation\n".format(filepath))
            resize_factor = 640.00/max(rows, columns)
            resized = False
            if (resize_factor < 1):
                resized = True
                img = cv2.resize(img, None, fx=resize_factor,fy=resize_factor)
                rows, columns, colors = img.shape
            destFileName = datasetImgFile.split('.')[0]
            destAnnFile = destination_annotations_path + '/' + destFileName +'.txt'
            destImgFile = destination_images_path + '/' + datasetImgFile
            if(exists(destAnnFile)):
                logf.write("Annotation already exists for {0}\n".format(filepath))
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
                    cv2.rectangle(mask_ref,(fx,fy),(lx,ly),(0,200,0),-1)
                cv2.imshow('image',cv2.addWeighted(img+mask+mask_ref, 0.7, img, 0.3, 0))
                k = cv2.waitKey(1) & 0xFF
                if k == 27: # Stop annotating the dataset (Esc key)
                    check = 1
                    break
                elif k == ord('q'): # Finish annotating present image
                    logf.write("Ending the annotation process for {0}\n".format(filepath))
                    break
                elif k == ord('c'): # Cancel annotation for most recent bbox
                    logf.write("Canceling the previous bbox annotation\n")
                    mask = mask_prev.pop()
                    kitti_data.pop()
                elif k == ord('l'): # Change the label for next object
                    logf.write("Changing the label from {0} to ".format(obj_label))
                    obj_label = input('Enter the object label: ')
                    logf.write("{0}\n".format(obj_label))
                elif k == ord('n'): # Skip to next image
                    cancel_check = 1
                    logf.write("Skipping to next image. Annotation not saved.\n")
                    break

            cv2.destroyAllWindows()
            if(not (len(kitti_data) == 0) and not(cancel_check)):
                # Write the contents into file
                annotation_file_obj = open(destAnnFile,'w')
                for obj in kitti_data:
                    if (resized):
                        obj['bbox']['xmin'] /= resize_factor
                        obj['bbox']['ymin'] /= resize_factor
                        obj['bbox']['xmax'] /= resize_factor
                        obj['bbox']['ymax'] /= resize_factor
                    annotation_str = "%s %.2f %.0f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f\n" \
                    %(obj['label'], 0, 0, 0, obj['bbox']['xmin'], obj['bbox']['ymin'], obj['bbox']['xmax'], \
                    obj['bbox']['ymax'], 0, 0, 0, 0, 0, 0, 0)
                    annotation_file_obj.write(annotation_str)
                annotation_file_obj.close()
                # Copy the image into separate folder
                copyfile(filepath,destImgFile)
            if(check): # Corresponding to the Esc key
                logf.write("Qutting the annotation process\n")
                break
    logf.close()
