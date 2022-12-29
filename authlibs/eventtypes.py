import inspect,sys
#vim:tabstop=2:expandtab

class RATTBE_LOGEVENT_UNKNOWN:
    id= 0
    desc= 'Unknown Event'

class RATTBE_LOGEVENT_COMMENT:
    id=1
    desc="Comment"


class RATTBE_LOGEVENT_CONFIG_OTHER:
    id=1000
    desc='Other Event'

class RATTBE_LOGEVENT_CONFIG_NEW_MEMBER_MANUAL:
    id=1001
    desc='Created New Member Manual'

class RATTBE_LOGEVENT_CONFIG_NEW_MEMBER_PAYSYS:
    id=1002
    desc='Created New Member from Pay System'

class RATTBE_LOGEVENT_CONFIG_PAY_MEMBER_IMPORT_ERR:
    id=1003
    desc='Payment Import Error'

class RATTBE_LOGEVENT_CONFIG_PAY_MEMBER_REASSIGN:
    id=1005
    desc='Payment Reassignment'

class RATTBE_LOGEVENT_MEMBER_TAG_ASSIGN:
    id=1006
    desc='Tag Assigned to Member'

class RATTBE_LOGEVENT_MEMBER_TAG_UNASSIGN:
    id=1007
    desc='Tag Unassigned to Member'

class RATTBE_LOGEVENT_MEMBER_ACCESS_ENABLED:
    id=1008
    desc='Member Access Enabled'

class RATTBE_LOGEVENT_MEMBER_ACCESS_DISABLED:
    id=1009
    desc='Member Access Disabled'

class RATTBE_LOGEVENT_MEMBER_WAIVER_ACCEPTED:
    id=1010
    desc='Waiver Accepted'

class RATTBE_LOGEVENT_MEMBER_PRIVILEGE_GRANTED:
    id=1011
    desc='Member Privilege Granted'

class RATTBE_LOGEVENT_MEMBER_PRIVILEGE_REVOKED:
    id=1012
    desc='Member Privilege Revoked'

class RATTBE_LOGEVENT_MEMBER_RESOURCE_LOCKOUT:
    id=1013
    desc='Member temporarily suspended from resource'

class RATTBE_LOGEVENT_MEMBER_RESOURCE_UNLOCKED:
    id=1014
    desc='Member Resource suspension removed'

class RATTBE_LOGEVENT_MEMBER_RECORD_DELETED:
    id=1015
    desc='Member record deleted'

class RATTBE_LOGEVENT_MEMBER_WAIVER_LINKED:
    id=1016
    desc='Member waiver linked'

class RATTBE_LOGEVENT_MEMBER_WAIVER_UNLINKED:
    id=1017
    desc='Member waiver unlinked'

class RATTBE_LOGEVENT_MEMBER_PAYMENT_LINKED:
    id=1018
    desc='Member payment manually linked'

class RATTBE_LOGEVENT_MEMBER_PAYMENT_UNLINKED:
    id=1019
    desc='Member payment manually unlinked'

class RATTBE_LOGEVENT_MEMBER_NOTICE_SENT:
    id=1020
    desc='Notice Sent'

class RATTBE_LOGEVENT_MEMBER_KIOSK_ACCEPTED:
    id=1021
    desc='Entry Kiosk Accepted'

class RATTBE_LOGEVENT_MEMBER_KIOSK_DENIED:
    id=1022
    desc='Entry Kiosk Denied'

class RATTBE_LOGEVENT_MEMBER_KIOSK_FAILED:
    id=1024
    desc='Entry Kiosk Failed'

class RATTBE_LOGEVENT_MEMBER_ENTRY_ALLOWED:
    id=1025
    desc='Allowed Entry'
    slack_icon=':white_check_mark:'
    slack_color='#00aa00'

class RATTBE_LOGEVENT_MEMBER_ENTRY_DENIED:
    id=1026
    desc='Denied Entry'
    slack_icon=':no_entry:'
    slack_color='#aa0000'

