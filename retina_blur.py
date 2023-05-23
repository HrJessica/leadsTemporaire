import argparse
import torch
import torch.backends.cudnn as cudnn
import numpy as np
from data import cfg
from layers.functions.prior_box import PriorBox
from utils.nms.py_cpu_nms import py_cpu_nms
from models.retinaface import RetinaFace
from utils.box_utils import decode, decode_landm
from filtre import anonymize_face_pixelate
from filtre import anonymize_face_simple
import time
import cv2

parser = argparse.ArgumentParser(description='Retinaface')

parser.add_argument('-m', '--trained_model', default='./weights/Final_Retinaface.pth',
                    type=str, help='Trained state_dict file path to open')
parser.add_argument('--cpu', action="store_true", default=False, help='Use cpu inference')
parser.add_argument('--confidence_threshold', default=0.7, type=float, help='confidence_threshold')
parser.add_argument('--top_k', default=5000, type=int, help='top_k')
parser.add_argument('--nms_threshold', default=0.3, type=float, help='nms_threshold')
parser.add_argument('--keep_top_k', default=750, type=int, help='keep_top_k')
parser.add_argument('-s', '--save_image', action="store_true", default=True, help='show detection results')
parser.add_argument('--vis_thres', default=0.7, type=float, help='visualization_threshold')
parser.add_argument("-g", "--gauss", action= 'store_true', default=False ,
	help="face blurring/anonymizing method")
#args = parser.parse_args()
args, _ = parser.parse_known_args()
print(type(args))
def check_keys(model, pretrained_state_dict):
    ckpt_keys = set(pretrained_state_dict.keys())
    model_keys = set(model.state_dict().keys())
    used_pretrained_keys = model_keys & ckpt_keys
    unused_pretrained_keys = ckpt_keys - model_keys
    missing_keys = model_keys - ckpt_keys
    print('Missing keys:{}'.format(len(missing_keys)))
    print('Unused checkpoint keys:{}'.format(len(unused_pretrained_keys)))
    print('Used keys:{}'.format(len(used_pretrained_keys)))
    assert len(used_pretrained_keys) > 0, 'load NONE from pretrained checkpoint'
    return True


def remove_prefix(state_dict, prefix):
    ''' Old style model is stored with all names of parameters sharing common prefix 'module.' '''
    print('remove prefix \'{}\''.format(prefix))
    f = lambda x: x.split(prefix, 1)[-1] if x.startswith(prefix) else x
    return {f(key): value for key, value in state_dict.items()}

def load_model(model, pretrained_path, load_to_cpu):
    print('Loading pretrained model from {}'.format(pretrained_path))
    if load_to_cpu:
        pretrained_dict = torch.load(pretrained_path, map_location=lambda storage, loc: storage)
    else:
        device = torch.cuda.current_device()
        pretrained_dict = torch.load(pretrained_path, map_location=lambda storage, loc: storage.cuda(device))
    if "state_dict" in pretrained_dict.keys():
        pretrained_dict = remove_prefix(pretrained_dict['state_dict'], 'module.')
    else:
        pretrained_dict = remove_prefix(pretrained_dict, 'module.')
    check_keys(model, pretrained_dict)
    model.load_state_dict(pretrained_dict, strict=False)
    return model

def detect(img_raw ,resize , device,net):
    img = np.float32(img_raw)

    im_height, im_width, _ = img.shape
    scale = torch.Tensor([img.shape[1], img.shape[0], img.shape[1], img.shape[0]])
    img -= (104, 117, 123)
    img = img.transpose(2, 0, 1)
    img = torch.from_numpy(img).unsqueeze(0)
    img = img.to(device)
    scale = scale.to(device)

    tic = time.time()
    loc, conf, landms = net(img)  # forward pass
    print('net forward time: {:.4f}'.format(time.time() - tic))
    priorbox = PriorBox(cfg, image_size=(im_height, im_width))
    priors = priorbox.forward()
    priors = priors.to(device)
    prior_data = priors.data
    boxes = decode(loc.data.squeeze(0), prior_data, cfg['variance'])
    boxes = boxes * scale / resize
    boxes = boxes.cpu().numpy()
    scores = conf.squeeze(0).data.cpu().numpy()[:, 1]
    landms = decode_landm(landms.data.squeeze(0), prior_data, cfg['variance'])
    scale1 = torch.Tensor([img.shape[3], img.shape[2], img.shape[3], img.shape[2],
                               img.shape[3], img.shape[2], img.shape[3], img.shape[2],
                               img.shape[3], img.shape[2]])
        
    scale1 = scale1.to(device)
    landms = landms * scale1 / resize
    landms = landms.cpu().numpy()

    # ignore low scores
    inds = np.where(scores > args.confidence_threshold)[0]
    boxes = boxes[inds]
    landms = landms[inds]
    scores = scores[inds]

    # keep top-K before NMS
    order = scores.argsort()[::-1][:args.top_k]
    boxes = boxes[order]
    landms = landms[order]
    scores = scores[order]

    # do NMS
    dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32, copy=False)
    keep = py_cpu_nms(dets, args.nms_threshold)
    # keep = nms(dets, args.nms_threshold,force_cpu=args.cpu)
    dets = dets[keep, :]
    landms = landms[keep]

    # keep top-K faster NMS
    dets = dets[:args.keep_top_k, :]
    landms = landms[:args.keep_top_k, :]

    dets = np.concatenate((dets, landms), axis=1)
    return dets
def draw_box(box ,img_raw):
    cv2.rectangle(img_raw, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
def get_bbox(dets , img_raw):
    box_prop = []
    for b in dets:
        if b[4] < args.vis_thres:
            break

        b = list(map(int, b[:4]))
        draw_box(b , img_raw)
        '''extraire le ROI'''
        xstart = b[0]
        xend = b[2]
        ystart = b[1]
        yend = b[3]
        face = img_raw[ystart:yend , xstart:xend]
        
        if args.gauss:
            face = anonymize_face_simple(face, factor=3.0)
		    # otherwise, we must be applying the "pixelated" face
		    # anonymization method 
        else:
            face = anonymize_face_pixelate(face,blocks=10)
		# store the blurred face in the output image
        img_raw[ystart:yend , xstart:xend] = face
        '''cv2.imshow('output', face)
        cv2.waitKey(0)'''
        box_prop.append(b)
    return box_prop

def retina(img_raw , device ,fileName,net):
    d = detect(img_raw , 1 , device,net)
    b_box = get_bbox(d , img_raw)
    return b_box
    
def split_video(video_path,device,result_path,net):
    capture = cv2.VideoCapture(video_path)
    frameNr = 0
    img_array = []
    while(True):
        #process frames
        success, frame = capture.read()
        if success:
            img_raw = frame
            name_img = 'frame'+ str(frameNr)
            retina(img_raw,device, name_img,net)
            height, width, layers = img_raw.shape
            size = (width,height)
            img_array.append(img_raw)
        else:
            break
        frameNr = frameNr+1
    out = cv2.VideoWriter(result_path,cv2.VideoWriter_fourcc(*'mp4v'),29,size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
    capture.release()

if __name__ == '__main__': 
    torch.set_grad_enabled(False)
    # net and model
    net = RetinaFace(phase="test")
    net = load_model(net, args.trained_model, args.cpu)
    net.eval()
    cudnn.benchmark = True  
    device = torch.device("cpu" if args.cpu else "cuda")
    net = net.to(device)
    