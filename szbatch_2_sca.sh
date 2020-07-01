#!/bin/bash
#SBATCH --job-name=chemprop     # create a short name for your job
#SBATCH --cpus-per-task=32       # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --gres=dcu:4
#SBATCH --mem-per-cpu=2G       	# memory per cpu-core
#SBATCH --time=140:00:00         # total run time limit (HH:MM:SS)

batch_size=$1
hidden_size=$2
ffn_num_layers=$3
#ffn_hidden_size=$4
depth=$4
seed=$5
model=$6
name=$7
data=$8
feature=${9}

name0=$name'7'
name1=$name'9'
name2=$name'11'

model0=$model'7'
model1=$model'9'
model2=$model'11'

echo "batch_size = $batch_size"
echo "ffn_num_layers = $ffn_num_layers"
echo "hidden_size = $hidden_size"
echo "ffn_hidden_size = $ffn_hidden_size"
echo "depth = $depth"
echo "seed = $seed"
echo "data = $data"
echo "feature = $feature"
source activate mpnn

#time python train.py --gpu 0 --data_path $data  --features_generator rdkit_2d_normalized --save_dir $model0 --dataset_type regression --split_type scaffold_balanced  --num_folds 5 --metric rmse  --epochs 90 --batch_size $batch_size --no_features_scaling  --ensemble_size 5 --init_lr 0.0001 --max_lr 0.001 --final_lr 0.0001 --pytorch_seed $seed  --ffn_num_layers $ffn_num_layers --hidden_size $hidden_size --ffn_hidden_size 7 --depth $depth > $name0 2>&1 & 

#time python train.py --gpu 1 --data_path $data  --features_generator rdkit_2d_normalized --save_dir $model1 --dataset_type regression --split_type scaffold_balanced  --num_folds 5 --metric rmse  --epochs 90 --batch_size $batch_size --no_features_scaling  --ensemble_size 5 --init_lr 0.0001 --max_lr 0.001 --final_lr 0.0001 --pytorch_seed $seed  --ffn_num_layers $ffn_num_layers --hidden_size $hidden_size --ffn_hidden_size 9 --depth $depth > $name1 2>&1 & 

#time python train.py --gpu 2 --data_path $data  --features_generator rdkit_2d_normalized --save_dir $model2 --dataset_type regression --split_type scaffold_balanced  --num_folds 5 --metric rmse  --epochs 90 --batch_size $batch_size --no_features_scaling  --ensemble_size 5 --init_lr 0.0001 --max_lr 0.001 --final_lr 0.0001 --pytorch_seed $seed  --ffn_num_layers $ffn_num_layers --hidden_size $hidden_size --ffn_hidden_size 11 --depth $depth > $name2 2>&1 & 

#time python train.py --gpu 0 --data_path $data  --features_generator rdkit_2d_normalized --save_dir $model0 --dataset_type regression --split_type random  --num_folds 5 --metric rmse  --epochs 90 --batch_size $batch_size --no_features_scaling  --ensemble_size 5 --init_lr 0.0001 --max_lr 0.001 --final_lr 0.0001 --pytorch_seed $seed  --ffn_num_layers $ffn_num_layers --hidden_size $hidden_size --ffn_hidden_size 7 --depth $depth > $name0 2>&1 & 

#time python train.py --gpu 1 --data_path $data  --features_generator rdkit_2d_normalized --save_dir $model1 --dataset_type regression --split_type random  --num_folds 5 --metric rmse  --epochs 90 --batch_size $batch_size --no_features_scaling  --ensemble_size 5 --init_lr 0.0001 --max_lr 0.001 --final_lr 0.0001 --pytorch_seed $seed  --ffn_num_layers $ffn_num_layers --hidden_size $hidden_size --ffn_hidden_size 9 --depth $depth > $name1 2>&1 & 

#time python train.py --gpu 2 --data_path $data  --features_generator rdkit_2d_normalized --save_dir $model2 --dataset_type regression --split_type random  --num_folds 5 --metric rmse  --epochs 90 --batch_size $batch_size --no_features_scaling  --ensemble_size 5 --init_lr 0.0001 --max_lr 0.001 --final_lr 0.0001 --pytorch_seed $seed  --ffn_num_layers $ffn_num_layers --hidden_size $hidden_size --ffn_hidden_size 11 --depth $depth > $name2 2>&1 & 


time python train.py --gpu 0 --data_path $data  --features_path $feature --save_dir $model0 --dataset_type regression --split_type scaffold_balanced  --num_folds 8 --metric rmse  --epochs 90 --batch_size $batch_size --no_features_scaling  --ensemble_size 5 --init_lr 0.0001 --max_lr 0.001 --final_lr 0.0001 --pytorch_seed $seed  --ffn_num_layers $ffn_num_layers --hidden_size $hidden_size --ffn_hidden_size 7 --depth $depth --quiet > $name0 2>&1 & 

time python train.py --gpu 1 --data_path $data  --features_path $feature --save_dir $model1 --dataset_type regression --split_type scaffold_balanced  --num_folds 8 --metric rmse  --epochs 90 --batch_size $batch_size --no_features_scaling  --ensemble_size 5 --init_lr 0.0001 --max_lr 0.001 --final_lr 0.0001 --pytorch_seed $seed  --ffn_num_layers $ffn_num_layers --hidden_size $hidden_size --ffn_hidden_size 9 --depth $depth --quiet > $name1 2>&1 & 

time python train.py --gpu 2 --data_path $data  --features_path $feature --save_dir $model2 --dataset_type regression --split_type scaffold_balanced  --num_folds 8 --metric rmse  --epochs 90 --batch_size $batch_size --no_features_scaling  --ensemble_size 5 --init_lr 0.0001 --max_lr 0.001 --final_lr 0.0001 --pytorch_seed $seed  --ffn_num_layers $ffn_num_layers --hidden_size $hidden_size --ffn_hidden_size 11 --depth $depth --quiet > $name2 2>&1 & 
wait