class RATTBE_LOGEVENT_DOOR_OPENED:
    id=1027
    desc='Door Opened'
    slack_icon=':arrow_forward:'
    slack_color='#777777'

class RATTBE_LOGEVENT_DOOR_CLOSED:
    id=1028
    desc='Door Closed'
    slack_icon=':arrow_backward:'
    slack_color='#777777'

class RATTBE_LOGEVENT_MEMBER_LEASE_CHARGE:
    id=1027
    desc='Charge for Leased Space'

class RATTBE_LOGEVENT_SYSTEM_OTHER:
    id=2000
    desc='Other System Event'

class RATTBE_LOGEVENT_SYSTEM_WIFI:
    id=2001
    desc='Wifi Status'

class RATTBE_LOGEVENT_SYSTEM_POWER_LOST:
    id=2002
    desc='Power Loss'
    slack_icon=':zzz:'

class RATTBE_LOGEVENT_SYSTEM_POWER_RESTORED:
    id=2003
    desc='Power Restored'
    slack_icon=':bulb:'

class RATTBE_LOGEVENT_SYSTEM_POWER_SHUTDOWN:
    id=2004
    desc='Shutdown'
    slack_icon=':zzz:'

class RATTBE_LOGEVENT_SYSTEM_POWER_OTHER:
    id=2005
    desc='Other Power Event'
    slack_icon=':lightning:'

class RATTBE_LOGEVENT_SYSTEM_BOOT:
    id=2006
    desc='System Boot'
    slack_icon=':up:'

class RATTBE_LOGEVENT_SYSTEM_OTA:
    id=2007
    desc="OTA Firmware Update"
    slack_icon=':floppy_disk:'
    
class RATTBE_LOGEVENT_TOOL_OTHER:
    id=3000
    desc='Other Tool Event'

class RATTBE_LOGEVENT_TOOL_ISSUE:
    id=3001
    desc='Other Tool Issue'
    slack_icon=":exclamation:"

class RATTBE_LOGEVENT_TOOL_SAFETY:
    id=3002
    desc='Tool Safety'
    slack_icon=":alert:"

class RATTBE_LOGEVENT_TOOL_ACTIVE:
    id=3003
    desc='Tool Active'
    slack_icon=":arrow_forward:"

class RATTBE_LOGEVENT_TOOL_INACTIVE:
    id=3004
    desc='Tool Inactive'
    slack_icon=":double_vertical_bar:"

class RATTBE_LOGEVENT_TOOL_LOCKOUT_PENDING:
    id=3005
    desc='Tool Lockout Pending'

class RATTBE_LOGEVENT_TOOL_LOCKOUT_LOCKED:
    id=3006
    desc='Tool Locked-out'
    slack_icon=":lock:"

class RATTBE_LOGEVENT_TOOL_LOCKOUT_UNLOCKED:
    id=3007
    desc='Tool Unlocked'
    slack_icon=":unlock:"

class RATTBE_LOGEVENT_TOOL_LOCKOUT_OTHER:
    id=3008
    desc='Lockout other'


class RATTBE_LOGEVENT_TOOL_POWERON:
    id=3009
    desc="Tool Powered On"
    slack_icon=":bulb:"

class RATTBE_LOGEVENT_TOOL_POWEROFF:
    id=3010
    desc="Tool Powered Off"
    slack_icon=":zzz:"

class RATTBE_LOGEVENT_TOOL_LOGIN_COMBO:
    id=3011
    desc="Login (via. combo/passcode)"
    slack_icon=":arrow_right:"
    slack_color="#00aa00"

class RATTBE_LOGEVENT_TOOL_PROHIBITED:
    id=3012
    desc="Denied Access"
    slack_icon=":no_entry:"
    slack_color="#aa0000"

