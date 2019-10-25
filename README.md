# aws_route53_s3_backup
Backup your route53 records to s3 using the Boto3 library

This is a nobrainer backup for projects that you don't have in Terraform, or if you have a LOT of small records that don't really sit well in your Terraform but you don't want to clean it up. 

Anyway, I'm not judging anyone, just throw those records in a bucket. :) If someone changes them then panics, we've got your back!

You can run it daily on ec2.

it would require using the /tmp folder but you could make it a daily aws lambda function too. 
