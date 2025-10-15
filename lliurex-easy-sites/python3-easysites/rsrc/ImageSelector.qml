import org.kde.kirigami as Kirigami
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Popup {

    id:imagePopUp
    property alias customImagePathText:customImagePath.text
    property string selectedImageFile
    property bool imageFileError:false

    width:500
    height:250
    anchors.centerIn: Overlay.overlay
    modal:true
    focus:true
    closePolicy:Popup.NoAutoClose

    background:Rectangle{
        color:"#ebeced"
        border.color:"#b8b9ba"
        border.width:1
        radius:5.0
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
                                    if ((customImagePath.text=="")||(siteStackBridge.siteImage[2])){
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
                                if (!siteStackBridge.siteImage[2]){
                                    siteStackBridge.siteImage[1].substring(siteStackBridge.siteImage[1].lastIndexOf('/')+1)
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
                enabled:!siteStackBridge.siteImage[2]
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
                        tmpPath=siteStackBridge.siteImage[1]
                    }
                    siteStackBridge.updateImageValues([option,tmpPath])
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
        currentFolder:{
            if (selectedImageFile!=""){
                selectedImageFile.substring(0,selectedImageFile.lastIndexOf("/"))

            }else{
                StandardPaths.standardLocations(StandardPaths.PicturesLocation)[0]
            }

        }
        onAccepted:{
            selectedImageFile=""
            var tmpFile=imgDialog.selectedFile.toString()
            tmpFile=tmpFile.replace(/^(file:\/{2})/,"")
            customImagePath.text=tmpFile.substring(tmpFile.lastIndexOf('/')+1)
            selectedImageFile=tmpFile
            if (!siteStackBridge.checkMimeTypes(selectedImageFile)){
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

        imageFileError=false
        selectedImageFile=""
        messageLabel.visible=""
        applyBtn.enabled=!siteStackBridge.siteImage[2]
        
        if (siteStackBridge.siteImage[0]=="stock"){
            stockOption.checked=true
            customImagePath.text=""
        }else{
            customOption.checked=true
            if (!siteStackBridge.siteImage[2]){
                customImagePath.text=siteStackBridge.siteImage[1].substring(siteStackBridge.siteImage[1].lastIndexOf('/')+1)
            }else{
                customImagePath.text=""
            }
        }

    }
  
}
