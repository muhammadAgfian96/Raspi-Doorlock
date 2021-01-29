import cv2
import time
import numpy as np

def draw_box_name(bbox, name, frame, suhu='ERR', threshold_suhu=38.0):
	"""
	Arguments:
		bbox = x, y, x+w, y+h --> (atas, bawah)
	"""

	if type(suhu) == type('tipe string'):
		color_bbox = (0,0,255) # blue
		color_text = (0,0,0)
	else:
		if suhu > threshold_suhu:
			color_bbox = (255,0,0)
			color_text = (255,255,255)
		else:
			color_text = (0,0,0)
			color_bbox = (0,255,0)
		suhu = '{:.2f}'.format(suhu)


	frame = cv2.rectangle(frame, (bbox[0], bbox[1]), 
								 (bbox[2], bbox[3]), 
								 color_bbox, 
								 thickness=2)
	
	# ---- label for NAME
	ukuran_x = bbox[2]-bbox[0]

	#depth_1_avg = round(358 + (-7.16 * ukuran_x) + 0.0575*(ukuran_x**2) + (-0.000165*(ukuran_x**3)), 2)
	#depth_2 = round(367 + (-7.25 * ukuran_x) + 0.0571*(ukuran_x**2) + (-0.00016*(ukuran_x**3)), 2)
	
	thres = 10
	baseline, labelSize = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.9,2)
	top = bbox[1] - 2 if bbox[1] - thres > thres else bbox[1] + thres +10
	topBaseline = top-baseline[1] if bbox[1] - 15 >  15 else top+baseline[1]
	frame = cv2.rectangle(frame,
							(bbox[0]-1, top - baseline[1]), 
							(bbox[0]+baseline[0], top+2),
							color_bbox, -1)	
	
	frame = cv2.putText(frame, f"{ukuran_x}",
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

def draw_fps(image, start_time):
	FPS =  1/ (time.time()-start_time)     
	image = cv2.putText(image, "FPS: {:.2f}".format(FPS), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 2)
	return image

def get_jarak(bbox):
	raw_jarak = bbox[2]-bbox[0]
	jarak = raw_jarak
	if jarak < 70:
		condition = 'jauh'
	else:
		condition = 'dekat'
	return jarak, condition

def get_jarak_terdekat(bboxes):
	jarak_terdekat = -1
	condition_sekarang = 'jauh'
	for bbox in bboxes:
		jarak, condition = get_jarak(bbox)
		if jarak > jarak_terdekat: 
			jarak_terdekat = jarak
			condition_sekarang = condition
	return jarak_terdekat, condition_sekarang

def draw_status(image, bbox, height_border = 75):
	height_img, width_img, channels = image.shape
	jarak, condition = get_jarak_terdekat(bbox)

	if condition == 'jauh':
		condition_text = f'Lebih dekat. {jarak} cm'
		color_bg = (0,0,255) # merah
	elif condition == 'dekat':
		condition_text = 'Berhenti. Tunggu Sebentar.'
		color_bg = (0, 255, 0) # hijau

	image = cv2.rectangle(image, (0,0), (width_img, height_border), color_bg, -1)
	
	image = cv2.putText(img = image, 
						text = condition_text, 
						org=(width_img//4, height_border-10), 
						fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
						fontScale = 0.8, 
						color = (255,255,255), 
						thickness=1)

	return image, condition


def draw_mesh_thermal(image, pixel_list):
	image = cv2.resize(image, (400,300))
	mean_pix = np.mean(pixel_list)
	
	cal_y_start = -40
	cal_y_end = 40
	cal_x_start = 0
	cal_x_end = 0
	cal_x_text = 0
	cal_y_text = 0

	start_y, end_y = cal_y_start + 0, cal_y_end + 320
	start_x, end_x = cal_x_start + 0, cal_x_end + 400
	total_length_y = abs(start_y) + end_y
	total_length_x = abs(start_x) + end_x
	
	for ix,x in enumerate(range(start_x, end_x, total_length_x//8)):
		for iy, y in enumerate(range(start_y, end_y, total_length_y//8)):
			
			if (ix == 4 and iy == 4):
				thickness = 2
			else:
				thickness = 1
				
			# line horizontal
			image = cv2.line(img = image,
					pt1 = ( x, start_y), 
					pt2 = ( x, end_y  ), 
					color=(0,255,255),
					thickness=thickness)
			
			# line vertikal
			image = cv2.line(img = image,
					pt1 = ( start_x,  + y ), 
					pt2 = ( end_x,    + y ), 
					color=(0,255,255),
					thickness=thickness)

			if (pixel_list[ix][iy] > mean_pix+0.5):
				thickness_text = 2
			else: 
				thickness_text = 1
				
			color_text = (0,255,255)
			image = cv2.putText(img = image,
						text = str(pixel_list[ix][iy]),
						org = (x + 5, y + 25),
						fontFace = cv2.FONT_HERSHEY_SIMPLEX,
						fontScale = 0.45, 
						color = color_text,
						thickness=thickness_text)
	return image
