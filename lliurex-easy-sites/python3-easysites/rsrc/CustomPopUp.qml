import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


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
                    source: "/usr/lib/python3.12/dist-packages/easysites/rsrc/loading.gif"
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
            case 13:
                var msg=i18nd("lliurex-easy-sites","Loading basic configuration. Wait a moment...");
                break;
            case 14:
                var msg=i18nd("lliurex-easy-sites","Loading site info. Wait a moment...");
                break;
            case 15:
                var msg=i18nd("lliurex-easy-sites","Validating the data entered. Wait a moment...")
                break;
            case 16:
                var msg=i18nd("lliurex-easy-sites","Saving the data entered. Wait a moment...")
                break;
            case 17:
                var msg=i18nd("lliurex-easy-sites","Hiding the site. Wait a moment...")
                break;
            case 18:
                var msg=i18nd("lliurex-easy-sites","Showing the site. Wait a moment...")
                break;
            case 19:
                var msg=i18nd("lliurex-easy-sites","Updating site content. Wait a moment...")
                break;
            case 20:
                var msg=i18nd("lliurex-easy-sites","Deleting the site. Wait a moment...")
                break;
            case 21:
                var msg=i18nd("lliurex-easy-sites","Mounting site content. Wait a moment...")
                break;
            case 22:
                var msg=i18nd("lliurex-easy-sites","Unmounting site content. Wait a moment...")
                break;
            case 23:
                var msg=i18nd("lliurex-easy-sites","Showing all sites. Wait a moment...")
                break
            case 24:
                var msg=i18nd("lliurex-easy-sites","Hidding all sites. Wait a moment...")
                break; 
            case 25:
                var msg=i18nd("lliurex-easy-sites","Deleting all sites. Wait a moment...")
                break;
       
              default:
                var msg=""
                break;
        }
        return msg
    }
}
