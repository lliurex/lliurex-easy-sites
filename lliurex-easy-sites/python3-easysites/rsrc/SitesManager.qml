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
                    onClicked:sitesOptionsStackBridge.changeSiteStatus([true,true])
                }

                MenuItem{
                    icon.name:"view-hidden.svg"
                    text:i18nd("lliurex-easy-sites","Hide all sites")
                    enabled:!sitesOptionsStackBridge.enableChangeStatusOptions[1]
                    onClicked:sitesOptionsStackBridge.changeSiteStatus([true,false])
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
        dialogTitle:"lliurex-easy-sites"+" - "+i18nd("lliurex-easy-sites","Site List")
        dialogMsg:{
            if (sitesOptionsStackBridge.showRemoveSiteDialog[1]){
                i18nd("lliurex-easy-sites","All sites will be deleted.\nDo yo want to continue?")
            }else{
                i18nd("lliurex-easy-sites","The site will be deleted.\nDo yo want to continue?")
            }
        }
        dialogVisible:sitesOptionsStackBridge.showRemoveSiteDialog[0]
        dialogWidth:300
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

   
    function getTextMessage(msgCode){
        switch (msgCode){
            case -9:
                var msg=i18nd("lliurex-easy-sites","Unable to sync the content")
                break;
            case -12:
                var msg=i18nd("lliurex-easy-sites","Unable to create the link template for the site")
                break
            case -19:
                var msg=i18nd("lliurex-easy-sites","Unable to create the icon for the site")
                break;
            case -20:
                var msg=i18nd("lliurex-easy-sites","Unable to create the symbolic link for the site")
                break;
            case -21:
                var msg=i18nd("lliurex-easy-sites","Unable to delete the site")
                break;
            case -22:
                var msg=i18nd("lliurex-easy-sites","Unabled to change the visibility of the site")
                break;
            case -37:
                var msg=i18nd("lliurex-easy-sites","Error reading configuration files of the sites")
                break;
            case 14:
                var msg=i18nd("lliurex-easy-sites","Site has been successfully deleted")
                break;
            case 15:
                var msg=i18nd("lliurex-easy-sites","Site has been successfully edited")
                break;
            case 16:
                var msg=i18nd("lliurex-easy-sites","Site is now visible again")
                break;
            case 17:
                var msg=i18nd("lliurex-easy-sites","Site has been hideen")
                break;
            case 18:
                var msg=i18nd("lliurex-easy-sites","Site has been successfully created")
                break
            case 46:
                var msg=i18nd("lliurex-easy-sites","The sites have been activated successfully")
                break;
            case 47:
                var msg=i18nd("lliurex-easy-sites","The sites have been hidden successfully")
                break;
            case 51:
                var msg=i18nd("lliurex-easy-sites","The sites have been removed successfully")
                break;
            case 53:
                var msg=i18nd("lliurex-easy-sites","Sites already visible. Nothing to do")
                break;
            case 54:
                var msg=i18nd("lliurex-easy-sites","Sites already hidden. Nothing to do")
                break;
            case 55:
                var msg=i18nd("lliurex-easy-sites","Sites already removed. Nothing to do")
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
