#!/bin/bash
echo $1
model=$1
name=$2
head=$(grep -r "Overall" $model | cut -d" " -f 1,5- | sort -k 2 | head | cut -d"/" -f 3 |  cut -d":" -f 1 | cut -d"." -f 1 | head -n 1)
end=$(grep -r "Overall"  $model | cut -d" " -f 1,5- | sort -k 2 | head | cut -d"/" -f 3 |  cut -d":" -f 1 | cut -d"." -f 2 | head -n 1)
end=${end:3}
file=$model"model/"$head"_model.pt"$end
echo $file
python predict.py --gpu 0 --test_path ./test_all.csv --features_path ./test_all_rdnorm.npz --checkpoint_dir $file --no_features_scaling --preds_path out.txt
python pred_r2.py out.txt $name
