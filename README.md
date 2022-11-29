# aws-boto-functions
Bunch of aws-boto3 functions that will make a DevOps Engineer's life easy.


### Pre-requisites
  1. Latest version of AWS CLI tools installed - https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
  2. AWS profiles (credentials and config files) configued
  3. Python v3.10 or above installed
  4. Additional python modules to install
     - `pip install boto3`
     - `pip install colorama`

### Assumptions
This python script has been tested on Windows operating system. Although the script might work as-is on a non-windows platform, minor changes may be needed to get the script working.


### List of AWS Functions
  - RDS
    - [scripts/list_rds_instances.py](Obtain list of all the RDS instances for every given region for every given AWS account)
    - [scripts/list_rds_snapshots.py](Obtain list of all the RDS Snapshots for every given region for every given AWS account)