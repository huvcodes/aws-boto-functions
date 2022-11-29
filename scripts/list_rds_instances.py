#!/usr/bin/env python3
# 
# ====================================================================================================================
# Python script to list RDS Instances for every given region and every given account
# ====================================================================================================================
#
# ASSUMPTIONS & PRE-REQUISITES:
# --------------------------------------------------------
# 
# Pre-Requisites:
# -----------------
# 1. Latest version of AWS CLI installed
# 2. AWS profiles (CLI credentials) coonfigured
# 3. Python v3.6 or above installed
# 4. Additional python modules to install
#   a. pip install boto3
#   b. pip install colorama
#
#
# Assumptions:
# -----------------
# This python script has been tested on Windows operating system.
# Although the script might work as-is on a non-windows platform, minor changes may be needed to get the script working.
#

import boto3
import colorama
import csv

from botocore.exceptions import ClientError
from botocore.exceptions import ProfileNotFound
from colorama import Fore
from colorama import Style
from datetime import datetime

# Initiating the coloroma class and auto reset the color codes after every print line
colorama.init(autoreset = True)

# List of AWS accounts/profiles set in your .aws/credentials and .aws/config files
profiles = ["dev_account", "test_account", "prod_account"]

# List of AWS regions to traverse through
aws_regions = [
    "ap-east-1",        # A.Pacific     ---     Hong Kong
    "ap-south-1",       # A.Pacific     ---     Mumbai
    "ap-northeast-1",   # A.Pacific     ---     Tokyo
    "ap-northeast-2",   # A.Pacific     ---     Seoul
    "ap-northeast-3",   # A.Pacific     ---     Osaka
    "ap-southeast-1",   # A.Pacific     ---     Singapore
    "ap-southeast-2",   # A.Pacific     ---     Sydney
    "ca-central-1",     # N.America     ---     Canada - Central
    "eu-central-1",     # Europe        ---     Frankfurt
    "eu-north-1",       # Europe        ---     Stockholm
    "eu-west-1",        # Europe        ---     Ireland
    "eu-west-2",        # Europe        ---     London
    "eu-west-3",        # Europe        ---     Paris
    "me-south-1",       # Middle East   ---     Bahrain
    "sa-east-1",        # S.America     ---     Sau Paulo 
    "us-east-1",        # N.America     ---     US - N.Virginia
    "us-east-2",        # N.America     ---     US - Ohio
    "us-west-1",        # N.America     ---     US - N.California
    "us-west-2"         # N.America     ---     US - Oregon
]


def main():
    try:
        for aws_profile in profiles:
            try:
                # Establish AWS CLI session
                session = boto3.Session(profile_name=aws_profile)
            except ProfileNotFound:
                print(f"{Fore.RED}{Style.BRIGHT}\nThe specified profile ['{aws_profile}'] is not available in your aws credentials file. Please check.")
                print(f"{Fore.RED}{Style.BRIGHT}Aborting execution here.\n")

            # List to populate RDS instances and write to csv
            db_instances_list = []
        
            # CSV file with RDS instance details
            output_csv = aws_profile + '_rds_instance_details_' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.csv'
        
            # Iterate through every region
            for region in aws_regions:
                # Instantiate AWS RDS client
                rds_client = session.client('rds', region)

                print(f'\n==============================================================================================================================================================')
                print(f'Checking for RDS instances in [{region}] region for [{aws_profile}] account\n')
                # Query to describe all RDS instances
                response = rds_client.describe_db_instances()
                
                if (len(response['DBInstances']) == 0):
                    print(f'0 RDS instances found in the region [{region}] for [{aws_profile}] account')
                    print(f'==============================================================================================================================================================\n\n')
                else:
                    # Reset arrays to zero for every region
                    unencrypted_instances = []
                    public_facing_instances = []
                    
                    print(f"{len(response['DBInstances'])} RDS instance(s) found in the region [{region}] for [{aws_profile}] account\n")
                    for instance in response['DBInstances']:
                        print('Instance: {0:40} Encrypted: {1} \t\t\t Public_Access: {2}'.format(
                            instance['DBInstanceIdentifier'], 
                            instance['StorageEncrypted'],
                            instance['PubliclyAccessible'])
                        )
                        
                        if instance['StorageEncrypted'] == False:
                            unencrypted_instances.append(instance)
                        
                        if instance['PubliclyAccessible'] == True:
                            public_facing_instances.append(instance)
                        
                        db_instances_list.append({
                            'AWS Region': region,
                            'DB Instance Identifier': instance['DBInstanceIdentifier'],
                            'Storage Encrypted': instance['StorageEncrypted'],
                            'Publicly Accessible': instance['PubliclyAccessible']
                        })
                        
                    print('\nDetected %d unencrypted RDS instances!' % len(unencrypted_instances))
                    print('\nDetected %d public facing RDS instances!' % len(public_facing_instances))
                    print(f'==============================================================================================================================================================\n\n')

            # Write output to csv file.
            print(f'\nWriting the output of {aws_profile} account to CSV file..')
            csv_column_header = [
                'AWS Region',
                'DB Instance Identifier',
                'Storage Encrypted',
                'Publicly Accessible'
            ]
            try:
                with open(output_csv, 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=csv_column_header)
                    writer.writeheader()
                    writer.writerows(db_instances_list)
                print(f'Details written to csv file [{output_csv}]\n')
            except IOError as e:
                print(f"{Fore.RED}{Style.BRIGHT}\nERROR: {e.response}\n")
                print(e.response['Error']['Code'])
                exit(1)

    except ClientError as error:
        print(f"{Fore.RED}{Style.BRIGHT}\nERROR: {error.response}\n")
        print(error.response['Error']['Code'])
        exit(1)

if __name__ == '__main__':
    main()