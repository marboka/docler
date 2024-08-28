import math
from typing import Dict

def modified_rmse(gt_dict:Dict, pred_dict:Dict) -> int:
    metric = 0
    for key_gt in gt_dict.keys():
        if key_gt in pred_dict.keys():
            metric += math.sqrt((gt_dict[key_gt]-pred_dict[key_gt])**2) *gt_dict[key_gt]
        else:
            metric += 1
    metric=metric/len(gt_dict.keys())
    metric = 1-metric
    return metric


if __name__ == '__main__':
    gt = {'a':0.99, 'b': 0.82, 'c':0.78, 'd':0.76, 'e':0.74}
    p1 = {'a':1, 'b': 0.56, 'c':0.49, 'd':0.44, 'e':0.36}
    p2 = {'a':1, 'b': 0.56, 'c':0.49, 'd':0.44, 'f':0.36}
    p3 = {'a':1, 'b': 0.56, 'c':0.49, 'd':0.74, 'f':0.36}
    p4 = {}

    print(modified_rmse(gt, gt)) # should be 1
    print(modified_rmse(gt, p1)) # between 0 and 1
    print(modified_rmse(gt, p2)) # lower then the previos as we don't have e
    print(modified_rmse(gt, p3)) # higher then the previous
    print(modified_rmse(gt, p4)) # 0