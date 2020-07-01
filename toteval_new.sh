echo "aqua Result"
bash eval2.sh ./aqua_Sol_cure_random_new aqua_random_res
bash eval2.sh ./aqua_Sol_cure_scaffold_new aqua_scaffold_res

echo "phys Result"
bash eval2.sh ./phys_Sol_cure_random_new phys_random_res
bash eval2.sh ./phys_Sol_cure_scaffold_new phys_scaffold_res

echo "esol Result"
bash eval2.sh ./esol_Sol_cure_random_new esol_random_res
bash eval2.sh ./esol_Sol_cure_scaffold_new esol_scaffold_res

echo "ochem Result"
bash eval2.sh ./ochem_Sol_cure_random_new ochem_random_res
bash eval2.sh ./ochem_Sol_cure_scaffold_new ochem_scaffold_res

echo "aqsol Result"
bash eval2.sh ./aqsol_Sol_cure_random_new aqsol_random_res
bash eval2.sh ./aqsol_Sol_cure_scaffold_new aqsol_scaffold_res

echo "chembl Result"
bash eval2.sh ./chembl_Sol_cure_random_new chembl_random_res
bash eval2.sh ./chembl_Sol_cure_scaffold_new chembl_scaffold_res

echo "kinect Result"
bash eval2.sh ./kinect_Sol_cure_random_new kinect_random_res
bash eval2.sh ./kinect_Sol_cure_scaffold_new kinect_scaffold_res
