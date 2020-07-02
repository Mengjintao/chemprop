echo "aqua Result"
bash eval2.sh ./aqua_org_random   aqua_random_res
bash eval2.sh ./aqua_org_scaffold aqua_scaffold_res

echo "phys Result"
bash eval2.sh ./phys_org_random   phys_random_res
bash eval2.sh ./phys_org_scaffold phys_scaffold_res

echo "esol Result"
bash eval2.sh ./esol_org_random   esol_random_res
bash eval2.sh ./esol_org_scaffold esol_scaffold_res

echo "ochem Result"
bash eval2.sh ./ochem_org_random   ochem_random_res
bash eval2.sh ./ochem_org_scaffold ochem_scaffold_res

echo "aqsol Result"
bash eval2.sh ./aqsol_org_random   aqsol_random_res
bash eval2.sh ./aqsol_org_scaffold aqsol_scaffold_res

echo "chembl Result"
bash eval2.sh ./chembl_org_random   chembl_random_res
bash eval2.sh ./chembl_org_scaffold chembl_scaffold_res

echo "kinect Result"
bash eval2.sh ./kinect_org_random   kinect_random_res
bash eval2.sh ./kinect_org_scaffold kinect_scaffold_res
