# flake8: noqa
import os.path as osp
import sys
import subprocess
sys.path.append("./")
import models.utils.data
import models.utils.models
import models.SKDADDYS_Ehat
from .options.test import test_pipeline

if __name__ == '__main__':
    
    test_pipeline('./','options/test/SKDADDYS_Ehat_test.yml')
