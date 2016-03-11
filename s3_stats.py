import boto3
import datetime
import csv
import sys
import argparse

PERIOD = 60 * 60 * 24 # 1day

def get_region(location):
    if not location :
        return 'us-east-1'
    elif location == 'EU':
        return 'eu-west-1'
    else:
        return location

def get_bucket_metrics(buckets,days=14):
    s3_client = boto3.client('s3')
    METRICS = {'NumberOfObjects' : ['AllStorageTypes'],'BucketSizeBytes': ['StandardStorage','ReducedRedundancyStorage','StandardIAStorage']}
    results = {}
    now = datetime.datetime.utcnow()
    for bucket in buckets:
        location = s3_client.get_bucket_location(Bucket=bucket)['LocationConstraint']
        region = get_region(location)
        cw = boto3.client('cloudwatch',region_name = region)
        datapoints = {}
        for metric, storage_types in METRICS.items():
                for storage_type in storage_types:
                    response = cw.get_metric_statistics(
                            Namespace = 'AWS/S3',
                            MetricName = metric,
                            Statistics = ['Average'],
                            Period = PERIOD,
                            EndTime = now,
                            StartTime = now - datetime.timedelta(days=days),
                            Dimensions=[ { 'Name': 'BucketName', 'Value': bucket }, { 'Name': 'StorageType','Value': storage_type} ]
                            )
                    for stats in response['Datapoints']:
                        date = stats['Timestamp'].strftime("%Y-%m-%d")
                        if not date in datapoints:
                            datapoints[date] = {}
                        if metric not in datapoints[date]:
                            datapoints[date][metric] = dict.fromkeys(storage_types,0)
                        datapoints[date][metric][storage_type] = stats['Average']
        results[bucket] = datapoints
    return results

def Gb(bytes):
    return round(bytes / (1024 * 1024 * 1024),1)

def print_metrics(results,out_file=sys.stdout):
    rows = []
    headers = ['Bucket','Date']
    for bucket in sorted(results.keys()):
        for date in sorted(results[bucket].keys()):
            row = { 'Date' : date, 'Bucket' : bucket}
            for metric in results[bucket][date].keys():
                for storage_type in results[bucket][date][metric].keys():
                    key = metric + "_" + storage_type
                    key = key.replace('Bytes','GBytes')
                    if not key in headers:
                        headers.append(key)
                    val = results[bucket][date][metric].get(storage_type,0)
                    if not metric.startswith('Number'):
                        val = Gb(val)
                    row[key] = val
            rows.append(row)
    writer = csv.DictWriter(out_file,delimiter=',',fieldnames = headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

def list_buckets():
    s3_client = boto3.client('s3')
    return [ b['Name'] for b in s3_client.list_buckets()['Buckets']]

if __name__  == "__main__":
    days = 1
    parser = argparse.ArgumentParser(description="Prints metrics about S3 buckets")
    parser.add_argument('-d', '--days',action="store",default=14,type=int)
    parser.add_argument('-b','--buckets', default=[],action="store",help="Comma-separated list of selected buckets (will list all buckets if emtpy")

    args = parser.parse_args()
    if args.days not in range(2,15):
        print("days must be between 2 and 14")
        sys.exit(1)
    if args.buckets:
        metrics = get_bucket_metrics(args.buckets.split(','),args.days)
    else:
        metrics = get_bucket_metrics(list_buckets(),args.days)
    print_metrics(metrics)
