import cv2

def draw_box_name(bbox,name,frame):
	color_bbox = (0,215,255)
	frame = cv2.rectangle(frame, (bbox[0], bbox[1]), 
								 (bbox[2], bbox[3]), 
								 color_bbox, 
								 thickness=2)
	baseline, labelSize = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 1,2)
	frame = cv2.rectangle(frame,
							(bbox[0]-1, bbox[1]-baseline[1]), 
							(bbox[0]+baseline[0], bbox[1]),color_bbox, -1)	
	frame = cv2.putText(frame, name,
						(bbox[0]+2, bbox[1]-2),
						cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,0), 1,
						cv2.LINE_AA)
	return frame
