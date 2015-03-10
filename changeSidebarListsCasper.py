#!/usr/bin/python
import commands, os, sys, getopt, getpass, platform, plistlib, re, CoreFoundation, Cocoa, LaunchServices, time

#########################################################################################
# Change this to True if you are going to use this with a Casper Policy
# Parameter 4: Action (first, last, remove, after, move)
# Parameter 5: Path (If adding) Name (If moving or Removing)
# Parameter 6: Name (Of item to add after or move after)
#########################################################################################
CASPER_MODE = False

#########################################################################################
# Global Variables
#########################################################################################
_DEBUG = False

_ARG_LIST = []
_SIDEBAR_LIST_HR = []
_SIDEBAR_NAME_LIST = []
_SIDEBAR_ITEMS_SNAPSHOT = []
_SIDEBAR_ITEMS = ""

if CASPER_MODE:
    _ARG_LIST.append(sys.argv[0])
    for args in sys.argv[4:]:
        _ARG_LIST.append(args)
else:
    _ARG_LIST = sys.argv

if _DEBUG: print _ARG_LIST

#########################################################################################
# Help Menu
#########################################################################################
_THIS_SCRIPT = _ARG_LIST[0]

def SHOW_HELP_MENU():
    print "\nUsage: python %s [options]"% _THIS_SCRIPT
    print "-" * 20, "-" * 60
    print "%-20s %s"% ("help", "Print this message")
    print "%-20s %s"% ("list", "List Items in Sidebar")
    print "%-20s %s"% ("first [Path]", "Add Directory to First Position")
    print "%-20s %s"% ("last [Path]", "Add Directory to Last Position")
    print "%-20s %s"% ("remove [Name]", "Remove Exisiting Item from the Sidebar")
    print "%-20s %s"% ("after [Path] [Name]", "Add Directory to After Existing Item")
    print "%-20s %s"% ("move [Name] [Name]", "Move Existing Item After Existing Item")
    print "\n"
    exit()

#########################################################################################
# Check to make sure we have the right variables
#########################################################################################
if len(_ARG_LIST) < 2: SHOW_HELP_MENU()

_ACTION = _ARG_LIST[1]

if len(_ARG_LIST) == 2 and _ACTION.upper() != "LIST":
    print "Bad Arguments"
    SHOW_HELP_MENU()

if len(_ARG_LIST) == 3 and _ACTION.upper() not in ("FIRST","LAST","REMOVE"):
    print "Bad Arguments"
    SHOW_HELP_MENU()
elif len(_ARG_LIST) == 3 and _ACTION.upper() in ("FIRST","LAST","REMOVE"):
    _ITEM1 = _ARG_LIST[2]

if len(_ARG_LIST) == 4 and _ACTION.upper() not in ("AFTER","MOVE"):
    SHOW_HELP_MENU()
elif len(_ARG_LIST) == 4 and _ACTION.upper() in ("AFTER","MOVE"):
    _ITEM1 = _ARG_LIST[2]
    _ITEM2 = _ARG_LIST[3]

#########################################################################################
# Make Human Readable Sidebar List and update the snapshot
# This list will be a tuple of the Name and URLs of the Sidebar items
# Any time we are going through the sidebar list, we should run this to make
# sure it is current
#########################################################################################
def MAKE_SIDEBAR_LIST_HR():
    global _SIDEBAR_LIST_HR
    global _SIDEBAR_ITEMS_SNAPSHOT
    global _SIDEBAR_ITEMS
    global _SIDEBAR_NAME_LIST
    
    _SIDEBAR_LIST_HR = []
    _SIDEBAR_NAME_LIST = []
    _SIDEBAR_ITEMS= LaunchServices.LSSharedFileListCreate(CoreFoundation.kCFAllocatorDefault, LaunchServices.kLSSharedFileListFavoriteItems, None)
    _SIDEBAR_ITEMS_SNAPSHOT = LaunchServices.LSSharedFileListCopySnapshot(_SIDEBAR_ITEMS, None)
    
    for item in _SIDEBAR_ITEMS_SNAPSHOT[0]:
        item_Name = LaunchServices.LSSharedFileListItemCopyDisplayName(item)
        item_Path = ""
        if item_Name not in ("AirDrop", "All My Files", "iCloud"):
            item_Path = LaunchServices.LSSharedFileListItemResolve(item,0,None,None)[1]
        item_TUP = (item_Name, item_Path)
        _SIDEBAR_NAME_LIST.append(item_Name.upper())
        _SIDEBAR_LIST_HR.append(item_TUP)

