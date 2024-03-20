# flake8: noqa
import os.path as osp
import sys
sys.path.append("./")
import models.utils.data
import models.utils.models
import models.SKDADDYS_Ehat
from options.train.train_pipeline import train_pipeline

if __name__ == '__main__':
    
    train_pipeline('./','options/train/SKDADDYS_Ehat_train.yml')
