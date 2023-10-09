# bash script to run generate_mirror.py using sbatch and poetry on the rockefeller cluster

#!/bin/bash
# get timestamp
timestamp=$(date +%Y%m%d_%H%M%S)

sbatch <<EOT
#!/bin/bash

# Set sbatch options on node node062 (bigmem)
#SBATCH --job-name=generate_mirror
#SBATCH --output="generate_mirror"${timestamp}".out"
#SBATCH --error="generate_mirror"${timestamp}".err"
#SBATCH --time=10:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=${1:-5}
#SBATCH --tasks-per-node=${1:-5}
#SBATCH --cpus-per-task=1
#SBATCH --nodelist=node062

# Run generate_mirror.py
poetry run python generate_mirror.py -n ${1:-5} -s ${2:-False} -l ${3:-left}

# End of script

## Notes
# To run this script, use the following command:
# sbatch scripts/generate_mirror.sh <num_tasks> <symmetric(True/False)> <left_right(left/right)>
# where <num_tasks> is the number of tasks to run in parallel
# and <symmetric> is whether to use symmetric or asymmetric mirrors
# and <left_right> is whether to use left or right mirrors
# If no arguments are provided, the default values are used

# To check the status of the job, use the following command:
# squeue -u <username>

# To cancel the job, use the following command:
# scancel <job_id>

# To check the output of the job, use the following command:
# cat generate_mirror.out

# To check the error messages of the job, use the following command:
# cat generate_mirror.err

# End of Notes

EOT