import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


GridLayout{
    id: mainGrid
    columns: 2
    flow: GridLayout.LeftToRight
    columnSpacing:10

    Rectangle{
        width:120
        Layout.fillHeight:true
        border.color: "#d3d3d3"

        GridLayout{
            id: menuGrid
            rows:3 
            flow: GridLayout.TopToBottom
            rowSpacing:0

            MenuOptionBtn {
                id:listItem
                optionText:i18nd("lliurex-easy-sites","Sites")
                optionIcon:"/usr/share/icons/breeze/places/22/folder-html.svg"
               
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.moveToMainOptions(0)
                    }
                }
                
            }
            MenuOptionBtn {
                id:helpItem
                optionText:i18nd("lliurex-easy-sites","Help")
                optionIcon:"/usr/share/icons/breeze/actions/22/help-contents.svg"
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.openHelp();
                    }
                }
            }
        }
    }

    StackView {
        id: optionsView
        property int currentIndex:mainStackBridge.mainCurrentOption
        Layout.fillWidth:true
        Layout.fillHeight:true
        initialItem:sitesView

        onCurrentIndexChanged:{
            switch(currentIndex){
                case 0:
                    optionsView.replace(sitesView)
                    break;
             }
        }
        replaceEnter: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 0
                to:1
                duration: 60
            }
        }
        replaceExit: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 1
                to:0
                duration: 60
            }
        }
        Component{
            id:sitesView
            SitesManager{
                id:sitesManager
            }
        }

   }
}

