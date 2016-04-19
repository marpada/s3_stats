# s3_stats

Prints usage statistics of your S3 buckets on CSV format. Stats are
retrieved from Cloudwatch.

## Requirements

boto3

## Usage

```
usage: python s3_stats.py [-h] [-d DAYS] [-b BUCKETS]

Prints metrics about S3 buckets

optional arguments:
  -h, --help            show this help message and exit
  -d DAYS, --days DAYS
  -b BUCKETS, --buckets BUCKETS
                        Comma-separated list of selected buckets (will list all buckets if emtpy)

```

By default will print daily statistics for all your buckets for the
last 14 days (maximun metric period on Cloudwatch)

```
python s3_stats.py -d DAYS

```
Will print the stats for the last DAYS. Notice that for S3 Cloudwatch
aggregates the metrics daily, so it's possible that the *-d 1* option
does not return any data

```
python s3_stats.py -b bucket1,bucket2
```
Will show the metrics for bucket1 and bucket2.

## Output format

The output is a CSV with the following fields:

- Bucket
- Region
- Date (UTC)
- BucketSizeGBytes_StandardStorage : Gb on Standard Storage (SS)
- BucketSizeGBytes_ReducedRedundancyStorage : Gb on Reduced
  Reduncancy Storage (RRS)
- BucketSizeGBytes_ReducedRedundancyStorage : Gb on Infrequent Access
  Storage (IAS)
- NumberOfObjects_AllStorageTypes: Number of objects in the bucket

## License

[MIT](https://opensource.org/licenses/MIT)
