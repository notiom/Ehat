# [NTIRE 2024 Challenge on Efficient Super-Resolution](https://cvlai.net/ntire/2024/) @ [CVPR 2024](https://cvpr.thecvf.com/)

<div align=center>
<img src="https://raw.githubusercontent.com/notiom/Ehat/main/figs/logo.png" width="400px"/> 
</div>

## EHAT(Enhance Hybrid Attention Transformer for Image Super Resolution)
Transformer-based methods have demonstrated excellent performance in numerous vision tasks, including but not limited to image super-resolution reconstruction. However, we find that these networks can only utilize a limited spatial range of input information through attribution analysis. It means that the potential of Transformer is enormous. To overcome these limitations, we propose a novel network model Enhanced Hybrid Attention Transformer (EHAT) built upon the recent development of Hybrid Attention Transformer (HAT) by Xiangyu Chen et al., incorporating our independently designed innovative Branch Self-Attention mechanism (BSA). The importation of BSA aims to address the issues of overlooking the importance of some pathways and having a single-weight setting for pathway in traditional approaches. Compared to simply setting pathway weights to fixed values, BSA dynamically adjusts their weights by learning mechanisms to accurately identify the importance of each pathway, so that to capture key features in the data more precisely. Ideally, BSA assigns larger weight coefficients to pathways with more significant features, thereby effectively enhancing the overall network performance. Through extensive empirical validation, we successfully demonstrate the effectiveness of BSA in improving network performance.

 EHAT Neural Network Architecture Diagram is flllows
 <div align=center>
<img src="https://raw.githubusercontent.com/notiom/Ehat/main/figs/fig1.png" height="400px" width="600px"/> 
</div>

 new learning channel-based self-attention mechanism is follows
  <div align=center>
<img src="https://raw.githubusercontent.com/notiom/Ehat/main/figs/fig2.png" height="400px" width="600px"/> 
</div>

The final experimental comparison chart is follows
  <div align=center>
<img src="https://raw.githubusercontent.com/notiom/Ehat/main/figs/fig3.jpg" height="400px" width="600px"/> 
</div>

For more details, please refer to the <a href="https://github.com/notiom/Ehat/blob/main/factsheet.pdf">factsheet.pdf</a>.

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
The best weight files in the model zoo is<div><a href = "https://github.com/notiom/Ehat/releases/download/vv2.0.0/SKDADDYS_Ehat.pth">SKDADDYS_Ehat.pth</a>,Additionally, there are pre-trained weights for the hat network in the model zoo is <div><a href = "https://github.com/notiom/Ehat/releases/download/vv2.0.0/preHAT_L_x4.pth">preHAT_L_x4.pth</a>.

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
