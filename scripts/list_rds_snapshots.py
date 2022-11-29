#!/usr/bin/env python3
# 
# ====================================================================================================================
# Python script to list RDS Snapshots for every given region and every given account
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

            # Lists to populate snapshots and write to csv
            instance_snapshots_list = []
            cluster_snapshots_list = []
        
            # CSV file with RDS Snapshots details
            output_csv = aws_profile + '_rds_snapshots_details_' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.csv'
        
            # Iterate through every region
            for region in aws_regions:
                # Instantiate AWS RDS client
                rds_client = session.client('rds', region)

                # -----------------------------------------------------------------------------------------
                # Block to populate RDS Instance Snapshots - Begin

                print(f'\n==============================================================================================================================================================')
                print(f'Checking for RDS Instance Snapshots in [{region}] region for [{aws_profile}] account\n')
                
                # Query to describe all RDS DB Instances Snapshots
                instance_response = rds_client.describe_db_snapshots()
                
                if (len(instance_response['DBSnapshots']) == 0):
                    print(f'0 RDS Instance Snapshots found in the region [{region}] for [{aws_profile}] account\n\n')
                else:
                    # Reset list to zero for every region
                    unencrypted_snapshots = []
                    
                    print(f"{len(instance_response['DBSnapshots'])} RDS snapshot(s) found in the region [{region}]for [{aws_profile}] account\n")
                    for snapshot in instance_response['DBSnapshots']:
                        print('Snapshot: {0:60} DBInstanceIdentifier: {1} \t\t\t SnapshotType: {2} \t\t Encrypted: {3}'.format(
                            snapshot['DBSnapshotIdentifier'],
                            snapshot['DBInstanceIdentifier'],
                            snapshot['SnapshotType'],
                            snapshot['Encrypted'])
                        )
                        
                        if snapshot['Encrypted'] == False:
                            unencrypted_snapshots.append(snapshot)
                        
                        # Code snippet to check if any RDS snapshots can be publicly accessible
                        # snapshot_attributes = rds_client.describe_db_snapshot_attributes(DBSnapshotIdentifier=snapshot['DBSnapshotIdentifier'])
                        # print("RDS Snapshot Name: "+  snapshot_attributes['DBSnapshotAttributesResult']['DBSnapshotIdentifier'], end='' )
                        # for item in attributes['DBSnapshotAttributesResult']['DBSnapshotAttributes']:
                            # print(" \t Snapshot Available to { if value is all then its public} : ",end=''); print( each['AttributeValues'])
                        
                        instance_snapshots_list.append({
                            'AWS Region': region,
                            'DB Identifier': snapshot['DBInstanceIdentifier'],
                            'Snapshot Identifier': snapshot['DBSnapshotIdentifier'],
                            'Snapshot Creation Time': snapshot['SnapshotCreateTime'],
                            'Snapshot Status': snapshot['Status'],
                            'Snapshot Type': snapshot['SnapshotType'],
                            'Is Snapshot Encrypted': snapshot['Encrypted']
                        })
                    print('\nDetected %d unencrypted RDS Instance Snapshots!\n\n' % len(unencrypted_snapshots))

                # Block to populate RDS Instance Snapshots - End
                # -----------------------------------------------------------------------------------------


                
                # -----------------------------------------------------------------------------------------
                # Block to populate RDS Cluster Snapshots - Begin

                print(f'Checking for RDS Cluster Snapshots in [{region}] region for [{aws_profile}] account\n')
                # Query to describe all RDS Cluster Instances Snapshots
                cluster_response = rds_client.describe_db_cluster_snapshots()

                if (len(cluster_response['DBClusterSnapshots']) == 0):
                    print(f'0 RDS Cluster Snapshots found in the region [{region}] for [{aws_profile}] account')
                    print(f'==============================================================================================================================================================\n\n')
                else:
                    # Reset arrays to zero for every region
                    unencrypted_cluster_snapshots = []

                    print(f"{len(cluster_response['DBClusterSnapshots'])} RDS Cluster Snapshot(s) found in the region [{region}] for [{aws_profile}] account\n")
                    for cluster_snapshot in cluster_response['DBClusterSnapshots']:
                        print('Cluster Snapshot: {0:120} DBClusterIdentifier: {1} \t\t\t\t\t\t SnapshotType: {2} \t\t\t\t\t\t Encrypted: {3}'.format(
                            cluster_snapshot['DBClusterSnapshotIdentifier'],
                            cluster_snapshot['DBClusterIdentifier'],
                            cluster_snapshot['SnapshotType'],
                            cluster_snapshot['StorageEncrypted'])
                        )

                        if cluster_snapshot['StorageEncrypted'] == False:
                            unencrypted_cluster_snapshots.append(cluster_snapshot)
                        
                        cluster_snapshots_list.append({
                            'AWS Region': region,
                            'DB Identifier': cluster_snapshot['DBClusterIdentifier'],
                            'Snapshot Identifier': cluster_snapshot['DBClusterSnapshotIdentifier'],
                            'Snapshot Creation Time': cluster_snapshot['SnapshotCreateTime'],
                            'Snapshot Status': cluster_snapshot['Status'],
                            'Snapshot Type': cluster_snapshot['SnapshotType'],
                            'Is Snapshot Encrypted': cluster_snapshot['StorageEncrypted']
                        })
                    
                    print('\nDetected %d unencrypted RDS Cluster Snapshots!' % len(unencrypted_cluster_snapshots))
                    print(f'==============================================================================================================================================================\n\n')

                # Block to populate RDS Cluster Snapshots - End
                # -----------------------------------------------------------------------------------------


            # -----------------------------------------------------------------------------------------
            # Block to write the output to csv file - Begin
            
            print(f'\nWriting the output of {aws_profile} account to CSV file..')
            csv_column_header = [
                'AWS Region',
                'DB Identifier',
                'Snapshot Identifier',
                'Snapshot Creation Time',
                'Snapshot Status',
                'Snapshot Type',
                'Is Snapshot Encrypted'
            ]
            try:
                with open(output_csv, 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=csv_column_header)
                    writer.writeheader()
                    writer.writerows(instance_snapshots_list)
                    writer.writerows(cluster_snapshots_list)
                print(f'Details written to csv file [{output_csv}]\n')
            except IOError as e:
                print(f"{Fore.RED}{Style.BRIGHT}\nERROR: {e.response}\n")
                print(e.response['Error']['Code'])
                exit(1)
            
            # Block to write the output to csv file - End
            # -----------------------------------------------------------------------------------------

    except ClientError as error:
        print(f"{Fore.RED}{Style.BRIGHT}\nERROR: {error.response}\n")
        print(error.response['Error']['Code'])
        exit(1)

if __name__ == '__main__':
    main()