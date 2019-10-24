import boto3
import time
import datetime
import json
import os

now = datetime.datetime.now()
today = now.strftime("%Y-%m-%d")
s3 = boto3.resource('s3')
route53 = boto3.client('route53')
bucketName = ""
route53FolderName = "route53"
fullFolderPath = route53FolderName + "/" + today
hostedZones = []
recordSets = {}
globalErrorList = []


def main():
    getHostedZones()
    getRecords()
    writeRecordsToFile()


def getHostedZones(nextMarker=""):
    try:
        print('Listing hosted zones .. ')

        if nextMarker is not "":
            response = route53.list_hosted_zones(Marker=nextMarker)
        else:
            response = route53.list_hosted_zones()
        print('Hosted zone count: ', len(response['HostedZones']))
    except Exception as x:
        globalErrorList.append(str(x))
        print(x)

    for zone in response['HostedZones']:
        hostedZones.append(zone)
    time.sleep(2)
    if bool(response['IsTruncated']):
        getHostedZones(str(response['NextMarker']))


def getRecords(startRecordName=""):
    print(hostedZones)
    for zone in hostedZones:
        try:
            print('Getting records for ' + str(zone['Name']))
            if startRecordName is not "":
                response = route53.list_resource_record_sets(
                    HostedZoneId=zone['Id'], StartRecordName=startRecordName)
            else:
                response = route53.list_resource_record_sets(
                    HostedZoneId=zone['Id'])
            print('response record set count: ', len(
                response['ResourceRecordSets']))
            time.sleep(2)

            recordSets[zone['Name']] = []
            for record in response['ResourceRecordSets']:
                recordSets[zone['Name']].append(record)

            if bool(response['IsTruncated']):
                getRecords(str(response['NextRecordName']))
        except Exception as x:
            globalErrorList.append(str(x))
            print(x)


def writeRecordsToFile():
    print('Writing records to file ..')
    cwd = './' + route53FolderName + '/' + today

    if not os.path.isdir('./' + route53FolderName):
        os.mkdir(route53FolderName)

    if not os.path.isdir(cwd):
        os.mkdir(cwd)

    for zone in hostedZones:
        fileName = cwd + '/' + today + '-' + zone['Name'] + 'json'
        if os.path.isfile(fileName):
            os.remove(fileName)

        with open(fileName, 'a') as outputFile:
            print(json.dumps(recordSets[zone['Name']]), file=outputFile)


def uploadRoute53DataFile(data):
    # Upload a new file
    data = open('test.jpg', 'rb')
    s3.Bucket(bucketName).put_object(Key='test.jpg', Body=data)


main()
