# [NTIRE 2024 Challenge on Efficient Super-Resolution](https://cvlai.net/ntire/2024/) @ [CVPR 2024](https://cvpr.thecvf.com/)

<div align=center>
<img src="https://github.com/Amazingren/NTIRE2024_ESR/blob/main/figs/logo.png" width="400px"/> 
</div>

## EHAT(Enhance Hybrid Attention Transformer for Image Super Resolution)
Transformer-based approach shows impressive performance in low-level visual tasks such as image super-resolution. However, we find that these networks can only utilize a limited spatial range of input information through attribution analysis. This means that the potential of Transformer is still underutilized in existing networks. In order to activate more input pixels for better reconstruction, we propose {a novel two-domain attention mixer} (EHAT) , which is based on a novel hybrid attention converter (HAT) developed by Xiangyu Chen et al. , based on the combination of channel-based attention and window-based self-attention scheme, {a new learning channel-based self-attention mechanism} (BSA) proposed by autonomous researchers is integrated, in addition, to better capture the global feature dependencies of spatial and channel dimensions, we introduce  {a dual-attention network} (DAnet) , which can be used to identify the global feature dependencies of spatial and channel dimensions, by adaptively integrating local features and global dependencies, we further expand the scale of the model to demonstrate that the performance of this task can be greatly improved.

 EHAT Neural Network Architecture Diagram is flllows
 <div align=center>
<img src="https://github.com/Amazingren/NTIRE2024_ESR/blob/main/figs/logo.png" width="200px"/> 
</div>
 new learning channel-based self-attention mechanism is follows
  <div align=center>
<img src="https://github.com/Amazingren/NTIRE2024_ESR/blob/main/figs/logo.png" width="200px"/> 
</div>
The final experimental comparison chart is follows
  <div align=center>
<img src="https://github.com/Amazingren/NTIRE2024_ESR/blob/main/figs/logo.png" width="200px"/> 
</div>
For more details, please refer to the <a href="https://github.com/Amazingren/NTIRE2024_ESR/blob/main/figs/logo.png">factsheet.pdf</a>.

## The Environments
The evaluation environments adopted by us is recorded in the `requirements.txt`. After you built your own basic Python setup via either *virtual environment* or *anaconda*, please try to keep similar to it via:

```pip install -r requirements.txt```

or take it as a reference based on your original environments.

## The Validation datasets
After downloaded all the necessary validate dataset ([DIV2K_LSDIR_valid_LR](https://drive.google.com/file/d/1YUDrjUSMhhdx1s-O0I1qPa_HjW-S34Yj/view?usp=sharing) and [DIV2K_LSDIR_valid_HR](https://drive.google.com/file/d/1z1UtfewPatuPVTeAAzeTjhEGk4dg2i8v/view?usp=sharing)), please organize them as follows:

```
|NTIRE2024_ESR_Challenge/
|--DIV2K_LSDIR_valid_HR/
|    |--000001.png
|    |--000002.png
|    |--...
|    |--000100.png
|    |--0801.png
|    |--0802.png
|    |--...
|    |--0900.png
|--DIV2K_LSDIR_valid_LR/
|    |--000001x4.png
|    |--000002x4.png
|    |--...
|    |--000100x4.png
|    |--0801x4.png
|    |--0802x4.png
|    |--...
|    |--0900.png
|--NTIRE2024_ESR/
|    |--...
|    |--test_demo.py
|    |--...
|--results/
|--......
```

## pre-trained model
The best weight files in the model zoo is<div>
<a href = "https://github.com/notiom/Ehat/releases/download/vv2.0.0/SKDADDYS_Ehat.pth">SKDADDYS_Ehat.pth</a>,Additionally, there are pre-trained weights for the hat network in the model zoo is <div>
<a href = "https://github.com/notiom/Ehat/releases/download/vv2.0.0/preHAT_L_x4.pth">preHAT_L_x4.pth</a>.

## How to test the EHat mode
1. `git clone https://github.com/notiom/Ehat.git`
2. run the command
    ```bash
    python test_demo.py --data_dir [path to your data dir] --save_dir [path to your save dir] --model_path [path to your model dir] --model_id 35
    ```
    - Be sure the change the directories `--data_dir`, `--save_dir` and `--model_path`.

## Organizers
- XiaoLe Yan (23220231151812@stu.xmu.edu.cn)
- Binren Li (Libinren@stu.xmu.edu.cn)
- Yubin Wei (YubinWei@stu.xmu.edu.cn)
- Haonan Chen (23220231151779@stu.xmu.edu.cn) 
- Siqi Zhang (23220231151819@stu.xmu.edu.cn)
- Sihan Chen (23220231151780@stu.xmu.edu.cn)

If you have any question, feel free to reach out the contact persons.
