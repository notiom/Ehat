from copy import deepcopy
import os.path
import logging
import torch
import argparse
import json
import glob

from pprint import pprint
from fvcore.nn import FlopCountAnalysis
from utils.model_summary import get_model_activation, get_model_flops
from utils import utils_logger
from utils import utils_image as util

from torch.nn import functional as F
#The following part is added by myself.
from basicsr.utils import FileClient,imfrombytes,tensor2img,img2tensor
from basicsr.utils import imwrite


def select_model(args, device):
    # Model ID is assigned according to the order of the submissions.
    # Different networks are trained with input range of either [0,1] or [0,255]. The range is determined manually.
    model_id = args.model_id

    if model_id == 35:
        from models.SKDADDYS_Ehat import HAT
        name, data_range = f"{model_id:02}_RLFN_baseline", 255.0
        #need to download the weights file.
        # model_path = os.path.join('model_zoo', 'SKDADDYS_Ehat.pth')
        model_path = args.model_path
        model = HAT(upscale=4,
                    in_chans=3,
                    img_size=64,
                    window_size=16,
                    compress_ratio=3,
                    squeeze_factor=30,
                    conv_scale=0.01,
                    overlap_ratio=0.5,
                    img_range=1.,
                    depths=[6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
                    embed_dim=180,
                    num_heads=[6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
                    mlp_ratio=2,
                    upsampler='pixelshuffle',
                    resi_connection='1conv')
        param_key='params'
        load_net = torch.load(model_path, map_location=lambda storage, loc: storage)
        if param_key is not None:
            if param_key not in load_net and 'params' in load_net:
                param_key = 'params'
            load_net = load_net[param_key]
        # remove unnecessary 'module.'
        for k, v in deepcopy(load_net).items():
            if k.startswith('module.'):
                load_net[k[7:]] = v
                load_net.pop(k)
        model.load_state_dict(load_net, strict=True)
        # model.load_state_dict(torch.load(model_path), strict=True)
    else:
        raise NotImplementedError(f"Model {model_id} is not implemented.")

    # print(model)
    model.eval()
    tile = None
    for k, v in model.named_parameters():
        v.requires_grad = False
    model = model.to(device)
    return model, name, data_range, tile


def select_dataset(data_dir, mode):
    # inference on the LSDIR_DIV2K_test set
    if mode == "test":
        path = [
            (
                p.replace("_HR", "_LR").replace(".png", "x4.png"),
                p
            ) for p in sorted(glob.glob(os.path.join(data_dir, "LSDIR_DIV2K_test_HR/*.png")))
        ]

    # inference on the LSDIR_DIV2K_valid set
    elif mode == "valid":
        path = [
            (
                p.replace("_HR", "_LR").replace(".png", "x4.png"),
                p
            ) for p in sorted(glob.glob(os.path.join(data_dir, "LSDIR_DIV2K_valid_HR/*.png")))
        ]
    else:
        raise NotImplementedError(f"{mode} is not implemented in select_dataset")
    
    return path


def forward(img_lq, model, tile=None, tile_overlap=32, scale=4):
    if tile is None:
        # test the image as a whole
        output = model(img_lq)
    else:
        # test the image tile by tile
        b, c, h, w = img_lq.size()
        tile = min(tile, h, w)
        tile_overlap = tile_overlap
        sf = scale

        stride = tile - tile_overlap
        h_idx_list = list(range(0, h-tile, stride)) + [h-tile]
        w_idx_list = list(range(0, w-tile, stride)) + [w-tile]
        E = torch.zeros(b, c, h*sf, w*sf).type_as(img_lq)
        W = torch.zeros_like(E)

        for h_idx in h_idx_list:
            for w_idx in w_idx_list:
                in_patch = img_lq[..., h_idx:h_idx+tile, w_idx:w_idx+tile]
                out_patch = model(in_patch)
                out_patch_mask = torch.ones_like(out_patch)

                E[..., h_idx*sf:(h_idx+tile)*sf, w_idx*sf:(w_idx+tile)*sf].add_(out_patch)
                W[..., h_idx*sf:(h_idx+tile)*sf, w_idx*sf:(w_idx+tile)*sf].add_(out_patch_mask)
        output = E.div_(W)

    return output
class DataProcess:
    def __init__(self):
        self.window_size = 16
        self.mod_pad_h = 0
        self.mod_pad_w = 0
        self.scale = 4
        self.lq = None
        self.output = None
    def pre_process(self,img_lq):
        # pad to multiplication of window_size
        self.lq = img_lq
        _, _, h, w = self.lq.size()
        mod_pad_h, mod_pad_w = 0, 0
        _, _, h, w = img_lq.size()
        if h % self.window_size != 0:
            self.mod_pad_h = self.window_size - h % self.window_size
        if w % self.window_size != 0:
            self.mod_pad_w = self.window_size - w % self.window_size
        self.img = F.pad(self.lq, (0, self.mod_pad_w, 0, self.mod_pad_h), 'reflect')
        return self.img
    def post_process(self,img_sr):
        self.output = img_sr
        _, _, h, w = self.output.size()
        self.output = self.output[:, :, 0:h - self.mod_pad_h * self.scale, 0:w - self.mod_pad_w * self.scale]
        return self.output

class PairedImageDataset(torch.utils.data.Dataset):
    def __init__(self):
        super(PairedImageDataset, self).__init__()
        self.file_client = FileClient()

def normalsize_change(img_lr,img_hr,file_client,scale = 4):

    # Load gt and lq images. Dimension order: HWC; channel order: BGR;
    # image range: [0, 1], float32.
    img_bytes = file_client.get(img_hr, 'gt')
    img_hr = imfrombytes(img_bytes, float32=True)
    img_bytes = file_client.get(img_lr, 'lq')
    img_lr = imfrombytes(img_bytes, float32=True)

    img_hr = img_hr[0:img_lr.shape[0] * scale, 0:img_lr.shape[1] * scale, :]
    # crop the unmatched GT images during validation or testing, especially for SR benchmark datasets

    # BGR to RGB, HWC to CHW, numpy to tensor
    img_hr, img_lr = img2tensor([img_hr, img_lr], bgr2rgb=True, float32=True)
    return img_lr,img_hr

def run(model, model_name, data_range, tile, logger, device, args, mode="test"):

    sf = 4
    border = sf
    results = dict()
    results[f"{mode}_runtime"] = []
    results[f"{mode}_psnr"] = []
    if args.ssim:
        results[f"{mode}_ssim"] = []
    # results[f"{mode}_psnr_y"] = []
    # results[f"{mode}_ssim_y"] = []

    # --------------------------------
    # dataset path
    # --------------------------------
    data_path = select_dataset(args.data_dir, mode)
    save_path = os.path.join(args.save_dir, model_name, mode)
    util.mkdir(save_path)
    # create test dataset and dataloader
    
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    
    for i, (img_lr, img_hr) in enumerate(data_path):
        dataprocess = DataProcess()

        # --------------------------------
        # (1) img_lr
        # --------------------------------
        file_client = FileClient()
        img_name, ext = os.path.splitext(os.path.basename(img_hr))
        img_lr,img_hr = normalsize_change(img_lr,img_hr,file_client)
        img_lr = img_lr.unsqueeze(0)
        img_lr = img_lr.to(device)

        # --------------------------------
        # (2) img_sr
        # --------------------------------
        start.record()
        img_lr_pre = dataprocess.pre_process(img_lr)
        img_sr_pre = forward(img_lr_pre, model, tile)
        img_sr = dataprocess.post_process(img_sr_pre)
        img_sr = tensor2img(img_sr)
        del dataprocess
        end.record()
        torch.cuda.synchronize()
        results[f"{mode}_runtime"].append(start.elapsed_time(end))  # milliseconds
        # img_sr = util.tensor2uint(img_sr, data_range)

        # --------------------------------
        # (3) img_hr
        # --------------------------------
        # img_hr = util.imread_uint(img_hr, n_channels=3)
        # img_hr = img_hr.squeeze()
        # img_hr = util.modcrop(img_hr, sf)
        img_hr = tensor2img(img_hr)

        # --------------------------------
        # PSNR and SSIM
        # --------------------------------

        # print(img_sr.shape, img_hr.shape)
        psnr = util.calculate_psnr(img_sr, img_hr, border=border)
        results[f"{mode}_psnr"].append(psnr)

        if args.ssim:
            ssim = util.calculate_ssim(img_sr, img_hr, border=border)
            results[f"{mode}_ssim"].append(ssim)
            logger.info("{:s} - PSNR: {:.2f} dB; SSIM: {:.4f}.".format(img_name + ext, psnr, ssim))
        else:
            logger.info("{:s} - PSNR: {:.2f} dB".format(img_name + ext, psnr))

        # if np.ndim(img_hr) == 3:  # RGB image
        #     img_sr_y = util.rgb2ycbcr(img_sr, only_y=True)
        #     img_hr_y = util.rgb2ycbcr(img_hr, only_y=True)
        #     psnr_y = util.calculate_psnr(img_sr_y, img_hr_y, border=border)
        #     ssim_y = util.calculate_ssim(img_sr_y, img_hr_y, border=border)
        #     results[f"{mode}_psnr_y"].append(psnr_y)
        #     results[f"{mode}_ssim_y"].append(ssim_y)
        # print(os.path.join(save_path, img_name+ext))
        imwrite(img_sr, os.path.join(save_path, img_name+ext))

    results[f"{mode}_memory"] = torch.cuda.max_memory_allocated(torch.cuda.current_device()) / 1024 ** 2
    results[f"{mode}_ave_runtime"] = sum(results[f"{mode}_runtime"]) / len(results[f"{mode}_runtime"]) #/ 1000.0
    results[f"{mode}_ave_psnr"] = sum(results[f"{mode}_psnr"]) / len(results[f"{mode}_psnr"])
    if args.ssim:
        results[f"{mode}_ave_ssim"] = sum(results[f"{mode}_ssim"]) / len(results[f"{mode}_ssim"])
    # results[f"{mode}_ave_psnr_y"] = sum(results[f"{mode}_psnr_y"]) / len(results[f"{mode}_psnr_y"])
    # results[f"{mode}_ave_ssim_y"] = sum(results[f"{mode}_ssim_y"]) / len(results[f"{mode}_ssim_y"])
    logger.info("{:>16s} : {:<.3f} [M]".format("Max Memory", results[f"{mode}_memory"]))  # Memery
    logger.info("------> Average runtime of ({}) is : {:.6f} milliseconds".format("test" if mode == "test" else "valid", results[f"{mode}_ave_runtime"]))
    logger.info("------> Average PSNR of ({}) is : {:.6f} dB".format("test" if mode == "test" else "valid", results[f"{mode}_ave_psnr"]))

    return results
                     
def main(args):

    utils_logger.logger_info("NTIRE2024-EfficientSR", log_path="NTIRE2024-EfficientSR.log")
    logger = logging.getLogger("NTIRE2024-EfficientSR")

    # --------------------------------
    # basic settings
    # --------------------------------
    torch.cuda.current_device()
    torch.cuda.empty_cache()
    torch.backends.cudnn.benchmark = False
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    json_dir = os.path.join(os.getcwd(), "results.json")
    if not os.path.exists(json_dir):
        results = dict()
    else:
        with open(json_dir, "r") as f:
            results = json.load(f)

    # --------------------------------
    # load model
    # --------------------------------
    model, model_name, data_range, tile = select_model(args, device)
    logger.info(model_name)

    # if model not in results:
    if True:
        # --------------------------------
        # restore image
        # --------------------------------

        # inference on both the DIV2K and LSDIR validate sets
        valid_results = run(model, model_name, data_range, tile, logger, device, args, mode="valid")
        # record PSNR, runtime
        results[model_name] = valid_results

        # inference conducted by the organizer
        if args.include_test:
            test_results = run(model, model_name, data_range, tile, logger, device, args, mode="test")
            results[model_name].update(test_results)

        input_dim = (3, 256, 256)  # set the input dimension
        activations, num_conv = get_model_activation(model, input_dim)
        activations = activations/10**6
        logger.info("{:>16s} : {:<.4f} [M]".format("#Activations", activations))
        logger.info("{:>16s} : {:<d}".format("#Conv2d", num_conv))

        # The FLOPs calculation in previous NTIRE_ESR Challenge
        # flops = get_model_flops(model, input_dim, False)
        # flops = flops/10**9
        # logger.info("{:>16s} : {:<.4f} [G]".format("FLOPs", flops))

        # fvcore is used in NTIRE2024_ESR for FLOPs calculation
        input_fake = torch.rand(1, 3, 256, 256).to(device)
        flops = FlopCountAnalysis(model, input_fake).total()
        flops = flops/10**9
        logger.info("{:>16s} : {:<.4f} [G]".format("FLOPs", flops))

        num_parameters = sum(map(lambda x: x.numel(), model.parameters()))
        num_parameters = num_parameters/10**6
        logger.info("{:>16s} : {:<.4f} [M]".format("#Params", num_parameters))
        results[model_name].update({"activations": activations, "num_conv": num_conv, "flops": flops, "num_parameters": num_parameters})

        with open(json_dir, "w") as f:
            json.dump(results, f)
    if args.include_test:
        fmt = "{:20s}\t{:10s}\t{:10s}\t{:14s}\t{:14s}\t{:14s}\t{:10s}\t{:10s}\t{:8s}\t{:8s}\t{:8s}\n"
        s = fmt.format("Model", "Val PSNR", "Test PSNR", "Val Time [ms]", "Test Time [ms]", "Ave Time [ms]",
                       "Params [M]", "FLOPs [G]", "Acts [M]", "Mem [M]", "Conv")
    else:
        fmt = "{:20s}\t{:10s}\t{:14s}\t{:10s}\t{:10s}\t{:8s}\t{:8s}\t{:8s}\n"
        s = fmt.format("Model", "Val PSNR", "Val Time [ms]", "Params [M]", "FLOPs [G]", "Acts [M]", "Mem [M]", "Conv")
    for k, v in results.items():
        val_psnr = f"{v['valid_ave_psnr']:2.2f}"
        val_time = f"{v['valid_ave_runtime']:3.2f}"
        mem = f"{v['valid_memory']:2.2f}"
        
        num_param = f"{v['num_parameters']:2.3f}"
        flops = f"{v['flops']:2.2f}"
        acts = f"{v['activations']:2.2f}"
        conv = f"{v['num_conv']:4d}"
        if args.include_test:
            # from IPython import embed; embed()
            test_psnr = f"{v['test_ave_psnr']:2.2f}"
            test_time = f"{v['test_ave_runtime']:3.2f}"
            ave_time = f"{(v['valid_ave_runtime'] + v['test_ave_runtime']) / 2:3.2f}"
            s += fmt.format(k, val_psnr, test_psnr, val_time, test_time, ave_time, num_param, flops, acts, mem, conv)
        else:
            s += fmt.format(k, val_psnr, val_time, num_param, flops, acts, mem, conv)
    with open(os.path.join(os.getcwd(), 'results.txt'), "w") as f:
        f.write(s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("NTIRE2024-EfficientSR")
    parser.add_argument("--data_dir", default="../datasets", type=str)
    parser.add_argument("--save_dir", default="../results", type=str)
    parser.add_argument("--model_path", default="./model_zoo/SKDADDYS_Ehat.pth", type=str)
    parser.add_argument("--model_id", default=35, type=int)
    parser.add_argument("--include_test", action="store_true", help="Inference on the DIV2K test set")
    parser.add_argument("--ssim", action="store_true", help="Calculate SSIM")

    args = parser.parse_args()
    print(args)
    main(args)
