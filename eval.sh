#!/bin/bash
function getbest(){
echo $1
echo "hello"
cmd="grep Overall $1"
echo $cmd
$cmd
#| cut -d" " -f 1,5- | sort -k 2 | head | cut -d"/" -f 3 |  cut -d":" -f 1 | cut -d"." -f 1 | head -n 1
echo $hht

#head=$(grep "Overall" $fd | cut -d" " -f 1,5- | sort -k 2 | head | cut -d"/" -f 3 |  cut -d":" -f 1 | cut -d"." -f 1 | head -n 1)
#end=$(grep "Overall"  $fd | cut -d" " -f 1,5- | sort -k 2 | head | cut -d"/" -f 3 |  cut -d":" -f 1 | cut -d"." -f 2 | head -n 1)
#end=${end:3}
#echo $head
#echo $end
#file=$head"_model.pt"$end
#echo $file
return $file
}

ret=$(getbest ./ochem_Sol_cure1_scaffoldmodel/*)




echo $ret
#python predict.py --gpu 0 --test_path ./test_bdz.csv --features_path ./test_bdz_rdnorm.npz --checkpoint_dir ./ochem_Sol_cure1_scaffoldmodel/16_11_3_2_0_model.pt7 --no_features_scaling --preds_path out.txt
#python pred_r2.py out.txt