#########################################################################################
# _ACTION List
# Take our Human Readable List and print it out, useful for Extension Attributes
#########################################################################################
def PRINT_SIDEBAR_LIST_HR():
    MAKE_SIDEBAR_LIST_HR()
    print "-" * 20, "-" * 60
    for item in _SIDEBAR_LIST_HR:
        print "%-20s %s"% (item[0], item[1])

if _ACTION.upper() == "LIST":
    PRINT_SIDEBAR_LIST_HR()
    exit()

#########################################################################################
# _ACTION Move Items
# Take two items by their name and put one after the other
# This apparently is the only LS Action that is supported in 10.9 and newer
#########################################################################################
def MOVE_ITEMS(this,that):
    MAKE_SIDEBAR_LIST_HR()
    item_To_Move = this.upper()
    item_After = that.upper()
    
    if item_To_Move not in _SIDEBAR_NAME_LIST:
        print "%s does not appear in the Sidebar"% item_To_Move
        exit()
    if item_After not in _SIDEBAR_NAME_LIST:
        print "%s does not appear in the Sidebar"% item_After
        exit()

    if _DEBUG: print "Moving %s after %s"% (item_To_Move,item_After)
    
    for item in _SIDEBAR_ITEMS_SNAPSHOT[0]:
        item_Name = LaunchServices.LSSharedFileListItemCopyDisplayName(item)
        item_Name = item_Name.upper()
        
        if item_Name == item_After: item_After = item
        if item_Name == item_To_Move: item_To_Move = item

    if _DEBUG: print "To Move: %s\nAfter:\t%s"% (item_To_Move,item_After)

    LaunchServices.LSSharedFileListItemMove(_SIDEBAR_ITEMS,item_To_Move,item_After)

#########################################################################################
# _ACTION Move Items
#########################################################################################
if _ACTION.upper() == "MOVE": MOVE_ITEMS(_ITEM1,_ITEM2)

#########################################################################################
# Get Nth Item Name
#########################################################################################
def GET_NTH_ITEM_NAME(N):
    global _SIDEBAR_LIST_HR
    MAKE_SIDEBAR_LIST_HR()
    if _DEBUG: print "The item is at location %s is %s"% (N,_SIDEBAR_LIST_HR[N][0])
    return _SIDEBAR_LIST_HR[N][0]


#########################################################################################
# ADDING ITEMS
#########################################################################################
NEW_ITEM = "file://localhost" + _ITEM1
if _DEBUG: print "NEW_ITEM: %s"% NEW_ITEM
#########################################################################################
# Create NSURL
#########################################################################################
ITEM_TO_ADD = Cocoa.NSURL.alloc().init()
ITEM_TO_ADD = Cocoa.NSURL.URLWithString_(NEW_ITEM)
if _DEBUG: print "ITEM_TO_ADD: %s"% ITEM_TO_ADD

#########################################################################################
# _ACTION Write to Sidebar
#########################################################################################
if _ACTION.upper() in ("FIRST","LAST","AFTER"):
    MAKE_SIDEBAR_LIST_HR()
    LaunchServices.LSSharedFileListInsertItemURL(_SIDEBAR_ITEMS,LaunchServices.kLSSharedFileListItemBeforeFirst,None,None,ITEM_TO_ADD,None,None)

    if _ACTION.upper() == "FIRST":
        MAKE_SIDEBAR_LIST_HR()
        last_item = GET_NTH_ITEM_NAME(-1)
        first_item = GET_NTH_ITEM_NAME(0)
        MOVE_ITEMS(last_item,first_item)
        #Stupid add Before first action does not work after 10.9 Do this mess instead
        first_item = GET_NTH_ITEM_NAME(0)
        second_item = GET_NTH_ITEM_NAME(1)
        MOVE_ITEMS(first_item,second_item)
        exit()

    if _ACTION.upper() == "AFTER":
        MAKE_SIDEBAR_LIST_HR()
        last_item = GET_NTH_ITEM_NAME(-1)
        after_item = _ITEM2
        MOVE_ITEMS(last_item,after_item)
        exit()


#########################################################################################
# _ACTION Remove
#########################################################################################
if _ACTION.upper() == "REMOVE":
    MAKE_SIDEBAR_LIST_HR()
    if _ITEM1.upper() not in _SIDEBAR_NAME_LIST:
        print "%s does not appear in the Sidebar"%  _ITEM1
    else:
        for item in _SIDEBAR_ITEMS_SNAPSHOT[0]:
            item_Name = LaunchServices.LSSharedFileListItemCopyDisplayName(item)
            if _ITEM1.upper() == item_Name.upper(): LaunchServices.LSSharedFileListItemRemove(_SIDEBAR_ITEMS, item)




