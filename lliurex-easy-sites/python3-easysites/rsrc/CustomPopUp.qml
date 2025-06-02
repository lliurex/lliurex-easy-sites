import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


Popup {
    id:popUpWaiting
    width:570
    height:80
    anchors.centerIn: Overlay.overlay
    modal:true
    focus:true
    visible:!mainStackBridge.closePopUp[0]
    closePolicy:Popup.NoAutoClose

    GridLayout{
        id: popupGrid
        rows: 2
        flow: GridLayout.TopToBottom
        anchors.centerIn:parent


        RowLayout {
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter
            Rectangle{
                color:"transparent"
                width:30
                height:30
                AnimatedImage{
                    source: "/usr/lib/python3/dist-packages/easysites/rsrc/loading.gif"
                    transform: Scale {xScale:0.45;yScale:0.45}
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            Text{
                id:popupText
                text:getTextMessage()
                font.pointSize: 10
                Layout.alignment:Qt.AlignHCenter
            }
        }
    }

    function getTextMessage(){
        switch (mainStackBridge.closePopUp[1]){
            case 1:
                var msg=i18nd("lliurex-easy-sites","Loading basic configuration. Wait a moment...");
                break;
            case 2:
                var msg=i18nd("lliurex-easy-sites","Loading site info. Wait a moment...");
                break;
            case 3:
                var msg=i18nd("lliurex-easy-sites","Validating the data entered. Wait a moment...")
                break;
            case 4:
                var msg=i18nd("lliurex-easy-sites","Saving the data entered. Wait a moment...")
                break;
            case 5:
                var msg=i18nd("lliurex-easy-sites","Activating the site. Wait a moment...")
                break;
            case 6:
                var msg=i18nd("lliurex-easy-sites","Activating all sites. Wait a moment...")
                break;
            case 7:
                var msg=i18nd("lliurex-easy-sites","Deactivating the site. Wait a moment...")
                break;
            case 8:
                var msg=i18nd("lliurex-easy-sites","Deactivating all sites. Wait a moment...")
                break;
            case 9:
                var msg=i18nd("lliurex-easy-sites","Removing the site. Wait a moment...")
                break;
            case 10:
                var msg=i18nd("lliurex-easy-sites","Removing all sites. Wait a moment...")
                break;
            default:
                var msg=""
                break;
        }
        return msg
    }
}
