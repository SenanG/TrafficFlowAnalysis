import cv2
from detector import Detector, filter_fields, visualize
from tracker import Tracker
from colors import COLORS
from counter import Counter
from aggregator import Aggregator
NAME_OF_CAMERA = '/dev/video0'
NAME_OF_WINDOW = 'window'
CROP = [0,1080,0,1920] 

CROSS = [[50,500],[290,490]]

def visualize_line(im,cross):
    tl,br = cross
    return cv2.line(im,tl,br,[0,255,0],2)

def visualize_tracker(im,tracker):
    for obj in tracker.objects:
        #If a tracked object is not found on current frame
        if obj.unused_count>1:
            continue
        #If an object has crossed the line color is BLACK
        if obj.has_crossed:
            color = [0,0,0]
        #Assign each tracked object a color based on its index number
        else:
            i = obj.idx % len(COLORS)
            color = COLORS[i]
        box = [int(round(j)) for j in obj.box]
        cv2.rectangle(im,box[:2],box[2:],color,2)
    return im

def display_text_box(img, text):
    #Define some parameters for the text box
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2
    color = (255, 255, 255)
    background_color = (0, 0, 0)
    padding = 10
    
    #Get the size of the text box and calculate the position
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    x = padding
    y = img.shape[0] - padding - text_size[1]
    
    #Draw the text box and the text on top of the image
    cv2.rectangle(img, (x, y), (x + text_size[0] + padding, y + text_size[1] + padding), background_color, -1)
    cv2.putText(img, text, (x + padding // 2, y + text_size[1] + padding // 2), font, font_scale, color, thickness)
    
    return img

def main():
    # Load camera
    cam = cv2.VideoCapture(NAME_OF_CAMERA)
    # Set resolution of Camera
    w,h = (1920,1080)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    cv2.namedWindow(NAME_OF_WINDOW,cv2.WINDOW_KEEPRATIO)

    detector = Detector()
    tracker = Tracker()
    counter = Counter(CROSS)
    aggregator = Aggregator()
    
    while True:
        #Read camera
        ret,im = cam.read()
        #Exit if no image
        if not ret:
            break
        im = im[CROP[0]:CROP[1],CROP[2]:CROP[3]]
        
        #Detect objects on image
        outputs = detector.detect(im)
        fields = detector.get_fields(outputs)
        fields = filter_fields(fields)

        #Track the object boxes
        tracker.track(fields['pred_boxes'])
        
        #Checks if object crosses line
        counter.check_crosses(tracker.objects)

        #Visualize line and tracked objects on image
        im_with_results = visualize_line(im,CROSS)
        im_with_results = visualize_tracker(im_with_results,tracker)
        
        #Get counts and display that on image
        results = counter.get_results()
        im_with_results = display_text_box(im_with_results,f"{results}")

        #Print results to file and reset counts
        if aggregator.check():
            counter.print_results()
            counter.reset()

        # Display image
        cv2.imshow(NAME_OF_WINDOW,im_with_results)
        chd = cv2.waitKey(1)
        # Exit if q is pressed
        if chd == ord('q'):
            break

if __name__=='__main__':
    main()