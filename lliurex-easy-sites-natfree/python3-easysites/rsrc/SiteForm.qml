import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3


Rectangle{
    color:"transparent"
    property string selectedFolder

    Text{ 
        text:{
            switch(siteStackBridge.actionType){
                case "add":
                    i18nd("lliurex-easy-sites","New Site")
                    break;
                case "edit":
                    i18nd("lliurex-easy-sites","Edit Site")
                    break;
             }
        }
        font.pointSize: 16
    }
    
    GridLayout{
        id:generalLayout
        rows:2
        flow: GridLayout.TopToBottom
        rowSpacing:10
        width:parent.width-20
        anchors.horizontalCenter:parent.horizontalCenter
  
        Kirigami.InlineMessage {
            id: messageLabel
            visible:siteStackBridge.showSiteFormMessage[0]
            text:getMessageText()
            type:Kirigami.MessageType.Error
            Layout.minimumWidth:580
            Layout.fillWidth:true
            Layout.topMargin: 40
        }

        GridLayout{
            id:optionsGrid
            columns:2
            flow: GridLayout.LeftToRight
            columnSpacing:10
            Layout.topMargin:40
            Layout.alignment:Qt.AlignHCenter

            Text{
                id:siteName
                text:i18nd("lliurex-easy-sites","Name:")
                Layout.alignment:Qt.AlignRight
            }
            RowLayout{
                Layout.alignment:Qt.AlignLeft
                spacing:10

                TextField{
                    id:siteNameEntry
                    text:siteStackBridge.siteName
                    horizontalAlignment:TextInput.AlignLeft
                    implicitWidth:330
                    onTextChanged:{
                        siteStackBridge.updateSiteNameValue(siteNameEntry.text)
                    }
                }
                Rectangle{
                    id:container
                    width:85
                    height:85
                    border.color: "#ffffff"
                    border.width:5
                    color:"transparent"
   
                    Image{
                        id:siteImg
                        width:65
                        height:65
                        fillMode:Image.PreserveAspectFit
                        source:siteStackBridge.siteImage[1]
                        ToolTip.delay: 1000
                        ToolTip.timeout: 3000
                        ToolTip.visible:mouseAreaImg.containsMouse?true:false 
                        ToolTip.text:i18nd("lliurex-easy-sites","Clic to edit the image")
                        clip:true
                        anchors.centerIn:parent
                        Keys.onSpacePressed: imageSelector.open()
                        MouseArea {
                            id: mouseAreaImg
                            anchors.fill: parent
                            hoverEnabled: true
                            onEntered: {
                                container.border.color="#add8e6"
                                focus=true
                            }
                            onExited: {
                                container.border.color="#ffffff"
                            }
                             onClicked:{
                                imageSelector.open()
                            }
                        }

                        ImageSelector{
                            id:imageSelector
                        }
                    }
                }

            }
            Text{
                id:siteDescription
                text:i18nd("lliurex-easy-sites","Description:")
                Layout.alignment:Qt.AlignRight
                Layout.topMargin:15
            }
            TextField{
                id:siteDescriptionEntry
                text:siteStackBridge.siteDescription
                horizontalAlignment:TextInput.AlignLeft
                implicitWidth:330
                Layout.topMargin:15
                onTextChanged:{
                    siteStackBridge.updateSiteDescriptionValue(siteDescriptionEntry.text)
                }
            }
            Text{
                id:folderLabel
                text:i18nd("lliurex-easy-sites","Get content from:")
                Layout.alignment:Qt.AlignRight
                Layout.topMargin:15
            }

            RowLayout{
                Layout.alignment:Qt.AlignLeft
                spacing:10
                Layout.topMargin:15
                Text{
                    id:siteFolder
                    text:{
                        if (siteStackBridge.siteFolder==""){
                            i18nd("lliurex-easy-sites","<specify the folder to get content>")
                        }else{
                            siteStackBridge.siteFolder
                        }
                    }
                    horizontalAlignment:TextInput.AlignLeft
                    Layout.fillWidth:{
                        if (siteFolder.width>optionsGrid.width){
                            true
                        }else{
                            false
                        }
                    }
                    width:200
                    elide:Text.ElideMiddle
                }

                Button {
                    id:editFolderBtn
                    display:AbstractButton.IconOnly
                    icon.name:"document-edit.svg"
                    Layout.preferredHeight: 35
                    ToolTip.delay: 1000
                    ToolTip.timeout: 3000
                    ToolTip.visible: hovered
                    ToolTip.text:i18nd("lliurex-easy-sites","Click to select folder")
                    onClicked:siteFolderDialog.open()
                }
            }

            Text{
                id:syncOption
                text:""
            }
            ButtonGroup{
                buttons:typeOptions.children
            }

            Column{
                id:typeOptions
                spacing:5
                Layout.alignment:Qt.AlignTop

                RadioButton{
                    id:copyOption
                    checked:!siteStackBridge.mountUnit
                    text:i18nd("lliurex-easy-sites","Copy selected content to site folder")
                    enabled:{
                        if (siteStackBridge.actionType=="edit"){
                            false
                        }else{
                            siteStackBridge.canMount
                        }
                    }
                    onToggled:{
                        if (checked){
                            siteStackBridge.updateMountValue(false)
                        }
                    }
                }

                RadioButton{
                    id:mountOption
                    checked:siteStackBridge.mountUnit
                    text:i18nd("lliurex-easy-sites","Mount selected content in site folder")
                    enabled:{
                        if (siteStackBridge.actionType=="edit"){
                            false
                        }else{
                            siteStackBridge.canMount
                        }
                    }
                    onToggled:{
                        if (checked){
                            siteStackBridge.updateMountValue(true)
                        }
                    }
                }
            }

            Text{
                id:autoMount
                text:i18nd("lliurex-easy-sites","Content mount:")
                Layout.alignment:Qt.AlignRight
                Layout.topMargin:15
                visible:mountOption.checked
                enabled:siteStackBridge.canMount
            }

            CheckBox {
                id:autoMountCb
                text:i18nd("lliurex-easy-sites","Automatic mounting at system startup")
                checked:{
                    if (siteStackBridge.autoMount=="enable"){
                        true
                    }else{
                        false
                    }
                }
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                visible:mountOption.checked
                enabled:siteStackBridge.canMount
                onToggled:{
                   siteStackBridge.manageAutoMount(checked)
                }

                Layout.alignment:Qt.AlignLeft
                Layout.topMargin:15
            }

            Text{
                id:siteState
                text:i18nd("lliurex-easy-sites","State:")
                Layout.alignment:Qt.AlignRight
                Layout.topMargin:15
            }
            CheckBox {
                id:siteVisibleCb
                text:i18nd("lliurex-easy-sites","Site visible in server main page")
                checked:siteStackBridge.isSiteVisible
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                onToggled:{
                   siteStackBridge.updateIsSiteVisibleValue(checked)
                }

                Layout.alignment:Qt.AlignLeft
                Layout.topMargin:15
            }
      }
       
    }
    RowLayout{
        id:btnBox
        anchors.bottom: parent.bottom
        anchors.right:parent.right
        anchors.bottomMargin:25
        anchors.rightMargin:10
        spacing:10

        Button {
            id:applyBtn
            visible:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok.svg"
            text:i18nd("lliurex-easy-sites","Apply")
            Layout.preferredHeight:40
            enabled:siteStackBridge.changesInSite
            onClicked:{
                closeTimer.stop()
                siteStackBridge.applySiteChanges()
                
            }
        }
        Button {
            id:cancelBtn
            visible:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel.svg"
            text:i18nd("lliurex-easy-sites","Cancel")
            Layout.preferredHeight: 40
            enabled:siteStackBridge.changesInSite
            onClicked:{
              siteStackBridge.cancelSiteChanges()
            }
            
        }
    }

     FileDialog{
        id:siteFolderDialog
        title: "Select a folder"
        folder:{
            if (selectedFolder!=""){
                shortcuts.selectedFolder
            }else{
                shortcuts.home
            }
        }
        selectFolder:true
        onAccepted:{
            selectedFolder=""
            selectedFolder=siteFolderDialog.fileUrl.toString()
            selectedFolder=selectedFolder.replace(/^(file:\/{2})/,"")
            siteStackBridge.updateSiteFolderValue(selectedFolder)
            siteFolder.text=selectedFolder
            messageLabel.visible=false
        }
      
    }

    ChangesDialog{
        id:settingsChangesDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"lliurex-easy-sites"+" - "+i18nd("lliurex-easy-sites","Site")
        dialogVisible:siteStackBridge.showChangesInSiteDialog
        dialogMsg:i18nd("lliurex-easy-sites","The are pending changes to save.\nDo you want save the changes or discard them?")
        dialogWidth:400
        btnAcceptVisible:true
        btnAcceptText:i18nd("lliurex-easy-sites","Apply")
        btnDiscardText:i18nd("lliurex-easy-sites","Discard")
        btnDiscardIcon:"delete.svg"
        btnDiscardVisible:true
        btnCancelText:i18nd("lliurex-easy-sites","Cancel")
        btnCancelIcon:"dialog-cancel.svg"
        Connections{
            target:settingsChangesDialog
            function onDialogApplyClicked(){
                siteStackBridge.manageChangesDialog("Accept")
            }
            function onDiscardDialogClicked(){
                siteStackBridge.manageChangesDialog("Discard")           
            }
            function onRejectDialogClicked(){
                closeTimer.stop()
                siteStackBridge.manageChangesDialog("Cancel")       
            }

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
        dialogMsg:i18nd("lliurex-easy-sites","The size of selected content is ")+siteStackBridge.freeSpaceChecked[1]+".\n"+i18nd("lliurex-easy-sites","If copied this content the available space on the system will be ")+siteStackBridge.freeSpaceChecked[3]+".\n"+i18nd("lliurex-easy-sites","Do you want to continue?.")
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
        dialogMsg:i18nd("lliurex-easy-sites","The size of selected content is ")+siteStackBridge.freeSpaceChecked[1]+".\n"+i18nd("lliurex-easy-sites","If cannot be copied because the available space on the system would only be ")+siteStackBridge.freeSpaceChecked[3]+"."
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

    function getMessageText(){

         switch (siteStackBridge.showSiteFormMessage[1]){
            case -19:
                var msg=i18nd("lliurex-easy-sites","You must indicate a name for the site");
                break;
            case -20:
                var msg=i18nd("lliurex-easy-sites","The name site is duplicate");
                break;
            case -21:
                var msg=i18nd("lliurex-easy-sites","Image file is not correct");
                break;
            case -22:
                var msg=i18nd("lliurex-easy-sites","You must indicate a image file");
                break;
            case -23:
                var msg=i18nd("lliurex-easy-sites","You must indicate a folder to sync content");
                break;
            case -25:
                var msg=i18nd("lliurex-easy-sites","The selected content exceeds the available space limit")
                break;
            default:
                var msg=""
                break
        }
        return msg    

    }
   
}
