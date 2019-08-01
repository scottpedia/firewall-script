import boto3
import sys
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

IPIFY_API_URL = 'https://api.ipify.org'
SECURITY_GROUP_ID = 'your-security-group-id'
SECURITY_GROUP_NAME = 'your-security-group-name'
SECURITY_GROUP_REGION = 'aws-region'

nsg = boto3.resource('ec2', region_name=SECURITY_GROUP_REGION).SecurityGroup(SECURITY_GROUP_ID)
public_ip_address = None
to_delete = False

def get_public_ipv4_address(): #get your public ip address using apis from ipify.org
    response = urlopen(IPIFY_API_URL).read().decode('utf8')
    return response + '/32'    

def get_list_of_ip_ranges(): #get existing ip CIDR ranges in the Security Group
    ip_permissions = nsg.ip_permissions
    # print(ip_permissions) #debuging purposes
    ip_ranges = []
    for rule in ip_permissions:
        for ip in rule['IpRanges']:
            ip_ranges.append(ip['CidrIp'])
    return ip_ranges

def modify_ip_permissions(**kwarg): #modify the Security Group in specific occasions
    #If deleting the existing ip is needed, the "ip_to_delete" is specified as an argument, vice versa.
    #if we need to delete the existing ip in the nsg. 
    if 'ip_to_delete' in kwarg: 
        try:
            print('Deleting existing ip rule({})...'.format(kwarg['ip_to_delete']))
            nsg.revoke_ingress(
                ToPort=3306,
                IpProtocol='tcp',
                CidrIp=kwarg['ip_to_delete'],
                FromPort=3306,
                GroupName=SECURITY_GROUP_NAME,
            )
            print('Done\n')
        except Exception as e:
            print('Errors occured during revoking ip permission')
            print(e)
            print(e.__traceback__)
            sys.exit(1)
    if 'your_ip' in kwarg:
        try: #Add your public ip address into the nsg with error handling
            print('Adding your ip({}) to the nsg...'.format(kwarg['your_ip']))
            nsg.authorize_ingress(
                ToPort=3306,
                IpProtocol='tcp',
                CidrIp=kwarg['your_ip'],
                FromPort=3306,
                GroupName=SECURITY_GROUP_NAME,
            )
            print('Done\n')
        except Exception as e:
            print('Errors occured during applying the new rule')
            print(e)
            print(e.__traceback__)
            sys.exit(1)
    
def to_run():
    print('Aquiring your public ip address...')
    public_ip_address = get_public_ipv4_address()
    print("The public Ip address detected : {}\n".format(public_ip_address))
    
    print("Aquiring Security Rules...")
    ip_ranges = get_list_of_ip_ranges()
    print("Rules Aquired.")

    if len(ip_ranges) == 0: #No existing custom rule found in the nsg
        print("No custom rules in nsg, no need to delete the existing one.")
        if not to_delete:
            modify_ip_permissions(your_ip=public_ip_address)
    elif len(ip_ranges) == 1: #The existing rule, the one previously defined, is found.
        if not to_delete:
            #output the sets of ip addresses for comparison
            print('\n')
            print('Your Address   : {}'.format(public_ip_address))
            print('The One in nsg : {}\n'.format(ip_ranges[0]))
            
            if ip_ranges[0] != public_ip_address:# if the two are different, vice versa.
                print("The custom rule found. Try to delete the existing rule before adding the new one.")
                modify_ip_permissions(your_ip=public_ip_address,ip_to_delete=ip_ranges[0])
            else:
                print('Your public ip address matches the one existing in you nsg, abort.')
        else:
            print("\nDeleting existing rule({})...".format(ip_ranges[0]))
            modify_ip_permissions(ip_to_delete=ip_ranges[0])
            print("Done.")
    else:# multiple rules found, which is impossible.
        print("Multiple({}) rules found.".format(len(ip_ranges)))
        print(ip_ranges)
        promotion = "Do you want to delete all of them? \nyes/no> "#aquire user decisions on how to solve the problem
        user_s_choice = input(promotion).lower()
        count = 0
        while True:#repeate the input process if user types the wrong answer
            if user_s_choice == 'yes' or to_delete:#user wants to delete all custom ip ranges in the nsg
                for ip_range in ip_ranges:
                    print('Deleting IP : {}'.format(user_s_choice))
                    modify_ip_permissions(ip_to_delete=ip_range)
                    print('Done.')
                sys.exit(0)
            elif user_s_choice == 'no':#if user does not want to delete them
                print("Program completed.")
                sys.exit(0)            
            else:# user types the wrong answer for the 3nd time
                count += 1
                print("Invalid answer detected, please enter again.")
                user_s_choice = input(promotion).lower()
                if count == 3:
                    print("Invalid answer detected for the 3nd time, quit.")
                    sys.exit(1)
    print('program completed.')

if __name__ == "__main__":
    if sys.argv[1] == 'delete': # Program detects that the user simply wants to delete the custom rule
        to_delete = True    
    to_run()
    #place all the tasks in a seperate function outside the main(), which is good for debugging.
    
