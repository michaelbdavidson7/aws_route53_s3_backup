import boto3
import time
import datetime
import json
import os

# Settings:
deployToS3Bucket = False
bucketName = "x"

# Init:
now = datetime.datetime.now()
today = now.strftime("%Y-%m-%d")
s3 = boto3.resource('s3')
route53 = boto3.client('route53')
route53FolderName = "route53"
fullFolderPath = route53FolderName + "/" + today
hostedZones = []
recordSets = {}
globalErrorList = []


def main():
    getHostedZones()
    getRecords()
    writeRecordsToFile()
    uploadRoute53DataFile()


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


def getRecords(startRecordName="", passedInZoneId="", passedInZoneName=""):
    print('Getting records for hosted zones .. ')
    for zone in hostedZones:
        try:
            if startRecordName is not "":
                print('Getting additional records for zoneid ', passedInZoneId)
                response = route53.list_resource_record_sets(
                    HostedZoneId=passedInZoneId, StartRecordName=startRecordName)
                print(response)

                for record in response['ResourceRecordSets']:
                    recordSets[passedInZoneName].append(record)
                print(len(recordSets[passedInZoneName]))
            else:
                print('Getting records for ' + str(zone['Name']))
                response = route53.list_resource_record_sets(
                    HostedZoneId=zone['Id'])
                
                if zone['Name'] not in recordSets:
                    recordSets[zone['Name']] = []
                for record in response['ResourceRecordSets']:
                    recordSets[zone['Name']].append(record)
            print('response record set count: ', len(response['ResourceRecordSets']))
            time.sleep(2)


            if response['IsTruncated'] == True:
                print('Truncated response.. going back for more .. ')
                getRecords(str(response['NextRecordName']), str(zone['Id']), str(zone['Name']))

            if startRecordName is not "":
                return
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
        fileName = cwd + '/' + zone['Name'] + 'json'
        if os.path.isfile(fileName):
            os.remove(fileName)

        with open(fileName, 'a') as outputFile:
            print(json.dumps(recordSets[zone['Name']]), file=outputFile)


def uploadRoute53DataFile():
    if deployToS3Bucket is False:
        return
    print('Writing files to s3 bucket ..')
    cwd = './' + route53FolderName + '/' + today

    for zone in hostedZones:
        fullFileName = cwd + '/' + zone['Name'] + 'json'
        # Upload a new file
        print('Writing ' + zone['Name'] + ' to bucket')
        data = open(fullFileName, 'rb')
        s3.Bucket(bucketName).put_object(Key=route53FolderName +
                                         '/'+today+'/'+zone['Name']+'json', Body=data)
        
        time.sleep(1)


main()