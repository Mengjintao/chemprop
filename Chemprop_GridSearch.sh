#org_random
bash worker.sh ../org/aqua/aqua_org.csv     ../org/aqua/aqua_rdnorm.npz     aqua_org_random
bash worker.sh ../org/phys/phys_org.csv     ../org/phys/phys_rdnorm.npz     phys_org_random
bash worker.sh ../org/esol/esol_org.csv     ../org/esol/esol_rdnorm.npz     esol_org_random
bash worker.sh ../org/ochem/ochem_org.csv   ../org/ochem/ochem_rdnorm.npz   ochem_org_random
bash worker.sh ../org/aqsol/aqsol_org.csv   ../org/aqsol/aqsol_rdnorm.npz   aqsol_org_random
bash worker.sh ../org/ochem/chembl_org.csv  ../org/chembl/chembl_rdnorm.npz chembl_org_random
bash worker.sh ../org/kinect/kinect_org.csv ../org/kinect/kinect_rdnorm.npz kinect_org_random

#sca_random
bash worker.sh2 ../org/aqua/aqua_org.csv     ../org/aqua/aqua_rdnorm.npz     aqua_org_scaffold
bash worker.sh2 ../org/phys/phys_org.csv     ../org/phys/phys_rdnorm.npz     phys_org_scaffold
bash worker.sh2 ../org/esol/esol_org.csv     ../org/esol/esol_rdnorm.npz     esol_org_scaffold
bash worker.sh2 ../org/ochem/ochem_org.csv   ../org/ochem/ochem_rdnorm.npz   ochem_org_scaffold
bash worker.sh2 ../org/aqsol/aqsol_org.csv   ../org/aqsol/aqsol_rdnorm.npz   aqsol_org_scaffold
bash worker.sh2 ../org/ochem/chembl_org.csv  ../org/chembl/chembl_rdnorm.npz chembl_org_scaffold
bash worker.sh2 ../org/kinect/kinect_org.csv ../org/kinect/kinect_rdnorm.npz kinect_org_scaffold


#org_random
bash worker.sh ../cure/aqua_cure.csv   ../cure/aqua_rdnorm.npz   aqua_cure_random
bash worker.sh ../cure/phys_cure.csv   ../cure/phys_rdnorm.npz   phys_cure_random
bash worker.sh ../cure/esol_cure.csv   ../cure/esol_rdnorm.npz   esol_cure_random
bash worker.sh ../cure/ochem_cure.csv  ../cure/ochem_rdnorm.npz  ochem_cure_random
bash worker.sh ../cure/aqsol_cure.csv  ../cure/aqsol_rdnorm.npz  aqsol_cure_random
bash worker.sh ../cure/chembl_cure.csv ../cure/chembl_rdnorm.npz chembl_cure_random
bash worker.sh ../cure/kinect_cure.csv ../cure/kinect_rdnorm.npz kinect_cure_random

#sca_random
bash worker.sh2 ../cure/aqua_cure.csv   ../cure/aqua_rdnorm.npz   aqua_cure_scaffold
bash worker.sh2 ../cure/phys_cure.csv   ../cure/phys_rdnorm.npz   phys_cure_scaffold
bash worker.sh2 ../cure/esol_cure.csv   ../cure/esol_rdnorm.npz   esol_cure_scaffold
bash worker.sh2 ../cure/ochem_cure.csv  ../cure/ochem_rdnorm.npz  ochem_cure_scaffold
bash worker.sh2 ../cure/aqsol_cure.csv  ../cure/aqsol_rdnorm.npz  aqsol_cure_scaffold
bash worker.sh2 ../cure/chembl_cure.csv ../cure/chembl_rdnorm.npz chembl_cure_scaffold
bash worker.sh2 ../cure/kinect_cure.csv ../cure/kinect_rdnorm.npz kinect_cure_scaffold

