import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3

Popup {

    id:imagePopUp
    property alias customImagePathText:customImagePath.text
    property string selectedImageFile
    property bool imageFileError:false

    width:500
    height:350
    anchors.centerIn: Overlay.overlay
    modal:true
    focus:true
    closePolicy:Popup.NoAutoClose

    background:Rectangle{
        color:"#ebeced"
    }

    contentItem:Rectangle{
        id:container
        width:imagePopUp.width
        height:imagePopUp.height
        color:"transparent"
        Text{ 
            text:i18nd("lliurex-easy-sites","Edit image for site")
            font.pointSize: 16
        }
        GridLayout{
            id:imageSelectorLayout
            rows:2
            flow: GridLayout.TopToBottom
            rowSpacing:10
            anchors.left:parent.left
            enabled:true
            Kirigami.InlineMessage {
                id: messageLabel
                visible:false
                text:i18nd("lliurex-easy-sites","Image file is not correct")
                type: Kirigami.MessageType.Error
                Layout.minimumWidth:480
                Layout.fillWidth:true
                Layout.topMargin: 40
            }

            GridLayout{
                id: imageOptions
                rows: 2
                flow: GridLayout.TopToBottom
                rowSpacing:10
                Layout.topMargin: messageLabel.visible?0:50
                ButtonGroup{
                    id:imageOptionsGroup
                }
                RowLayout{
                    id:stockRow
                    spacing:10
                    Layout.alignment:Qt.AlignLeft
                    Layout.bottomMargin:10
                    RadioButton{
                        id:stockOption
                        checked:{
                            if (siteStackBridge.siteImage[0]=="stock"){
                                true
                            }else{
                                false
                            }
                        }
                        text:i18nd("lliurex-easy-sites","From stock")
                        onToggled:{
                            if (checked){
                                messageLabel.visible=false
                                applyBtn.enabled=true
                            }
                        }
                        ButtonGroup.group:imageOptionsGroup
                        
                    }
                }

                RowLayout{
                    id:customRow
                    spacing:10
                    Layout.alignment:Qt.AlignLeft|Qt.AlignVCenter
                    Layout.bottomMargin:10
                    RadioButton{
                        id:customOption
                        checked:{
                            if (siteStackBridge.siteImage[0]=="custom"){
                                true
                            }else{
                                false
                            }
                        }
                        text:i18nd("lliurex-easy-sites","Custom image")
                        onToggled:{
                            if (checked){
                                if (imageFileError){
                                    messageLabel.visible=true
                                    applyBtn.enabled=false
                                }else{
                                    if ((customImagePath.text=="")||(siteStackBridge.siteImage[3])){
                                        applyBtn.enabled=false
                                    }else{
                                        applyBtn.enabled=true
                                    }
                                }
                            }
                        }
                        ButtonGroup.group:imageOptionsGroup
                    }
                    TextField{
                        id:customImagePath
                        text:{
                            if (siteStackBridge.siteImage[0]=="custom"){
                                if (!siteStackBridge.siteImage[3]){
                                    siteStackBridge.siteImage[1].substring(siteStackBridge.siteImage[2].lastIndexOf('/')+1)
                                }else{
                                    ""
                                }
                            }else{
                                ""
                            }
                        }
                        Layout.preferredWidth:250
                        maximumLength:500
                        readOnly:true
                        enabled:customOption.checked?true:false
                    }

                    Button{
                        id:fileSelectorBtn
                        display:AbstractButton.IconOnly
                        icon.name:"insert-image.svg"
                        enabled:customOption.checked?true:false
                        height: 35
                        ToolTip.delay: 1000
                        ToolTip.timeout: 3000
                        ToolTip.visible: hovered
                        ToolTip.text:i18nd("lliurex-easy-sites","Click to select an image")
                        onClicked:imgDialog.open()
                    }
                }
            }
        }
        RowLayout{
            id:btnBox
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.topMargin:10
            spacing:10

            Button {
                id:applyBtn
                visible:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok.svg"
                text:i18nd("lliurex-easy-sites","Apply")
                Layout.preferredHeight:40
                enabled:!siteStackBridge.siteImage[3]
                onClicked:{
                    var option=""
                    var tmpPath=""
                    if (stockOption.checked){
                        option="stock"
                    }else{
                        option="custom"
                    }
                    if (selectedImageFile!=""){
                        tmpPath=selectedImageFile
                    }else{
                        tmpPath=siteStackBridge.siteImage[2]
                    }
                    siteStackBridge.updateImageValues([option,imageList.currentImgIndex,tmpPath])
                    restoreInitValues()
                    imageSelector.close()
                }
            }
            
            Button {
                id:cancelBtn
                visible:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-cancel.svg"
                text:i18nd("lliurex-easy-sites","Cancel")
                Layout.preferredHeight: 40
                enabled:true
                onClicked:{
                    restoreInitValues()
                    imageSelector.close()
                }
            }

        }
    }


    FileDialog{
        id:imgDialog
        title: "Select and image file"
        folder:{
            if (selectedImageFile!=""){
                shortcuts.selectedImageFile.substring(0,selectedImageFile.lastIndexOf("/"))
            }else{
                shortcuts.home
            }

        }
        onAccepted:{
            selectedImageFile=""
            var tmpFile=imgDialog.fileUrl.toString()
            tmpFile=tmpFile.replace(/^(file:\/{2})/,"")
            customImagePath.text=tmpFile.substring(tmpFile.lastIndexOf('/')+1)
            selectedImageFile=tmpFile
            if (!siteStackBridge.checkMimetypeImage(selectedImageFile)){
                messageLabel.visible=true
                applyBtn.enabled=false
                imageFileError=true
            }else{
                messageLabel.visible=false
                applyBtn.enabled=true
                imageFileError=false
            }
        }
      
    }

    function restoreInitValues(){

        imageList.currentImgIndex=siteStackBridge.siteImage[1]
        imageFileError=false
        selectedImageFile=""
        messageLabel.visible=""
        applyBtn.enabled=!siteStackBridge.siteImage[3]
        
        if (siteStackBridge.siteImage[0]=="stock"){
            stockOption.checked=true
            customImagePath.text=""
        }else{
            customOption.checked=true
            if (!siteStackBridge.siteImage[3]){
                customImagePath.text=siteStackBridge.siteImage[2].substring(siteStackBridge.siteImage[2].lastIndexOf('/')+1)
            }else{
                customImagePath.text=""
            }
        }

    }
  
}
