# -*- coding: utf-8 -*-

import cv2

def draw_box_name(bbox, name, frame, suhu='error', threshold_suhu=38.0):
	"""
	Arguments:
		bbox = x, y, x+w, y+h --> (atas, bawah)
	"""

	if type(suhu) ==type(' tipe string'):
		color_bbox = (0,0,255)
		color_text = (0,0,0)
	else:
		if suhu > threshold_suhu:
			color_bbox = (255,0,0)
			color_text = (255,255,255)
		else:
			color_text = (0,0,0)
			color_bbox = (0,255,0)


	frame = cv2.rectangle(frame, (bbox[0], bbox[1]), 
								 (bbox[2], bbox[3]), 
								 color_bbox, 
								 thickness=2)
	
	# ---- label for NAME
	thres = 10
	baseline, labelSize = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.9,2)
	top = bbox[1] - 2 if bbox[1] - thres > thres else bbox[1] + thres +10
	topBaseline = top-baseline[1] if bbox[1] - 15 >  15 else top+baseline[1]
	frame = cv2.rectangle(frame,
							(bbox[0]-1, top - baseline[1]), 
							(bbox[0]+baseline[0], top+2),
							color_bbox, -1)	
	
	frame = cv2.putText(frame, name,
						(bbox[0]+3, top),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_text, 1,
						cv2.LINE_AA)

	# ---- label for THERMAL
	baselineSuhu, labelSizeSuhu = cv2.getTextSize(str(suhu)+" C", cv2.FONT_HERSHEY_SIMPLEX, 0.7,2)
	bottom = bbox[3] + 15 if bbox[3] + 20 < frame.shape[0] else bbox[3]-2

	frame = cv2.rectangle(frame,
							(bbox[2], bottom - baselineSuhu[1]), 
							(bbox[2]-baselineSuhu[0], bottom+3),
							color_bbox, -1)	

	frame = cv2.putText(frame, str(suhu)+" C",
						(bbox[2]-baselineSuhu[0]+5, bottom),
						cv2.FONT_HERSHEY_SIMPLEX, 0.65, color_text, 1,
						cv2.LINE_AA)
	return frame