class RATTBE_LOGEVENT_TOOL_LOGIN:
    id=3013
    desc="Allowed Access"
    slack_icon=":arrow_right:"
    slack_color="#00aa00"

class RATTBE_LOGEVENT_TOOL_COMBO_FAILED:
    id=3014
    desc="Incorrect Passcode attempt"
    slack_icon=":no_entry:"
    slack_color="#aa0000"

class RATTBE_LOGEVENT_TOOL_LOGOUT:
    id=3015
    desc="Done"
    slack_icon=":arrow_left:"

class RATTBE_LOGEVENT_TOOL_MAINTENANCE_DONE:
    id=3016
    desc="Maintenance Done"
    slack_icon=":wrench:"

class RATTBE_LOGEVENT_TOOL_ACL_UPDATED:
    id=3017
    desc="ACL Updated"

class RATTBE_LOGEVENT_TOOL_UNRECOGNIZED_FOB:
    id=3018
    desc="Unknown RFID"
    slack_icon=":no_entry_sign:"

class RATTBE_LOGEVENT_VENDING_SUCCESS:
    id=3019
    desc="Vending Purchase"
    slack_icon=":cookie:"

class RATTBE_LOGEVENT_VENDING_FAILED:
    id=3020
    desc="Vending Failure"
    slack_icon=":bangbang:"

class RATTBE_LOGEVENT_VENDING_ADDBALANCE:
    id=3021
    desc="Add Balance"
    slack_icon=":moneybag:"
    
class RATTBE_LOGEVENT_RESOURCE_ACCESS_GRANTED:
    id=4000
    desc='Resource access granted'
    slack_icon=":thumbs_up:"

class RATTBE_LOGEVENT_RESOURCE_ACCESS_REVOKED:
    id=4001
    desc='Resource access revoked'
    slack_icon=":thumbs_down:"

class RATTBE_LOGEVENT_RESOURCE_ACCESS_XXX:
    id=4002
    desc='Resource access ???'

class RATTBE_LOGEVENT_RESOURCE_PRIV_CHANGE:
    id=4004
    desc='Resource privilege change'
    slack_icon=":level_slider:"

class RATTBE_LOGEVENT_RESOURCE_TEMP_ACCESS_GRANTED:
    id=4005
    desc='Resource temporary access granted'
    slack_icon=":thumbs_up:"

class RATTBE_LOGEVENT_RESOURCE_TEMP_ACCESS_REVOKED:
    id=4006
    desc='Resource temporary access revoked'
    slack_icon=":thumbs_down:"

class RATTBE_LOGEVENT_PROSTORE_OTHER:
    id=5000
    desc='Pro-Storage Bin Misc Event'

class RATTBE_LOGEVENT_PROSTORE_ASSIGNED:
    id=5001
    desc='Pro-Storage Bin Assigned'

class RATTBE_LOGEVENT_PROSTORE_UNASSIGNED:
    id=5002
    desc='Pro-Storage Bin Unassigned'

class RATTBE_LOGEVENT_PROSTORE_CHANGED:
    id=5003
    desc='Pro-Storage Bin Changed'

class RATTBE_LOGEVENT_PROSTORE_NOTICE_SENT:
    id=5004
    desc='Pro-Storage Notice Sent'

class RATTBE_LOGEVENT_PROSTORE_MAX:
    id=5099
    desc='Pro-Storage Max'

def get_event_slack_icons():
    icons={}
    for (name,cl) in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if hasattr(cl,"slack_icon"):
            icons[cl.id]=cl.slack_icon

    return icons

def get_event_slack_colors():
    colors={}
    for (name,cl) in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if hasattr(cl,"slack_color"):
            colors[cl.id]=cl.slack_color

    return colors
				


def get_events():
    events_by_id={}
    for (name,cl) in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        events_by_id[cl.id]=cl.desc
    return events_by_id

if __name__=="__main__":
    print (get_events())
    print (get_event_slack_icons())
