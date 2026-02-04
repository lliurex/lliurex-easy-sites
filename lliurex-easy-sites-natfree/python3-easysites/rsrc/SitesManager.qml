import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3

Rectangle{
    id:rectLayout
    color:"transparent"
    Text{ 
        text:i18nd("lliurex-easy-sites","Configured sites")
        font.pointSize: 16
    }

    GridLayout{
        id:generalSitesLayout
        rows:2
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        width:parent.width-10
        height:parent.height-90
        enabled:true
        Kirigami.InlineMessage {
            id: messageLabel
            visible:sitesOptionsStackBridge.showMainMessage[0]
            text:getTextMessage(sitesOptionsStackBridge.showMainMessage[1])
            type:getTypeMessage(sitesOptionsStackBridge.showMainMessage[2])
            Layout.minimumWidth:650
            Layout.fillWidth:true
            Layout.topMargin: 40
        }
        
            
        SitesList{
            id:sitesList
            sitesModel:sitesOptionsStackBridge.sitesModel
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.topMargin: messageLabel.visible?0:40
        }
    }
    
    RowLayout{
        id:btnBox
        anchors.bottom: parent.bottom
        anchors.fill:parent.fill
        anchors.bottomMargin:15
        spacing:10
       
        Button {
            id:actionsBtn
            visible:true
            display:AbstractButton.TextBesideIcon
            icon.name:"run-build.svg"
            text:i18nd("lliurex-easy-sites","Global Options")
            Layout.preferredHeight:40
            Layout.rightMargin:rectLayout.width-(actionsBtn.width+newBtn.width+20)
            enabled:sitesOptionsStackBridge.enableGlobalOptions
            onClicked:actionsMenu.open()

            Menu{
                id:actionsMenu
                y: -actionsBtn.height*2.5
                x: actionsBtn.width/2

                MenuItem{
                    icon.name:"view-visible.svg"
                    text:i18nd("lliurex-easy-sites","Show all sites")
                    enabled:!sitesOptionsStackBridge.enableChangeStatusOptions[0]
                    onClicked:sitesOptionsStackBridge.changeAllSiteStatus(true)
                }

                MenuItem{
                    icon.name:"view-hidden.svg"
                    text:i18nd("lliurex-easy-sites","Hide all sites")
                    enabled:!sitesOptionsStackBridge.enableChangeStatusOptions[1]
                    onClicked:sitesOptionsStackBridge.changeAllSiteStatus(false)
                }

               MenuItem{
                    icon.name:"delete.svg"
                    text:i18nd("lliurex-easy-sites","Delete alls sites")
                    onClicked:sitesOptionsStackBridge.removeSite([true])
                }
            }
           
        }
        
        Button {
            id:newBtn
            visible:true
            display:AbstractButton.TextBesideIcon
            icon.name:"list-add.svg"
            text:i18nd("lliurex-easy-sites","New site")
            Layout.preferredHeight:40
            onClicked:siteStackBridge.addNewSite() 
        }
    }

    ChangesDialog{
        id:removeSiteDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"Easy-Sites"+" - "+i18nd("lliurex-easy-sites","Site List")
        dialogMsg:{
            if (sitesOptionsStackBridge.showRemoveSiteDialog[1]){
                i18nd("lliurex-easy-sites","All sites will be deleted.\nDo yo want to continue?")
            }else{
                i18nd("lliurex-easy-sites","The site will be deleted.\nDo yo want to continue?")
            }
        }
        dialogVisible:sitesOptionsStackBridge.showRemoveSiteDialog[0]
        dialogWidth:320
        btnAcceptVisible:false
        btnAcceptText:""
        btnDiscardText:i18nd("lliurex-easy-sites","Accept")
        btnDiscardIcon:"dialog-ok.svg"
        btnDiscardVisible:true
        btnCancelText:i18nd("lliurex-easy-sites","Cancel")
        btnCancelIcon:"dialog-cancel.svg"
        Connections{
           target:removeSiteDialog
           function onDiscardDialogClicked(){
                sitesOptionsStackBridge.manageRemoveSiteDialog('Accept')         
           }
           function onRejectDialogClicked(){
                sitesOptionsStackBridge.manageRemoveSiteDialog('Cancel')       
           }

        }
    }

     ChangesDialog{
        id:freeSpaceErrorWarning
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"lliurex-easy-sites"+" - "+i18nd("lliurex-easy-sites","Site")
        dialogVisible:siteStackBridge.showFreeSpaceWarning
        dialogMsg:i18nd("lliurex-easy-sites","The size of selected content is ")+siteStackBridge.freeSpaceChecked[1]+"\n"+i18nd("lliurex-easy-sites","If copied this content the available space on the system will be ")+siteStackBridge.freeSpaceChecked[3]+"\n"+i18nd("lliurex-easy-sites","Do you want to continue?")
        dialogWidth:500
        btnAcceptVisible:false
        btnDiscardVisible:true
        btnDiscardText:i18nd("lliurex-easy-sites","Yes")
        btnDiscardIcon:"dialog-ok.svg"
        btnCancelText:i18nd("lliurex-easy-sites","No")
        btnCancelIcon:"dialog-cancel.svg"
        Connections{
            target:freeSpaceErrorWarning
            function onDiscardDialogClicked(){
                siteStackBridge.manageFreeSpaceDialogWarning("Accept")           
            } 
            function onRejectDialogClicked(){
                siteStackBridge.manageFreeSpaceDialogWarning("Cancel")       
            }
        }
    }

    ChangesDialog{
        id:freeSpaceErrorDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"lliurex-easy-sites"+" - "+i18nd("lliurex-easy-sites","Site")
        dialogVisible:siteStackBridge.showFreeSpaceError
        dialogMsg:i18nd("lliurex-easy-sites","The size of selected content is ")+siteStackBridge.freeSpaceChecked[1]+"\n"+i18nd("lliurex-easy-sites","If cannot be copied because the available space on the system would only be ")+siteStackBridge.freeSpaceChecked[3]
        dialogWidth:500
        btnAcceptVisible:false
        btnDiscardVisible:false
        btnCancelText:i18nd("lliurex-easy-sites","Close")
        btnCancelIcon:"dialog-close.svg"
        Connections{
            target:freeSpaceErrorDialog
            function onRejectDialogClicked(){
                siteStackBridge.closeFreeSpaceDialogError()       
            }
        }
    }

   
    function getTextMessage(msgCode){
        switch (msgCode){
            case -1:
                var msg=i18nd("lliurex-easy-sites","Unable to delete the site")
                break;
            case -2:
                var msg=i18nd("lliurex-easy-sites","Unable to create folder to the site")
                break;
            case -3:
                var msg=i18nd("lliurex-easy-sites","Unable to rename the site. Old site not exists")
                break;
            case -4:
                var msg=i18nd("lliurex-easy-sites","Unable to rename the site due to problems in process")
                break;
            case -5:
                var msg=i18nd("lliurex-easy-sites","Unable to create the icon for the site")
                break;
            case -6:
                var msg=i18nd("lliurex-easy-sites","Unable to create the symbolic link for the site")
                break;                
            case -7:
                var msg=i18nd("lliurex-easy-sites","Error reading configuration files of the sites")
                break;
            case -8:
                var msg=i18nd("lliurex-easy-sites","Error writing changes in the site configuration file")
                break;
            case -9:
                var msg=i18nd("lliurex-easy-sites","Unable to edit the site")
                break;
            case -10:
                var msg=i18nd("lliurex-easy-sites","Error removing all sites")
                break;
            case -11:
                var msg=i18nd("lliurex-easy-sites","Error showing all sites")
                break;
            case -12:
                var msg=i18nd("lliurex-easy-sites","Error hiding all sites")
                break;
            case -13:
                var msg=i18nd("lliurex-easy-sites","Unable to mount content for the site")
                break;
            case -14:
                var msg=i18nd("lliurex-easy-sites","Unable to unmount content for the site")
                break;
            case -15:
                var msg=i18nd("lliurex-easy-sites","Unable to configure automatic content mount for the site")
                break;
            case -16:
                var msg=i18nd("lliurex-easy-sites","Unable to disable automatic content mount for the site")
                break;
            case -17:
                var msg=i18nd("lliurex-easy-sites","Unable to show site")
                break;
            case -18:
                var msg=i18nd("lliurex-easy-sites","Unable to hide site")
                break;
            case -24:
                var msg=i18nd("lliurex-easy-sites","Unable to generate icon for the site")
                break;
            case 1:
                var msg=i18nd("lliurex-easy-sites","Site has been successfully edited")
                break;
            case 2:
                var msg=i18nd("lliurex-easy-sites","Site has been successfully created")
                break;
            case 3:
                var msg=i18nd("lliurex-easy-sites","Site has been successfully deleted")
                break;
             case 4:
                var msg=i18nd("lliurex-easy-sites","All sites have been successfully removed")
                break;
            case 5:
                var msg=i18nd("lliurex-easy-sites","All sites are now visible again")
                break;
            case 6:
                var msg=i18nd("lliurex-easy-sites","All sites have been hidden successfully")
                break;
            case 7:
                var msg=i18nd("lliurex-easy-sites","Content copied successfully")
                break;
            case 8:
                var msg=i18nd("lliurex-easy-sites","Content mounted successfully")
                break;
            case 9:
                var msg=i18nd("lliurex-easy-sites","Content unmounted successfully")
                break;
            case 10:
                var msg=i18nd("lliurex-easy-sites","Automatic content mount enable successfully")
                break;
            case 11:
                var msg=i18nd("lliurex-easy-sites","Automatic content mount disable successfully")
                break;
            case 12:
                var msg=i18nd("lliurex-easy-sites","Site is now visible")
                break;
            case 13:
                var msg=i18nd("lliurex-easy-sites","Site is now hidden")
                break;
            default:
                var msg=""
                break;
        }
        return msg
    } 

    function getTypeMessage(msgType){

        switch (msgType){
            case "Information":
                return Kirigami.MessageType.Information
            case "Ok":
                return Kirigami.MessageType.Positive
            case "Error":
                return Kirigami.MessageType.Error
            case "Warning":
                return Kirigami.MessageType.Warning
        }
    }

} 
