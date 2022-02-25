#this script is a prototype, and very specific. As always it should be executed on aproduction env only after thourough testing.
#This script functions as a way to pull inventory information from specifically tagged networks
#if no tag is provided it will pull the entire inventory.
##########################################################
# Prep your environment
#Environment with Python3 installed
#pip3 install meraki
##########################################################
#
# -k <your api key> [MANDATORY]
# -o <your org name> [MANDATORY] #not case sensitive
# -t <tag name> [OPTIONAL]
#
# usage python3 main.py -k <api key> -o <specific org name>  -t network_tag
######################################################################################################

import meraki
import sys, getopt, csv
from pathlib import Path


def createfile(inventory_data):
    keys = inventory_data[0].keys()
    filename = 'Maurices_Inventory' + '.csv'
    inpath = Path(filename)

    with inpath.open('w+', newline='')  as output_file:
            print(inpath)
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(inventory_data)
    return


def main(argv):
    global arg_apikey
    global arg_orgname

    arg_apikey = None
    arg_orgname = None
    arg_tagname = None

    try:
        opts, args = getopt.getopt(argv, 'k:o:t:')
    except getopt.GetoptError:
        sys.exit(0)

    for opt, arg in opts:
        if opt == '-k':
            arg_apikey = arg
        elif opt == '-o':
            arg_orgname = arg
        elif opt == '-t':
            arg_tagname = arg

    if arg_apikey is None or arg_orgname is None:
        print('Please specify the required values!')
        sys.exit(0)


    dashboard = meraki.DashboardAPI(arg_apikey, suppress_logging=True)

    org = dashboard.organizations.getOrganizations()
    for row in org:
        if row['name'].lower() == arg_orgname.lower():
            orgid = row['id']
            print("Org" + " " + row['name'] + " " + "found.")
        else:
            print(
                "Exception: This Org does not match:" + ' ' + row['name'] + ' ' + 'Is not the orginization specified!')

    # determine if a tag has been provided and only pull those networks
    if arg_tagname != None:
        networks = dashboard.organizations.getOrganizationNetworks(
        orgid, total_pages='all', tagsFilterType='withAllTags', tags=arg_tagname
            )
    else:
        networks = dashboard.organizations.getOrganizationNetworks(
         orgid, total_pages='all'
            )

    # process retrieved information and write it to a library
    inventory_data = []
    for network in networks:
        devices = dashboard.networks.getNetworkDevices(network['id']
        )

        for device in devices:
            #create a list of all Maurices networks, serials ....
            inventory_data_df = {'Network Name': network['name'], 'Network ID': device['networkId'], 'Device model': device['model'],
                                'Device MAC': device['mac'], 'Device Serial': device['serial']}

            print(inventory_data_df)
            print("added")
            inventory_data.append(inventory_data_df)


    output = createfile(inventory_data)

    print(output)


    print("I am Done, The results have been written to Maurices_Inventory.csv")


if __name__ == '__main__':
    main(sys.argv[1:])