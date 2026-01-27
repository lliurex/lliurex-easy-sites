import org.kde.plasma.components 2.0 as Components
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
import QtQuick.Dialogs 1.3

Components.ListItem{

    id: listSiteItem
    property string siteId
    property string siteImg
    property string siteName
    property string createdBy
    property string updatedBy
    property bool isVisible
    property string siteUrl
    property string siteFolder
    property string selectedFolder
    property bool mountUnit

    enabled:true

    onContainsMouseChanged: {

        if (!optionsMenu.activeFocus){
            if (containsMouse) {
                listSites.currentIndex=filterModel.visibleElements.indexOf(index)
            }else {
                listSites.currentIndex = -1
            }
        }

    }

    Rectangle {
        height:visible?85:0
        width:parent.width
        color:"transparent"
        border.color: "transparent"
        Item{
            id: menuItem
            height:visible?85:0
            width:listSiteItem.width-manageSiteBtn.width
            
            Image{
                id:siteImage
                width:60
                height:60
                fillMode:Image.PreserveAspectFit
                source:siteImg
                anchors.verticalCenter:parent.verticalCenter
                anchors.left:parent.left
                anchors.leftMargin:15
            }
            Column{
                id:siteDescription
                anchors.verticalCenter:parent.verticalCenter
                anchors.left:siteImage.right
                anchors.leftMargin:30
                spacing:10
                width:{
                    if (listSiteItem.ListView.isCurrentItem){
                        parent.width-(siteState.width+manageSiteBtn.width+150)
                    }else{
                        parent.width-(siteState.width+130)
                    }
                }
               
                Text{
                    id:nameText
                    text:siteName
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 12
                    horizontalAlignment:Text.AlignLeft
                    elide:Text.ElideMiddle
                    width:parent.width
                }

                Text{
                    id:descriptionTest
                    text:i18nd("lliurex-easy-sites","Created by:")+" "+createdBy+" - "+i18nd("lliurex-easy-sites","Updated by:")+ " "+updatedBy
                    font.family:"Quattrocento Sans Bold"
                    font.pointSize: 10
                    horizontalAlignment:Text.AlignLeft
                    elide:Text.ElideMiddle
                    width:parent.width
                }

            }

            Image{
                id:siteState
                source:isVisible?"/usr/share/icons/breeze/actions/24/view-visible.svg":"/usr/share/icons/breeze/actions/24/view-hidden.svg"
                sourceSize.width:32
                sourceSize.height:32
                anchors.left:siteDescription.right
                anchors.verticalCenter:parent.verticalCenter
                anchors.leftMargin:30
            }
            
            Button{
                id:manageSiteBtn
                display:AbstractButton.IconOnly
                icon.name:"configure.svg"
                anchors.leftMargin:15
                anchors.left:siteState.right
                anchors.verticalCenter:parent.verticalCenter
                visible:listSiteItem.ListView.isCurrentItem
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-easy-sites","Click to manage this site")
                onClicked:optionsMenu.open();
                onVisibleChanged:{
                    optionsMenu.close()
                }

                Menu{
                    id:optionsMenu
                    y: manageSiteBtn.height
                    x:-(optionsMenu.width-manageSiteBtn.width/2)

                    MenuItem{
                        icon.name:isVisible?"view-hidden.svg":"view-visible.svg"
                        text:isVisible?i18nd("lliurex-easy-sites","Hide site"):i18nd("lliurex-easy-sites","Show site")
                        onClicked:siteStackBridge.changeSiteStatus([siteId,!isVisible])
                    }
                    MenuItem{
                        icon.name:"folder-html.svg"
                        text:i18nd("lliurex-easy-sites","Open site in browser")
                        onClicked:siteStackBridge.viewSiteInBrowser(siteUrl)
                    }
                    MenuItem{
                        icon.name:"folder-black.svg"
                        text:i18nd("lliurex-easy-sites","Open folder")
                        onClicked:siteStackBridge.openSiteFolder(siteFolder)
                    }
                    MenuItem{
                        icon.name:"folder-sync.svg"
                        text:i18nd("lliurex-easy-sites","Sync new content")
                        onClicked:siteFolderDialog.open()
                    }
                    MenuItem{
                        icon.name:"document-edit.svg"
                        text:i18nd("lliurex-easy-sites","Edit site")
                        onClicked:siteStackBridge.loadSite(siteId)
                    }
                    MenuItem{
                        icon.name:"delete.svg"
                        text:i18nd("lliurex-easy-sites","Delete the site")
                        onClicked:sitesOptionsStackBridge.removeSite([false,siteId])
                    }
                }
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
            siteStackBridge.syncSiteContent([siteId,selectedFolder])
        }
      
    }   
}
