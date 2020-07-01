echo "aqua Result"
bash eval2.sh ./aqua_Sol_cure2_random aqua_random_res
bash eval2.sh ./aqua_Sol_cure2_scaffold aqua_scaffold_res

echo "phys Result"
bash eval2.sh ./phys_Sol_cure2_random phys_random_res
bash eval2.sh ./phys_Sol_cure2_scaffold phys_scaffold_res

echo "esol Result"
bash eval2.sh ./esol_Sol_cure1_random esol_random_res
bash eval2.sh ./esol_Sol_cure1_scaffold esol_scaffold_res

echo "ochem Result"
bash eval2.sh ./ochem_Sol_cure1_random ochem_random_res
bash eval2.sh ./ochem_Sol_cure1_scaffold ochem_scaffold_res

echo "aqsol Result"
bash eval2.sh ./aqsol_Sol_cure1_random aqsol_random_res
bash eval2.sh ./aqsol_Sol_cure1_scaffold aqsol_scaffold_res

echo "chembl Result"
bash eval2.sh ./chembl_Sol_cure1_random chembl_random_res
bash eval2.sh ./chembl_Sol_cure1_scaffold chembl_scaffold_res

echo "kinect Result"
bash eval2.sh ./kinect_Sol_cure1_random kinect_random_res
bash eval2.sh ./kinect_Sol_cure1_scaffold kinect_scaffold_res
