from zeep import Client
import os
import re


try:
    rrSystemId = int(input("What system ID would you like to download?"))
except:
    print('You MUST enter a System ID from Radio Reference')
    rrSystemId = int(input("What system ID would you like to download?"))

rrUser = input("Radio Reference Username: ")

rrPass = input("Radio Reference Password: ")
rrSiteId = input("Site ID: ")

# parameters
op25OutputPath = os.getcwd() + "/"
# op25OutputPath = '/home/pi/Downloads/op25/op25/gr-op25_repeater/apps/'

# radio reference authentication
client = Client('http://api.radioreference.com/soap2/?wsdl&v=15&s=rpc')
auth_type = client.get_type('ns0:authInfo')
myAuthInfo = auth_type(username=rrUser, password=rrPass, appKey='28801163', version='15',
                       style='rpc')

# prompt user for system ID
sysName = client.service.getTrsDetails(rrSystemId, myAuthInfo).sName
sysresult = client.service.getTrsDetails(rrSystemId, myAuthInfo).sysid
sysid = sysresult[0].sysid
print(sysName + ' system selected.')

#Read Talkgroup Data for given System ID
Talkgroups_type = client.get_type('ns0:Talkgroups')
result = Talkgroups_type(client.service.getTrsTalkgroups(rrSystemId, 0, 0, 0, myAuthInfo))

#Build sysID_siteID_talkgroups.tsv
talkgroups = []
for row in result:
    if row.enc == 0:
        talkgroups.append([row.tgDec,row.tgAlpha])#description row.tgDescr
    else:
        pass

count = 0
for i in talkgroups:
    try:
        result = talkgroups[count]
        tgid = str(result[0])
        tgtag = str(result[1])
        with open(op25OutputPath + sysid + '_' + rrSiteId + '_talkgroups.tsv', 'a+') as op25OutputFile:
            op25OutputFile.write(tgid + '\t' + tgtag + '\r\n')  # tgid -tab- talkgroup tag
        count = count + 1
    except Exception as e:
        print(e)
        count = count + 1
        pass



# Sites represented as Trunk.tsv files for OP25 consumption
client_type = client.get_type('ns0:TrsSites')
result = client_type(client.service.getTrsSites(rrSystemId, myAuthInfo))


trunktsvHeader = '"Sysname"\t' + '"Control Channel List"\t' + '"Offset"\t' + '"NAC"\t' + '"Modulation"\t' + '"TGID Tags File"\t' + '"Whitelist"\t' + '"Blacklist"\t' + '"Center Frequency"\n'

count = 0
for i in result:
    try:
        #print(str(result[count].siteId) + ':' + str(rrSiteId) + ':' + str(count))
        if str(result[count].siteId) in str(rrSiteId):



            sitefreqs = result[count].siteFreqs

            controlcount = 0
            altList = []
            for i in sitefreqs:
                if sitefreqs[controlcount].use == "d":
                    dedicatedCC = str(sitefreqs[controlcount].freq)
                if sitefreqs[controlcount].use == "a":
                    altList.append(str(sitefreqs[controlcount].freq))
                    alternateCC = re.sub("(\[|\]|')", "", str(altList))
                else:
                    pass
                controlcount = controlcount + 1

            systemC = '"' + sysid + '"'
            cclist = '"' + dedicatedCC + ',' + alternateCC + '"'
            offset = '"0"'
            nac = '"0"'
            modulation = '"CQPSK"'
            tagfile = '"' + op25OutputPath + sysid + '_' + rrSiteId + '_talkgroups.tsv"'
            whitelist = '""'
            blacklist = '""'
            centerfreq = '""'

            rfss = str(result[count].rfss)
            site = str(result[count].siteNumber)


            with open(op25OutputPath + sysid + '_' + rrSiteId + '_trunk.tsv', 'a+') as op25OutputFile:
                op25OutputFile.write(
                    trunktsvHeader + systemC + '\t' + cclist + '\t' + offset + '\t' + nac + '\t' + modulation + '\t' + tagfile + '\t' + whitelist + '\t' + blacklist + '\t' + centerfreq)

        count = count + 1
    except Exception as e:
        print(e)
        count = count + 1
        pass
