import boto3
import time

s3 = boto3.resource('s3')
route53 = boto3.client('route53')
bucketName = ""
hostedZones = []
globalErrorList = []

def main():
    getHostedZones()
    print('hostedZones', hostedZones)
    getRecords()



def getHostedZones(nextMarker=""):
    try:
        print('Listing hosted zones .. ')

        if nextMarker is not "":    
            response = route53.list_hosted_zones(Marker=nextMarker)
        else:
            response = route53.list_hosted_zones()
        print(response)
    except Exception as x:
        globalErrorList.append(str(x))
        print(x)

    for zone in response['HostedZones']:
        hostedZones.append(zone)
    time.sleep(2)
    if bool(response['IsTruncated']):
        getHostedZones(str(response['NextMarker']))

def getRecords():
    print(hostedZones)
    for zone in hostedZones:
        try:
            print('Getting records for '+ str(zone['Name']))
            response = route53.list_resource_record_sets(
                HostedZoneId=zone['Id']
                # StartRecordName='string',
                # StartRecordType='SOA'|'A'|'TXT'|'NS'|'CNAME'|'MX'|'NAPTR'|'PTR'|'SRV'|'SPF'|'AAAA'|'CAA',
                # StartRecordIdentifier='string',
                # MaxItems='string'
            )
            print('response', response)
        except Exception as x:   
            globalErrorList.append(str(x))
            print(x)

def uploadRoute53DataFile(data):
    # Upload a new file
    data = open('test.jpg', 'rb')
    s3.Bucket(bucketName).put_object(Key='test.jpg', Body=data)

main()